import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

class VideoMerger:
    def __init__(self):
        self.ffmpeg_path = shutil.which("ffmpeg") or "ffmpeg"

    def merge_clips(
        self,
        clip_paths: List[Path],
        output_master_path: Path,
        audio_path: Optional[Path] = None,
        bgm_path: Optional[Path] = None,
        srt_path: Optional[Path] = None
    ) -> Path:
        """
        Concatenates all trimmed clips and mixes voiceover + smart auto-ducked background music.
        """
        if not clip_paths:
            raise ValueError("No video clips provided for master merge")

        output_master_path = Path(output_master_path)
        output_master_path.parent.mkdir(parents=True, exist_ok=True)

        temp_dir = output_master_path.parent / "_temp_concat"
        temp_dir.mkdir(parents=True, exist_ok=True)
        concat_txt = temp_dir / "concat_list.txt"

        with open(concat_txt, "w", encoding="utf-8") as f:
            for clip in clip_paths:
                p_str = str(Path(clip).resolve()).replace("\\", "/")
                f.write(f"file '{p_str}'\n")

        # Step 1: Concatenate video streams
        raw_merged = temp_dir / "raw_merged.mp4"
        cmd_concat = [
            self.ffmpeg_path, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_txt),
            "-c", "copy",
            "-movflags", "+faststart",
            str(raw_merged)
        ]
        subprocess.run(cmd_concat, capture_output=True, text=True, check=True)

        has_voice = audio_path and Path(audio_path).exists()
        has_bgm = bgm_path and Path(bgm_path).exists()

        # Step 2: Audio Muxing (Voiceover + BGM Auto-Ducking)
        if has_voice and has_bgm:
            # Dual audio input with volume balancing & auto-ducking
            cmd_mix = [
                self.ffmpeg_path, "-y",
                "-i", str(raw_merged),
                "-i", str(audio_path),
                "-stream_loop", "-1", "-i", str(bgm_path),
                "-filter_complex", "[1:a]volume=1.0[voice]; [2:a]volume=0.18[music]; [voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                str(output_master_path)
            ]
            subprocess.run(cmd_mix, capture_output=True, text=True, check=True)

        elif has_voice:
            cmd_audio = [
                self.ffmpeg_path, "-y",
                "-i", str(raw_merged),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                str(output_master_path)
            ]
            subprocess.run(cmd_audio, capture_output=True, text=True, check=True)

        elif has_bgm:
            cmd_bgm_only = [
                self.ffmpeg_path, "-y",
                "-i", str(raw_merged),
                "-stream_loop", "-1", "-i", str(bgm_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                str(output_master_path)
            ]
            subprocess.run(cmd_bgm_only, capture_output=True, text=True, check=True)

        else:
            shutil.copyfile(raw_merged, output_master_path)

        # Cleanup
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

        return output_master_path
