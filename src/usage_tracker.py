import json
import time
from pathlib import Path
from typing import Dict, Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATS_FILE = DATA_DIR / "usage_stats.json"

class UsageTracker:
    """Tracks token consumption, stock API requests, and remaining quotas."""
    
    DEFAULT_QUOTAS = {
        "pexels": {"limit_per_hour": 200, "used": 0, "reset_timestamp": 0},
        "pixabay": {"limit_per_hour": 5000, "used": 0, "reset_timestamp": 0},
        "unsplash": {"limit_per_hour": 50, "used": 0, "reset_timestamp": 0},
        "ai_tokens": {"total_input_tokens": 0, "total_output_tokens": 0, "estimated_cost_usd": 0.0}
    }

    @classmethod
    def load_stats(cls) -> Dict[str, Any]:
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return dict(cls.DEFAULT_QUOTAS)

    @classmethod
    def save_stats(cls, stats: Dict[str, Any]):
        try:
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2)
        except Exception:
            pass

    @classmethod
    def record_stock_call(cls, provider: str, count: int = 1):
        stats = cls.load_stats()
        prov = provider.lower()
        now = time.time()

        if prov in stats:
            p_data = stats[prov]
            # Reset quota if 1 hour has passed
            if now > p_data.get("reset_timestamp", 0):
                p_data["used"] = 0
                p_data["reset_timestamp"] = now + 3600

            p_data["used"] += count
            stats[prov] = p_data
            cls.save_stats(stats)

    @classmethod
    def record_ai_tokens(cls, input_tokens: int, output_tokens: int, provider: str = "openrouter"):
        stats = cls.load_stats()
        ai_data = stats.get("ai_tokens", {"total_input_tokens": 0, "total_output_tokens": 0, "estimated_cost_usd": 0.0})
        
        ai_data["total_input_tokens"] += input_tokens
        ai_data["total_output_tokens"] += output_tokens
        
        # Approximate cost calculation ($0.15/1M tokens for free/low-tier models)
        cost = ((input_tokens + output_tokens) / 1_000_000) * 0.15
        ai_data["estimated_cost_usd"] = round(ai_data.get("estimated_cost_usd", 0.0) + cost, 4)
        
        stats["ai_tokens"] = ai_data
        cls.save_stats(stats)

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        stats = cls.load_stats()
        now = time.time()

        result = {}
        for prov in ["pexels", "pixabay", "unsplash"]:
            p = stats.get(prov, {"limit_per_hour": 200, "used": 0, "reset_timestamp": 0})
            rem_time = max(0, int(p.get("reset_timestamp", 0) - now))
            mins = rem_time // 60
            limit = p.get("limit_per_hour", 200)
            used = p.get("used", 0)
            remaining = max(0, limit - used)
            result[prov] = {
                "limit": limit,
                "used": used,
                "remaining": remaining,
                "reset_in_mins": mins if rem_time > 0 else 60
            }

        result["ai"] = stats.get("ai_tokens", {"total_input_tokens": 0, "total_output_tokens": 0, "estimated_cost_usd": 0.0})
        return result
