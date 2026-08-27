import os
import subprocess
import shutil
from pathlib import Path
from typing import Tuple, Optional
from src.config import Config

class VideoProcessor:
    def __init__(self):
        self.ffmpeg_path = shutil.which("ffmpeg") or "ffmpeg"
        self.gpu_encoder = self._detect_gpu_encoder()

    def _detect_gpu_encoder(self) -> str:
        """Detects available hardware encoder."""
        try:
            res = subprocess.run([self.ffmpeg_path, "-encoders"], capture_output=True, text=True)
            output = res.stdout
            if "h264_nvenc" in output:
                return "h264_nvenc"
            if "h264_qsv" in output:
                return "h264_qsv"
            if "h264_amf" in output:
                return "h264_amf"
        except Exception:
            pass
        return "libx264"

    def process_clip(
        self,
        input_path: Path,
        output_path: Path,
        duration: float = 3.0,
        aspect_ratio: str = "16:9",
        quality: str = "1080p",
        is_image: bool = False
    ) -> Path:
        """
        Trims and formats media to exact retention duration (3.0s) and resolution.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        res_info = Config.RESOLUTIONS.get(aspect_ratio, Config.RESOLUTIONS["16:9"])
        width, height = res_info.get(quality, (1920, 1080))

        if is_image or input_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
            return self._create_kenburns_clip(input_path, output_path, duration, width, height)
        else:
            return self._trim_and_scale_video(input_path, output_path, duration, width, height)

    def _trim_and_scale_video(
        self,
        input_path: Path,
        output_path: Path,
        duration: float,
        width: int,
        height: int
    ) -> Path:
        """
        Scales, crops to target aspect ratio, and cuts exact seconds.
        """
        # Crop and pad filter to preserve aspect ratio without distortion
        vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,fps=30"

        cmd = [
            self.ffmpeg_path, "-y",
            "-ss", "00:00:00",
            "-i", str(input_path),
            "-t", str(duration),
            "-vf", vf,
            "-c:v", self.gpu_encoder if self.gpu_encoder != "libx264" else "libx264",
            "-pix_fmt", "yuv420p",
            "-an",  # Strip source audio to avoid mixing issues
            "-movflags", "+faststart",
            str(output_path)
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            # Fallback to CPU libx264 if GPU encoder failed
            if self.gpu_encoder != "libx264":
                cmd[cmd.index("-c:v") + 1] = "libx264"
                subprocess.run(cmd, capture_output=True, text=True, check=True)
            else:
                raise RuntimeError(f"FFmpeg video processing failed: {e.stderr}")

        return output_path

    def _create_kenburns_clip(
        self,
        image_path: Path,
        output_path: Path,
        duration: float,
        width: int,
        height: int
    ) -> Path:
        """
        Applies smooth 3.0s Ken Burns Pan & Zoom to static stock images.
        """
        frames = int(duration * 30)
        vf = (
            f"scale=8000:-1,"
            f"zoompan=z='min(zoom+0.0015,1.5)':d={frames}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30,"
            f"setsar=1"
        )

        cmd = [
            self.ffmpeg_path, "-y",
            "-loop", "1",
            "-i", str(image_path),
            "-t", str(duration),
            "-vf", vf,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-an",
            "-movflags", "+faststart",
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_path
