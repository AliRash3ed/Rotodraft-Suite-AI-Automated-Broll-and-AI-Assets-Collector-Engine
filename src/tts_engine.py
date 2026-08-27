import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import edge_tts
from src.config import Config

class TTSEngine:
    def __init__(self):
        pass

    async def generate_speech(
        self,
        text: str,
        output_path: Path,
        voice: str = "en-US-ChristopherNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> Dict[str, Any]:
        """
        Generates neural speech and .srt subtitles using edge-tts.
        Returns: { 'audio_path': ..., 'srt_path': ..., 'duration': float }
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        srt_path = output_path.with_suffix(".srt")

        clean_text = text.strip()
        if not clean_text:
            raise ValueError("TTS text cannot be empty")

        communicate = edge_tts.Communicate(
            text=clean_text,
            voice=voice,
            rate=rate,
            pitch=pitch
        )

        sub_maker = edge_tts.SubMaker()
        with open(output_path, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    sub_maker.feed(chunk)

        # Write SRT file
        with open(srt_path, "w", encoding="utf-8") as srt_file:
            srt_file.write(sub_maker.get_srt())

        # Get exact duration via ffprobe
        duration = self.get_audio_duration(output_path)

        return {
            "audio_path": str(output_path),
            "srt_path": str(srt_path),
            "duration": duration,
            "voice": voice
        }

    def get_audio_duration(self, audio_path: Path) -> float:
        """Uses ffprobe to obtain exact audio duration in seconds."""
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            str(audio_path)
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            return float(data["format"]["duration"])
        except Exception as e:
            print(f"[WARN] ffprobe duration check failed: {e}. Estimating from file size...")
            # Fallback approximate estimation (~16KB per sec for 128kbps mp3)
            size = os.path.getsize(audio_path)
            return max(1.0, size / 16000.0)
