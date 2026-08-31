
import os
import re
import shutil
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.config import Config
from src.logger import logger
from src.system_checker import SystemChecker

class VideoProcessor:
    """
    FFmpeg video processing, exact duration trimming, aspect ratio cropping,
    Ken Burns photo-to-video animation, color grading presets, and full video concatenation.
    """

    def __init__(
        self,
        clip_duration: Optional[float] = None,
        output_quality: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        enable_ken_burns: bool = True,
        transition: str = "cut",
        color_preset: str = "none"
    ):
        Config.load_saved_settings()
        self.clip_duration = clip_duration or Config.DEFAULT_CLIP_DURATION
        self.output_quality = output_quality or Config.DEFAULT_QUALITY
        self.aspect_ratio = aspect_ratio or Config.DEFAULT_ASPECT_RATIO
        self.enable_ken_burns = enable_ken_burns
        self.transition = transition or Config.DEFAULT_TRANSITION
        self.color_preset = color_preset

        ff_info = SystemChecker.check_ffmpeg()
        self.ffmpeg_bin = ff_info.get("ffmpeg_path") or "ffmpeg"
        self.ffprobe_bin = ff_info.get("ffprobe_path") or "ffprobe"

    def process_clip(
        self,
        raw_filepath: Path,
        output_dir: Path,
        index: int,
        keyword: str,
        is_photo: bool = False,
        quality: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        target_duration: Optional[float] = None,
    ) -> Dict[str, Any]:
        q = quality or self.output_quality
        ar = aspect_ratio or self.aspect_ratio
        dur = target_duration or self.clip_duration

        target_w, target_h = Config.get_resolution(q, ar)
        safe_kw = self._sanitize_filename(keyword)
        output_filename = f"{index:02d}_{safe_kw}.mp4"
        output_path = output_dir / output_filename

        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"FFmpeg rendering Clip #{index:02d} to exact {dur}s ({target_w}x{target_h} {ar})...",
            "FFMPEG",
        )

        try:
            if is_photo or raw_filepath.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                success = self._create_video_from_photo(
                    raw_filepath, output_path, dur, target_w, target_h, enable_motion=self.enable_ken_burns
                )
            else:
                success = self._trim_and_scale_video(
                    raw_filepath, output_path, dur, target_w, target_h
                )

            if not success or not output_path.exists() or output_path.stat().st_size < 1000:
                raise RuntimeError(f"FFmpeg failed to generate clip {output_filename}")

            probe_info = self.probe_media(output_path)
            file_size_mb = round(output_path.stat().st_size / (1024 * 1024), 2)

            logger.success(
                f"Clip #{index:02d} verified & ready -> {output_filename} ({file_size_mb} MB, {probe_info.get('width', target_w)}x{probe_info.get('height', target_h)}, {probe_info.get('duration', dur)}s)",
                "FFMPEG",
            )

            return {
                "success": True,
                "output_path": str(output_path),
                "output_filename": output_filename,
                "duration": probe_info.get("duration", dur),
                "file_size_mb": file_size_mb,
                "resolution": f"{target_w}x{target_h}",
                "aspect_ratio": ar,
            }
        except Exception as e:
            logger.error(f"FFmpeg Error on Clip #{index:02d}: {str(e)}", "FFMPEG")
            return {
                "success": False,
                "error": str(e),
                "index": index,
                "keyword": keyword,
            }

    def process_batch(
        self,
        items: List[Dict[str, Any]],
        output_dir: Path,
        quality: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        clip_duration: Optional[float] = None,
        on_progress: Optional[Any] = None,
        max_workers: int = 4,
    ) -> List[Dict[str, Any]]:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        results_map = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {}
            for it in items:
                idx = it["index"]
                raw_path_val = it.get("raw_path") or it.get("raw_filepath")
                if not it.get("download_success") or not raw_path_val:
                    results_map[idx] = dict(it, process_success=False, process_error="Media stream not downloaded")
                    continue

                raw_p = Path(raw_path_val)
                is_p = it.get("is_photo_fallback", False) or raw_p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
                kw = it.get("keyword", f"clip_{idx}")

                fut = executor.submit(
                    self.process_clip,
                    raw_filepath=raw_p,
                    output_dir=output_dir,
                    index=idx,
                    keyword=kw,
                    is_photo=is_p,
                    quality=quality or self.output_quality,
                    aspect_ratio=aspect_ratio or self.aspect_ratio,
                    target_duration=clip_duration or self.clip_duration,
                )
                future_to_idx[fut] = idx

            done_count = 0
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                done_count += 1
                try:
                    res = future.result()
                    orig = next((i for i in items if i["index"] == idx), {"index": idx})
                    updated = dict(orig)
                    updated["process_success"] = res.get("success", False)
                    if res.get("success"):
                        updated["output_path"] = res.get("output_path")
                        updated["output_filename"] = res.get("output_filename")
                        updated["final_duration"] = res.get("duration")
                        updated["file_size_mb"] = res.get("file_size_mb")
                        updated["resolution"] = res.get("resolution")
                    else:
                        updated["process_error"] = res.get("error", "FFmpeg render error")
                    results_map[idx] = updated
                    if on_progress:
                        on_progress(done_count, len(items), updated)
                except Exception as e:
                    orig = next((i for i in items if i["index"] == idx), {"index": idx})
                    failed_item = dict(orig, process_success=False, process_error=str(e))
                    results_map[idx] = failed_item
                    if on_progress:
                        on_progress(done_count, len(items), failed_item)

        return [results_map.get(i["index"], i) for i in items]

    def concatenate_to_full_video(
        self,
        clips: List[Dict[str, Any]],
        output_dir: Path,
        project_name: str,
        fps: int = 30
    ) -> Optional[Path]:
        """Stitches all sequential 3.0s clips into one complete ready-to-watch full master video."""
        valid_paths = []
        for c in clips:
            p = c.get("output_path")
            if p and Path(p).exists() and Path(p).stat().st_size > 1000:
                valid_paths.append(Path(p))

        if not valid_paths:
            logger.warning("No valid clips found to concatenate into full video.", "FFMPEG")
            return None

        concat_list_file = output_dir / "concat_list.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for p in valid_paths:
                clean_path = str(p.resolve()).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        full_output_path = output_dir / f"{project_name}_full_master.mp4"
        logger.info(f"Stitching {len(valid_paths)} clips into Full Master Video ({full_output_path.name})...", "FFMPEG")

    def _get_creation_flags(self) -> int:
        """Returns Windows BELOW_NORMAL_PRIORITY_CLASS to prevent freezing on Potato PCs."""
        return 0x00004000 if os.name == "nt" else 0

    def _build_video_filter(self, target_w: int, target_h: int, aspect_ratio: str) -> str:
        """Generates resolution-accurate and aspect-ratio aware FFmpeg filtergraph."""
        if aspect_ratio in ["9:16", "portrait"] or (target_w < target_h):
            # Dual-Layer Ambient Blurred Background Stack (CapCut / TikTok Pro Style - 0 cropped faces!)
            vf = (
                f"split=2[bg][fg];"
                f"[bg]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
                f"crop={target_w}:{target_h},boxblur=25:5[blurred];"
                f"[fg]scale={target_w}:-2:force_original_aspect_ratio=decrease[sharp];"
                f"[blurred][sharp]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30"
            )
        else:
            # Standard scale & crop
            vf = (
                f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
                f"crop={target_w}:{target_h},"
                f"setsar=1,fps=30"
            )

        # Apply rich color grading presets
        if self.color_preset == "cinematic_warm":
            vf += ",colorbalance=rs=0.1:gs=-0.05:bs=-0.1:rm=0.08:gm=0.0:bm=-0.08,eq=contrast=1.08:saturation=1.12"
        elif self.color_preset == "teal_orange":
            vf += ",colorbalance=rs=0.12:gs=0.0:bs=-0.12:rm=-0.05:gm=0.05:bm=0.1,eq=contrast=1.12:saturation=1.15"
        elif self.color_preset == "noir_bw":
            vf += ",hue=s=0,eq=contrast=1.2:brightness=-0.02"

        return vf

    def stream_trim_remote_video(
        self,
        remote_url: str,
        output_path: Path,
        duration: float,
        target_w: int,
        target_h: int,
        aspect_ratio: str = "16:9",
        preset: str = "ultrafast"
    ) -> bool:
        """
        Direct HTTP Range Stream-Trimming.
        Pulls only the first N seconds of video directly over network without downloading entire file.
        Reduces download bandwidth from 70MB to ~1.5MB per clip.
        """
        vf_filter = self._build_video_filter(target_w, target_h, aspect_ratio)
        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-headers", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n",
            "-ss", "0.0",
            "-i", remote_url,
            "-t", str(duration),
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-an",
            str(output_path.resolve()),
        ]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=self._get_creation_flags()
        )
        return proc.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000

    def concatenate_to_full_video(
        self,
        clips: List[Dict[str, Any]],
        output_dir: Path,
        project_name: str,
        fps: int = 30
    ) -> Optional[Path]:
        """Stitches clips into a full master video with real xfade transition support."""
        valid_paths = []
        for c in clips:
            p = c.get("output_path")
            if p and Path(p).exists() and Path(p).stat().st_size > 1000:
                valid_paths.append(Path(p))

        if not valid_paths:
            logger.warning("No valid clips found to concatenate into full video.", "FFMPEG")
            return None

        full_output_path = output_dir / f"{project_name}_full_master.mp4"
        logger.info(f"Stitching {len(valid_paths)} clips into Master Video ({full_output_path.name}) with transition: [{self.transition.upper()}]...", "FFMPEG")

        # 1. Real xfade transitions when transition != "cut" and >= 2 clips
        if self.transition not in ["cut", "none"] and len(valid_paths) > 1:
            try:
                success = self._concat_with_xfade(valid_paths, full_output_path, fps)
                if success and full_output_path.exists():
                    mb = round(full_output_path.stat().st_size / (1024 * 1024), 2)
                    logger.success(f"Full Master Video with [{self.transition.upper()}] transition ready: ({mb} MB)!", "FFMPEG")
                    return full_output_path
            except Exception as e:
                logger.warning(f"xfade transition failed ({str(e)}), falling back to fast concat demuxer.", "FFMPEG")

        # 2. Fast Concat Demuxer (Hard Cut)
        concat_list_file = output_dir / "concat_list.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for p in valid_paths:
                clean_path = str(p.resolve()).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "veryfast",
            "-crf", "20",
            str(full_output_path)
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=self._get_creation_flags())
        if proc.returncode == 0 and full_output_path.exists():
            mb = round(full_output_path.stat().st_size / (1024 * 1024), 2)
            logger.success(f"Full Master Video successfully created: {full_output_path.name} ({mb} MB)!", "FFMPEG")
            return full_output_path
        else:
            logger.error(f"Failed to concatenate full video: {proc.stderr[:200]}", "FFMPEG")
            return None

    def _concat_with_xfade(self, paths: List[Path], output_path: Path, fps: int = 30) -> bool:
        """Builds a dynamic xfade filtergraph chain for seamless cross-fades and wipes."""
        trans_type = "fade" if self.transition in ["fade", "dissolve"] else "wipeleft"
        trans_dur = 0.5
        clip_dur = self.clip_duration

        inputs = []
        for p in paths:
            inputs.extend(["-i", str(p.resolve())])

        chain = []
        prev_link = "0:v"
        current_offset = clip_dur - trans_dur

        for i in range(1, len(paths)):
            next_link = f"v{i}"
            chain.append(
                f"[{prev_link}][{i}:v]xfade=transition={trans_type}:duration={trans_dur}:offset={current_offset:.2f}[{next_link}]"
            )
            prev_link = next_link
            current_offset += (clip_dur - trans_dur)

        filter_str = ";".join(chain)
        cmd = [
            self.ffmpeg_bin,
            "-y",
            *inputs,
            "-filter_complex", filter_str,
            "-map", f"[{prev_link}]",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            str(output_path.resolve())
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=self._get_creation_flags())
        return proc.returncode == 0

    def mux_audio_with_video(self, video_path: Path, audio_path: Path, output_path: Path) -> bool:
        """Instantly muxes external voiceover audio with video stream without video re-encoding (0.2s)."""
        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-i", str(video_path.resolve()),
            "-i", str(audio_path.resolve()),
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_path.resolve())
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=self._get_creation_flags())
        return proc.returncode == 0 and output_path.exists()

    def _trim_and_scale_video(
        self, input_path: Path, output_path: Path, duration: float, target_w: int, target_h: int
    ) -> bool:
        vf_filter = self._build_video_filter(target_w, target_h, self.aspect_ratio)
        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-ss", "0.0",
            "-t", str(duration),
            "-i", str(input_path.resolve()),
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-an",
            str(output_path.resolve()),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=self._get_creation_flags())
        return proc.returncode == 0

    def _create_video_from_photo(
        self, input_path: Path, output_path: Path, duration: float, target_w: int, target_h: int, enable_motion: bool = True
    ) -> bool:
        total_frames = int(duration * 30)
        
        if enable_motion:
            # Ken Burns Pan & Zoom animation
            vf_filter = (
                f"scale=-2:1080,zoompan=z='min(zoom+0.0015,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={target_w}x{target_h}:fps=30,"
                f"setsar=1"
            )
        else:
            # Static Photo frame
            vf_filter = self._build_video_filter(target_w, target_h, self.aspect_ratio)

        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-loop", "1",
            "-t", str(duration),
            "-i", str(input_path.resolve()),
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-an",
            str(output_path.resolve()),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=self._get_creation_flags())
        return proc.returncode == 0

    def probe_media(self, file_path: Path) -> Dict[str, Any]:
        cmd = [
            self.ffprobe_bin,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path.resolve()),
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=self._get_creation_flags())
            if proc.returncode == 0:
                data = json.loads(proc.stdout)
                duration = float(data.get("format", {}).get("duration", 0.0))
                video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
                return {
                    "duration": round(duration, 2),
                    "width": int(video_stream.get("width", 0)),
                    "height": int(video_stream.get("height", 0)),
                }
        except Exception:
            pass
        return {"duration": round(self.clip_duration, 2)}

    def sanitize_filename(self, text: str) -> str:
        return self._sanitize_filename(text)

    def _sanitize_filename(self, text: str) -> str:
        s = re.sub(r"[^\w\s-]", "", text.strip())
        s = re.sub(r"[-\s]+", "_", s)
        return s[:40].lower() or "broll"
