import os
import sqlite3
import json
import httpx
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.config import Config

DATA_DIR = Config.ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "leads.db"

# Optional Cloud Webhook URL for private remote backup (Stored in local .env only)
OWNER_WEBHOOK_URL = os.getenv("OWNER_WEBHOOK_URL", "")

class LeadManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    whatsapp_clicked INTEGER DEFAULT 0,
                    video_count INTEGER DEFAULT 1,
                    source TEXT DEFAULT 'web_studio',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS video_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT,
                    mode TEXT,
                    aspect_ratio TEXT,
                    mood TEXT,
                    voice TEXT,
                    duration REAL,
                    clip_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    async def save_lead(self, email: str, name: Optional[str] = "", video_count: int = 1) -> Dict[str, Any]:
        """Saves lead to local private SQLite database and optionally triggers private webhook."""
        email = email.strip().lower()
        if not email or "@" not in email:
            raise ValueError("Invalid email format")

        name = (name or "").strip()
        is_new = True

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO leads (email, name, video_count) VALUES (?, ?, ?)",
                    (email, name, video_count)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # Already exists, update count
                is_new = False
                cursor.execute(
                    "UPDATE leads SET video_count = video_count + 1 WHERE email = ?",
                    (email,)
                )
                conn.commit()

        # Optional cloud webhook sync (owner only)
        if OWNER_WEBHOOK_URL:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        OWNER_WEBHOOK_URL,
                        json={
                            "email": email,
                            "name": name,
                            "is_new": is_new,
                            "timestamp": datetime.now().isoformat(),
                            "app": "RotoDraft Suite"
                        }
                    )
            except Exception as e:
                print(f"[WARN] Owner webhook failed: {e}")

        return {"success": True, "email": email, "is_new": is_new}

    def record_whatsapp_click(self, email: str):
        """Marks that user clicked the WhatsApp deep-link."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE leads SET whatsapp_clicked = 1 WHERE email = ?",
                (email.strip().lower(),)
            )
            conn.commit()

    def record_video_generation(
        self,
        project_name: str,
        mode: str,
        aspect_ratio: str,
        mood: str,
        voice: str,
        duration: float,
        clip_count: int
    ):
        """Records telemetry event for owner analytics."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO video_events (project_name, mode, aspect_ratio, mood, voice, duration, clip_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (project_name, mode, aspect_ratio, mood, voice, duration, clip_count)
            )
            conn.commit()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Calculates conversion metrics and statistics for the Owner Dashboard."""
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Leads count
            cursor.execute("SELECT COUNT(*) FROM leads")
            total_leads = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM leads WHERE whatsapp_clicked = 1")
            whatsapp_conversions = cursor.fetchone()[0]

            # Videos generated
            cursor.execute("SELECT COUNT(*) FROM video_events")
            total_videos = cursor.fetchone()[0]

            # Aspect ratios
            cursor.execute("SELECT aspect_ratio, COUNT(*) as count FROM video_events GROUP BY aspect_ratio ORDER BY count DESC LIMIT 5")
            aspect_ratios = [dict(r) for r in cursor.fetchall()]

            # Top Voices
            cursor.execute("SELECT voice, COUNT(*) as count FROM video_events GROUP BY voice ORDER BY count DESC LIMIT 5")
            top_voices = [dict(r) for r in cursor.fetchall()]

            # Top Moods
            cursor.execute("SELECT mood, COUNT(*) as count FROM video_events GROUP BY mood ORDER BY count DESC LIMIT 5")
            top_moods = [dict(r) for r in cursor.fetchall()]

            # Recent leads list
            cursor.execute("SELECT email, name, whatsapp_clicked, video_count, created_at FROM leads ORDER BY id DESC LIMIT 50")
            recent_leads = [dict(r) for r in cursor.fetchall()]

        conversion_rate = round((whatsapp_conversions / max(1, total_leads)) * 100, 1)

        return {
            "total_leads": total_leads,
            "whatsapp_conversions": whatsapp_conversions,
            "conversion_rate_pct": conversion_rate,
            "total_videos": total_videos,
            "aspect_ratios": aspect_ratios,
            "top_voices": top_voices,
            "top_moods": top_moods,
            "recent_leads": recent_leads
        }

    def export_leads_csv(self) -> str:
        """Exports all captured leads to a CSV formatted string."""
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, name, whatsapp_clicked, video_count, created_at FROM leads ORDER BY id DESC")
            rows = cursor.fetchall()

        csv_lines = ["ID,Email,Name,WhatsApp Clicked,Video Count,Created At"]
        for r in rows:
            csv_lines.append(f"{r['id']},{r['email']},{r['name'] or ''},{r['whatsapp_clicked']},{r['video_count']},{r['created_at']}")
        return "\n".join(csv_lines)
