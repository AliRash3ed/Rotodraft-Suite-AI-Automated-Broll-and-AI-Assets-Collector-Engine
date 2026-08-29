import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any

class RealTimeLogger:
    def __init__(self, max_buffer: int = 1500):
        self.max_buffer = max_buffer
        self.buffer: List[Dict[str, Any]] = []
        self.subscribers: List[asyncio.Queue] = []

    def _sanitize(self, message: str) -> str:
        # Strip potential keys from log message
        import re
        message = re.sub(r"sk-[a-zA-Z0-9_\-]{15,}", "sk-****************", message)
        message = re.sub(r"Bearer\s+[a-zA-Z0-9_\-\.]{15,}", "Bearer ****************", message)
        return message

    def log(self, level: str, message: str, category: str = "GENERAL", data: Any = None):
        clean_msg = self._sanitize(str(message))
        event = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level.upper(),
            "category": category.upper(),
            "message": clean_msg,
            "data": data or {}
        }
        
        self.buffer.append(event)
        if len(self.buffer) > self.max_buffer:
            self.buffer.pop(0)

        # Print cleanly to terminal
        print(f"[{event['timestamp']}] [{event['category']}] [{event['level']}] {event['message']}")

        # Push to async SSE subscribers
        for queue in list(self.subscribers):
            try:
                queue.put_nowait(event)
            except Exception:
                pass

    def info(self, msg: str, cat: str = "INFO", data: Any = None):
        self.log("INFO", msg, cat, data)

    def success(self, msg: str, cat: str = "SUCCESS", data: Any = None):
        self.log("SUCCESS", msg, cat, data)

    def warning(self, msg: str, cat: str = "WARNING", data: Any = None):
        self.log("WARNING", msg, cat, data)

    def error(self, msg: str, cat: str = "ERROR", data: Any = None):
        self.log("ERROR", msg, cat, data)

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self.subscribers:
            self.subscribers.remove(q)

    def get_recent(self) -> List[Dict[str, Any]]:
        return list(self.buffer)

    def clear(self):
        self.buffer.clear()

logger = RealTimeLogger()
