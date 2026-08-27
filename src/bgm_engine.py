import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.config import Config

BGM_TRACKS = [
    {"id": "none", "name": "None (Voiceover Only)", "file": None},
    {"id": "lofi", "name": "🌿 Lo-Fi Chill (Storytelling & Relaxing)", "url": "https://assets.mixkit.co/music/preview/mixkit-chill-bro-494.mp3"},
    {"id": "cyberpunk", "name": "⚡ Cyberpunk Pulse (High Energy & Tech)", "url": "https://assets.mixkit.co/music/preview/mixkit-tech-house-vibes-130.mp3"},
    {"id": "cinematic", "name": "🎬 Cinematic Documentary (Dramatic & Epic)", "url": "https://assets.mixkit.co/music/preview/mixkit-cinematic-mystery-suspense-hum-2852.mp3"},
    {"id": "stoic", "name": "🧘 Stoic Ambient (Deep Reflection & Quotes)", "url": "https://assets.mixkit.co/music/preview/mixkit-ambient-piano-tone-493.mp3"},
    {"id": "corporate", "name": "💼 Corporate Inspiring (Clean & Upbeat)", "url": "https://assets.mixkit.co/music/preview/mixkit-inspiring-innovation-112.mp3"}
]

class BGMEngine:
    @classmethod
    def get_available_tracks(cls) -> List[Dict[str, Any]]:
        return BGM_TRACKS

    @classmethod
    async def get_track_audio(cls, track_id: str) -> Optional[Path]:
        """Downloads or retrieves the selected royalty-free BGM track."""
        if not track_id or track_id == "none":
            return None

        track = next((t for t in BGM_TRACKS if t["id"] == track_id), None)
        if not track or not track.get("url"):
            return None

        bgm_dir = Config.DOWNLOADS_DIR / "_bgm_cache"
        bgm_dir.mkdir(parents=True, exist_ok=True)
        dest_path = bgm_dir / f"{track_id}.mp3"

        if dest_path.exists() and dest_path.stat().st_size > 1000:
            return dest_path

        import httpx
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(track["url"])
                if resp.status_code == 200:
                    with open(dest_path, "wb") as f:
                        f.write(resp.content)
                    return dest_path
        except Exception as e:
            print(f"[WARN] Failed to download BGM track '{track_id}': {e}")

        return None
