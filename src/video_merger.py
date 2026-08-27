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
        srt_path: Optional[Path] = None
    ) -> Path:
        """
        Concatenates all trimmed clips and overlays voiceover audio.
        """
        if not clip_paths:
            raise ValueError("No video clips provided for master merge")

        output_master_path = Path(output_master_path)
        output_master_path.parent.mkdir(parents=True, exist_ok=True)

        # Create temporary concat list
        temp_dir = output_master_path.parent / "_temp_concat"
        temp_dir.mkdir(parents=True, exist_ok=True)
        concat_txt = temp_dir / "concat_list.txt"

        with open(concat_txt, "w", encoding="utf-8") as f:
            for clip in clip_paths:
                # FFmpeg concat requires forward slashes or escaped backslashes
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

        # Step 2: Overlay audio if provided
        if audio_path and Path(audio_path).exists():
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
        else:
            shutil.copyfile(raw_merged, output_master_path)

        # Clean up temporary concat folder
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

        return output_master_path
