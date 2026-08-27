import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from src.pipeline import RotoDraftPipeline
from src.ai_engine import AIEngine

class BatchEngine:
    _active_batches: Dict[str, Dict[str, Any]] = {}

    @classmethod
    async def start_batch(
        cls,
        topics: List[str],
        aspect_ratio: str = "9:16",
        voice: str = "en-US-ChristopherNeural",
        mood: str = "Cinematic",
        style: str = "viral_hook"
    ) -> str:
        """Starts a background multi-video factory run for a list of topics."""
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        cls._active_batches[batch_id] = {
            "batch_id": batch_id,
            "status": "in_progress",
            "total_items": len(topics),
            "completed_items": 0,
            "items": [
                {"index": i + 1, "topic": t, "status": "queued", "project_id": None}
                for i, t in enumerate(topics)
            ],
            "created_at": datetime.now().isoformat()
        }

        # Run background worker
        asyncio.create_task(cls._process_batch_queue(batch_id, topics, aspect_ratio, voice, mood, style))
        return batch_id

    @classmethod
    async def _process_batch_queue(
        cls,
        batch_id: str,
        topics: List[str],
        aspect_ratio: str,
        voice: str,
        mood: str,
        style: str
    ):
        ai = AIEngine()
        pipeline = RotoDraftPipeline()
        batch_data = cls._active_batches[batch_id]

        for i, topic in enumerate(topics):
            item_entry = batch_data["items"][i]
            item_entry["status"] = "generating_script"

            try:
                # Step 1: AI script generation
                script_res = await ai.rewrite_script(topic, style=style)
                script_text = script_res.get("enhanced_script", topic)
                est_sec = min(30.0, float(script_res.get("estimated_seconds", 24)))

                item_entry["status"] = "rendering_video"
                safe_title = "".join(c for c in topic if c.isalnum() or c == "_")[:20] or f"Batch_{i+1}"

                # Step 2: Execute pipeline
                async for event in pipeline.execute(
                    mode="full",
                    script=script_text,
                    duration_seconds=est_sec,
                    clip_duration=3.0,
                    aspect_ratio=aspect_ratio,
                    voice=voice,
                    mood=mood,
                    project_name=f"Batch_{safe_title}"
                ):
                    if event.get("type") == "done":
                        item_entry["project_id"] = event.get("project_id")
                        item_entry["master_url"] = event.get("master_url")
                        item_entry["status"] = "completed"

                batch_data["completed_items"] += 1
            except Exception as e:
                item_entry["status"] = f"failed: {str(e)}"

        batch_data["status"] = "completed"

    @classmethod
    def get_batch_status(cls, batch_id: str) -> Optional[Dict[str, Any]]:
        return cls._active_batches.get(batch_id)
