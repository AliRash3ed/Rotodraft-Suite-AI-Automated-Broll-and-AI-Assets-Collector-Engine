import sys
import platform
from typing import Dict, Any, Optional
from src.config import Config
from src.logger import logger

class AIErrorDoctor:
    """
    Self-Healing AI Error Diagnostician.
    Analyzes any error, identifies root cause, and provides step-by-step solutions with auto-repair actions.
    """

    @classmethod
    def diagnose(cls, error_msg: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        err_lower = str(error_msg).lower()
        system_info = f"{platform.system()} {platform.release()} (Python {sys.version.split()[0]})"
        
        # 1. Known Pattern Rule Engine (Instant & 100% Deterministic)
        if "ffmpeg" in err_lower or "ffprobe" in err_lower or "codec" in err_lower:
            return {
                "category": "FFmpeg Engine",
                "title": "FFmpeg Video Binary Not Found or Inaccessible",
                "explanation": "The video processing engine requires FFmpeg to trim, scale, and render 3.0s clips. FFmpeg was not detected in your system PATH.",
                "solution_steps": [
                    "Windows: Run 'winget install Gyan.FFmpeg' in PowerShell or download from gyan.dev/ffmpeg/builds/",
                    "macOS: Run 'brew install ffmpeg' in terminal.",
                    "Linux (Ubuntu/Debian): Run 'sudo apt update && sudo apt install ffmpeg'.",
                    "Restart the tool after installation."
                ],
                "auto_fixable": False,
                "suggested_action": "INSTALL_FFMPEG"
            }

        if "429" in err_lower or "rate limit" in err_lower or "quota" in err_lower:
            return {
                "category": "API Quota / Rate Limit",
                "title": "Provider Rate Limit Reached (HTTP 429)",
                "explanation": "The active AI or Stock Media provider has reached its hourly/monthly request limit.",
                "solution_steps": [
                    "Enable 'Smart Query Fallback' in settings to auto-switch to alternative providers (Pixabay, Groq, OpenRouter).",
                    "Switch AI Brain to Google Gemini (15 RPM Free Tier) or Groq Llama 3.3 (High Speed Free).",
                    "Or add a secondary API Key in Settings to allow key rotation."
                ],
                "auto_fixable": True,
                "suggested_action": "SWITCH_PROVIDER"
            }

        if "401" in err_lower or "unauthorized" in err_lower or "invalid api key" in err_lower:
            return {
                "category": "Authentication",
                "title": "Invalid or Expired API Key",
                "explanation": "The API server rejected your request because the configured API Key is missing or invalid.",
                "solution_steps": [
                    "Open 'Settings & APIs' modal in the dashboard.",
                    "Click the '🔑 Get Free Key' link next to the provider to generate a fresh key.",
                    "Paste the key and click 'Test Provider' to verify connection."
                ],
                "auto_fixable": False,
                "suggested_action": "OPEN_SETTINGS"
            }

        if "timeout" in err_lower or "connection" in err_lower or "nodename" in err_lower:
            return {
                "category": "Network & Proxy",
                "title": "Network Connection Timeout",
                "explanation": "Your system could not reach the stock media servers or AI API endpoint.",
                "solution_steps": [
                    "Check your internet connection.",
                    "If certain AI models are geo-blocked in your region, enter your proxy address in 'Settings -> Performance & Proxy' (e.g. http://127.0.0.1:7890).",
                    "Switch to local offline Ollama (llama3.2) which works with zero internet connection."
                ],
                "auto_fixable": True,
                "suggested_action": "RETRY_JOB"
            }

        # 2. General AI Diagnosis via AIEngine
        try:
            from src.ai_engine import AIEngine
            ai = AIEngine()
            prompt = f"""You are an elite developer support engineer.
Diagnose this error that occurred in an autonomous video creator tool:
ERROR: {error_msg}
SYSTEM: {system_info}
CONTEXT: {context or {}}

Provide a JSON object with:
{{
  "category": "General Error",
  "title": "Short descriptive title",
  "explanation": "1-2 sentences explaining why this happened",
  "solution_steps": ["step 1", "step 2"],
  "auto_fixable": false,
  "suggested_action": "RETRY_JOB"
}}"""
            raw = ai._dispatch_call("openrouter", prompt)
            import re
            cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned).strip()
            return json.loads(cleaned)
        except Exception:
            return {
                "category": "Pipeline Error",
                "title": "Unexpected Processing Exception",
                "explanation": f"The pipeline encountered an issue: {error_msg[:120]}",
                "solution_steps": [
                    "Review the Live Event Stream for specific clip numbers that failed.",
                    "Try reducing the number of parallel downloads in Settings.",
                    "Click 'Start B-Roll Collection' again to retry with auto-repair."
                ],
                "auto_fixable": True,
                "suggested_action": "RETRY_JOB"
            }
