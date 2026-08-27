import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
import edge_tts
from src.config import Config

class TTSEngine:
    def __init__(self):
        pass

    async def generate_speech(
        self,
        text: str,
        output_path: Path,
        provider: str = "edge",
        voice: str = "en-US-ChristopherNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates neural speech and .srt subtitles using Edge-TTS, OpenAI TTS, or ElevenLabs.
        Returns: { 'audio_path': ..., 'srt_path': ..., 'duration': float }
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        srt_path = output_path.with_suffix(".srt")

        clean_text = text.strip()
        if not clean_text:
            raise ValueError("TTS text cannot be empty")

        # 1. OpenAI TTS Provider
        if provider == "openai" and api_key:
            try:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                openai_voice = voice if voice in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"] else "alloy"
                payload = {
                    "model": "tts-1",
                    "input": clean_text,
                    "voice": openai_voice,
                    "speed": 1.0
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post("https://api.openai.com/v1/audio/speech", headers=headers, json=payload)
                    if resp.status_code == 200:
                        with open(output_path, "wb") as f:
                            f.write(resp.content)
                        duration = self.get_audio_duration(output_path)
                        self._create_simple_srt(clean_text, srt_path, duration)
                        return {
                            "audio_path": str(output_path),
                            "srt_path": str(srt_path),
                            "duration": duration,
                            "voice": openai_voice,
                            "provider": "openai"
                        }
            except Exception as e:
                print(f"[WARN] OpenAI TTS failed: {e}. Falling back to Edge-TTS...")

        # 2. ElevenLabs TTS Provider
        if provider == "elevenlabs" and api_key:
            try:
                voice_id = voice if len(voice) > 10 else "21m00Tcm4TlvDq8ikWAM"
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
                payload = {
                    "text": clean_text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
                }
                async with httpx.AsyncClient(timeout=35.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        with open(output_path, "wb") as f:
                            f.write(resp.content)
                        duration = self.get_audio_duration(output_path)
                        self._create_simple_srt(clean_text, srt_path, duration)
                        return {
                            "audio_path": str(output_path),
                            "srt_path": str(srt_path),
                            "duration": duration,
                            "voice": voice_id,
                            "provider": "elevenlabs"
                        }
            except Exception as e:
                print(f"[WARN] ElevenLabs TTS failed: {e}. Falling back to Edge-TTS...")

        # 3. Microsoft Edge-TTS (Default Free Neural Engine)
        edge_voice = voice if "Neural" in voice else "en-US-ChristopherNeural"
        communicate = edge_tts.Communicate(
            text=clean_text,
            voice=edge_voice,
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
            "voice": edge_voice,
            "provider": "edge"
        }

    def _create_simple_srt(self, text: str, srt_path: Path, duration: float):
        """Generates synchronized sentence-level SRT file when word boundaries aren't streamed."""
        sentences = [s.strip() for s in text.replace(".", ".\n").replace("!", "!\n").replace("?", "?\n").split("\n") if s.strip()]
        if not sentences:
            sentences = [text]
        
        per_seg = duration / len(sentences)
        srt_lines = []
        for i, s in enumerate(sentences):
            t_start = i * per_seg
            t_end = (i + 1) * per_seg
            
            s_start = f"{int(t_start//3600):02}:{int((t_start%3600)//60):02}:{int(t_start%60):02},{int((t_start%1)*1000):03}"
            s_end = f"{int(t_end//3600):02}:{int((t_end%3600)//60):02}:{int(t_end%60):02},{int((t_end%1)*1000):03}"
            
            srt_lines.append(f"{i+1}\n{s_start} --> {s_end}\n{s}\n")

        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines))

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
        except Exception:
            size = os.path.getsize(audio_path)
            return max(1.0, size / 16000.0)
