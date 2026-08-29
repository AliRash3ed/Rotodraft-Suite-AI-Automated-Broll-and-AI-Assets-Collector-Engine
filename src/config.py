import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SETTINGS_FILE = BASE_DIR / "data" / "saved_settings.json"

class Config:
    """
    Comprehensive Configuration Engine with full support for:
    - 11+ AI Brain Providers (OpenRouter, DeepSeek R1, Groq, Gemini, Claude, OpenAI, Cohere, Ollama, Custom OpenAI-Compatible)
    - 8+ Stock Media Platforms (Pexels, Pixabay, Unsplash, Pinterest, Storyblocks, Coverr, Mixkit, Videvo, Wikimedia)
    - Full Video & Audio Suite (TTS Voiceover, Whisper Subtitles, BGM, Transitions, Color LUTs)
    - NLE Auto-Exporters (Premiere Pro XML, DaVinci Resolve EDL, CapCut Draft JSON, CSV)
    """

    # Directories
    BASE_DIR: Path = BASE_DIR
    OUTPUT_DIR: Path = BASE_DIR / "downloads"
    DATA_DIR: Path = BASE_DIR / "data"

    # Server Configuration
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8001"))

    # AI Brain Provider Defaults
    DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "openrouter")
    
    # Pre-configured AI Providers
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openrouter/free")
    
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "command-r-08-2024")
    
    OLLAMA_ENDPOINT: str = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/v1/chat/completions")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Custom OpenAI-Compatible API Builder
    CUSTOM_AI_NAME: str = os.getenv("CUSTOM_AI_NAME", "Custom LLM")
    CUSTOM_AI_ENDPOINT: str = os.getenv("CUSTOM_AI_ENDPOINT", "http://localhost:20128/v1/chat/completions")
    CUSTOM_AI_KEY: str = os.getenv("CUSTOM_AI_KEY", "")
    CUSTOM_AI_MODEL: str = os.getenv("CUSTOM_AI_MODEL", "default")
    CUSTOM_AI_THINKING: bool = os.getenv("CUSTOM_AI_THINKING", "false").lower() == "true"
    CUSTOM_AI_MAX_TOKENS: int = int(os.getenv("CUSTOM_AI_MAX_TOKENS", "4096"))
    CUSTOM_AI_TEMPERATURE: float = float(os.getenv("CUSTOM_AI_TEMPERATURE", "0.2"))

    # Stock Media API Keys & Platform Toggles
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
    PIXABAY_API_KEY: str = os.getenv("PIXABAY_API_KEY", "")
    UNSPLASH_API_KEY: str = os.getenv("UNSPLASH_API_KEY", "")
    PINTEREST_SESSION_COOKIE: str = os.getenv("PINTEREST_SESSION_COOKIE", "")
    
    # Storyblocks Integration
    STORYBLOCKS_API_KEY: str = os.getenv("STORYBLOCKS_API_KEY", "")
    STORYBLOCKS_PROJECT_ID: str = os.getenv("STORYBLOCKS_PROJECT_ID", "")
    STORYBLOCKS_SECRET_KEY: str = os.getenv("STORYBLOCKS_SECRET_KEY", "")
    STORYBLOCKS_ENABLED: bool = os.getenv("STORYBLOCKS_ENABLED", "true").lower() == "true"
    
    # Coverr.co Integration (Free HD/4K Video API)
    COVERR_API_KEY: str = os.getenv("COVERR_API_KEY", "")
    COVERR_ENABLED: bool = os.getenv("COVERR_ENABLED", "true").lower() == "true"
    
    # Mixkit & Videvo & Wikimedia Toggles
    MIXKIT_ENABLED: bool = os.getenv("MIXKIT_ENABLED", "true").lower() == "true"
    VIDEVO_API_KEY: str = os.getenv("VIDEVO_API_KEY", "")
    VIDEVO_ENABLED: bool = os.getenv("VIDEVO_ENABLED", "true").lower() == "true"
    WIKIMEDIA_ENABLED: bool = os.getenv("WIKIMEDIA_ENABLED", "true").lower() == "true"

    # Video & FFmpeg Settings
    DEFAULT_CLIP_DURATION: float = float(os.getenv("DEFAULT_CLIP_DURATION", "3.0"))
    CLIP_DURATION: float = DEFAULT_CLIP_DURATION
    MIN_CLIP_DURATION: float = 1.0
    MAX_CLIP_DURATION: float = 15.0
    DEFAULT_QUALITY: str = os.getenv("DEFAULT_QUALITY", "1080p")
    DEFAULT_ASPECT_RATIO: str = os.getenv("DEFAULT_ASPECT_RATIO", "16:9")
    DEFAULT_TRANSITION: str = os.getenv("DEFAULT_TRANSITION", "cut")  # "cut", "fade", "kenburns"
    COLOR_PRESET: str = os.getenv("COLOR_PRESET", "none")  # "none", "cinematic_warm", "teal_orange", "noir_bw"
    
    # Video Encoding Precision
    VIDEO_FPS: int = int(os.getenv("VIDEO_FPS", "30"))
    VIDEO_BITRATE: str = os.getenv("VIDEO_BITRATE", "8000k")
    VIDEO_CRF: int = int(os.getenv("VIDEO_CRF", "20"))
    VIDEO_CODEC: str = os.getenv("VIDEO_CODEC", "libx264")
    AUDIO_CODEC: str = os.getenv("AUDIO_CODEC", "aac")
    
    # Voiceover & TTS Settings
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "edge-tts")  # "edge-tts", "elevenlabs", "openai", "gtts"
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    EDGE_TTS_VOICE: str = os.getenv("EDGE_TTS_VOICE", "en-US-ChristopherNeural")
    OPENAI_TTS_VOICE: str = os.getenv("OPENAI_TTS_VOICE", "alloy")

    # Subtitle / Caption Settings
    SUBTITLE_ENABLED: bool = os.getenv("SUBTITLE_ENABLED", "false").lower() == "true"
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    SUBTITLE_FONT: str = os.getenv("SUBTITLE_FONT", "Arial-Bold")
    SUBTITLE_FONT_SIZE: int = int(os.getenv("SUBTITLE_FONT_SIZE", "24"))
    SUBTITLE_COLOR: str = os.getenv("SUBTITLE_COLOR", "#ffffff")
    SUBTITLE_STROKE_COLOR: str = os.getenv("SUBTITLE_STROKE_COLOR", "#000000")
    SUBTITLE_STROKE_WIDTH: int = int(os.getenv("SUBTITLE_STROKE_WIDTH", "2"))
    SUBTITLE_POSITION: str = os.getenv("SUBTITLE_POSITION", "bottom")

    # Background Music (BGM) Settings
    BGM_ENABLED: bool = os.getenv("BGM_ENABLED", "false").lower() == "true"
    BGM_VOLUME: float = float(os.getenv("BGM_VOLUME", "0.15"))
    BGM_FILE_OR_DIR: str = os.getenv("BGM_FILE_OR_DIR", "")

    # Export Automation Defaults
    AUTO_EXPORT_PREMIERE_XML: bool = os.getenv("AUTO_EXPORT_PREMIERE_XML", "true").lower() == "true"
    AUTO_EXPORT_DAVINCI_EDL: bool = os.getenv("AUTO_EXPORT_DAVINCI_EDL", "true").lower() == "true"
    AUTO_EXPORT_CAPCUT_DRAFT: bool = os.getenv("AUTO_EXPORT_CAPCUT_DRAFT", "true").lower() == "true"
    AUTO_STITCH_FULL_VIDEO: bool = os.getenv("AUTO_STITCH_FULL_VIDEO", "false").lower() == "true"

    # Network, Concurrency & Retry Settings
    HTTP_PROXY: str = os.getenv("HTTP_PROXY", "")
    HTTPS_PROXY: str = os.getenv("HTTPS_PROXY", "")
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    MAX_SCRAPE_RETRIES: int = int(os.getenv("MAX_SCRAPE_RETRIES", "3"))
    MAX_PARALLEL_DOWNLOADS: int = int(os.getenv("MAX_PARALLEL_DOWNLOADS", "5"))
    MAX_PARALLEL_SEARCHES: int = int(os.getenv("MAX_PARALLEL_SEARCHES", "6"))
    MAX_PARALLEL_FFMPEG: int = int(os.getenv("MAX_PARALLEL_FFMPEG", "4"))

    # Direct Tutorial & API Key Portals
    API_TUTORIALS: Dict[str, Dict[str, str]] = {
        "openrouter": {
            "name": "OpenRouter",
            "url": "https://openrouter.ai/keys",
            "guide": "1. Go to openrouter.ai/keys\n2. Click 'Create Key'\n3. Set model to 'openrouter/free' or 'liquid/lfm-2.5-2.6b:free' for $0 cost."
        },
        "deepseek": {
            "name": "DeepSeek API",
            "url": "https://platform.deepseek.com/api_keys",
            "guide": "1. Go to platform.deepseek.com/api_keys\n2. Sign in & generate API Key\n3. Set model to 'deepseek-chat' or 'deepseek-reasoner' (Thinking Mode supported)."
        },
        "groq": {
            "name": "Groq Cloud",
            "url": "https://console.groq.com/keys",
            "guide": "1. Go to console.groq.com/keys\n2. Sign in with Google or GitHub\n3. Click 'Create API Key' (Ultra-fast 800 tokens/sec Llama 3.3 70B)."
        },
        "gemini": {
            "name": "Google Gemini",
            "url": "https://aistudio.google.com/app/apikey",
            "guide": "1. Go to aistudio.google.com/app/apikey\n2. Click 'Create API Key' in a new project\n3. Enjoy generous free 15 RPM quota on Gemini 1.5 Flash."
        },
        "openai": {
            "name": "OpenAI",
            "url": "https://platform.openai.com/api-keys",
            "guide": "1. Go to platform.openai.com/api-keys\n2. Click 'Create new secret key'\n3. Copy key (Starts with sk-proj-)."
        },
        "anthropic": {
            "name": "Anthropic Claude",
            "url": "https://console.anthropic.com/settings/keys",
            "guide": "1. Go to console.anthropic.com/settings/keys\n2. Click 'Create Key'\n3. Copy key (Starts with sk-ant-)."
        },
        "cohere": {
            "name": "Cohere",
            "url": "https://dashboard.cohere.com/api-keys",
            "guide": "1. Go to dashboard.cohere.com/api-keys\n2. Copy the Default Trial Key for Command-R."
        },
        "ollama": {
            "name": "Ollama (100% Offline Private)",
            "url": "https://ollama.ai",
            "guide": "1. Download from ollama.ai\n2. Open terminal & run 'ollama run llama3.2'\n3. Endpoint: http://localhost:11434/v1/chat/completions (No API key needed)."
        },
        "pexels": {
            "name": "Pexels API",
            "url": "https://www.pexels.com/api/new/",
            "guide": "1. Go to pexels.com/api/new/\n2. Fill quick form -> Click 'Your API Key'\n3. Free 200 requests/hour."
        },
        "pixabay": {
            "name": "Pixabay API",
            "url": "https://pixabay.com/api/docs/",
            "guide": "1. Go to pixabay.com/api/docs/\n2. Sign in\n3. Copy key from the green box (5,000 requests/hour free)."
        },
        "unsplash": {
            "name": "Unsplash Developers",
            "url": "https://unsplash.com/developers",
            "guide": "1. Go to unsplash.com/developers\n2. 'Your Apps' -> New Application\n3. Copy Access Key (50 requests/hour free)."
        },
        "storyblocks": {
            "name": "Storyblocks",
            "url": "https://www.storyblocks.com/api",
            "guide": "1. Sign in to Storyblocks Developer Portal\n2. Create API credentials or use public scraper fallback."
        },
        "coverr": {
            "name": "Coverr.co",
            "url": "https://coverr.co",
            "guide": "1. 100% Free HD/4K stock video library\n2. Direct search & download without mandatory API key."
        },
        "mixkit": {
            "name": "Mixkit (by Envato)",
            "url": "https://mixkit.co",
            "guide": "1. Free stock video clips & audio tracks\n2. Integrated high-speed scraper."
        },
        "videvo": {
            "name": "Videvo.net",
            "url": "https://www.videvo.net",
            "guide": "1. Free stock footage & motion graphics library."
        },
        "wikimedia": {
            "name": "Wikimedia Commons",
            "url": "https://commons.wikimedia.org",
            "guide": "1. Free historical, documentary & archive public domain media."
        }
    }

    @classmethod
    def get_free_port(cls, default_port: int = 8001) -> int:
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", default_port))
                return default_port
        except OSError:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", 0))
                return s.getsockname()[1]

    @classmethod
    def load_saved_settings(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    for k, v in saved.items():
                        if hasattr(cls, k) and v is not None and str(v).strip() != "":
                            setattr(cls, k, v)
            except Exception:
                pass

    @classmethod
    def save_settings(cls, new_settings: Dict[str, Any]):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        current = {}
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    current = json.load(f)
            except Exception:
                current = {}

        current.update(new_settings)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)

        # Update in-memory
        for k, v in new_settings.items():
            if hasattr(cls, k) and v is not None and str(v).strip() != "":
                setattr(cls, k, v)

    @classmethod
    def get_masked_settings(cls) -> Dict[str, Any]:
        cls.load_saved_settings()
        raw_keys = [
            "DEFAULT_AI_PROVIDER", "OPENROUTER_MODEL", "DEEPSEEK_MODEL", "GROQ_MODEL",
            "GEMINI_MODEL", "OPENAI_MODEL", "ANTHROPIC_MODEL", "COHERE_MODEL",
            "OLLAMA_ENDPOINT", "OLLAMA_MODEL", "CUSTOM_AI_NAME", "CUSTOM_AI_ENDPOINT",
            "CUSTOM_AI_MODEL", "CUSTOM_AI_THINKING", "CUSTOM_AI_MAX_TOKENS", "CUSTOM_AI_TEMPERATURE",
            "DEFAULT_CLIP_DURATION", "DEFAULT_QUALITY", "DEFAULT_ASPECT_RATIO", "DEFAULT_TRANSITION",
            "COLOR_PRESET", "VIDEO_FPS", "VIDEO_BITRATE", "VIDEO_CRF",
            "TTS_PROVIDER", "EDGE_TTS_VOICE", "OPENAI_TTS_VOICE",
            "SUBTITLE_ENABLED", "WHISPER_MODEL", "SUBTITLE_FONT", "SUBTITLE_FONT_SIZE", "SUBTITLE_COLOR",
            "BGM_ENABLED", "BGM_VOLUME",
            "AUTO_EXPORT_PREMIERE_XML", "AUTO_EXPORT_DAVINCI_EDL", "AUTO_EXPORT_CAPCUT_DRAFT", "AUTO_STITCH_FULL_VIDEO",
            "HTTP_PROXY", "HTTPS_PROXY",
            "STORYBLOCKS_ENABLED", "COVERR_ENABLED", "MIXKIT_ENABLED", "VIDEVO_ENABLED", "WIKIMEDIA_ENABLED",
            "MAX_PARALLEL_DOWNLOADS", "MAX_PARALLEL_SEARCHES", "MAX_PARALLEL_FFMPEG"
        ]
        secret_keys = [
            "OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY",
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "COHERE_API_KEY", "CUSTOM_AI_KEY",
            "PEXELS_API_KEY", "PIXABAY_API_KEY", "UNSPLASH_API_KEY", "STORYBLOCKS_API_KEY",
            "COVERR_API_KEY", "VIDEVO_API_KEY", "ELEVENLABS_API_KEY"
        ]

        result = {}
        for k in raw_keys:
            result[k] = getattr(cls, k, "")

        for k in secret_keys:
            val = getattr(cls, k, "")
            result[k] = val  # returned directly for local settings editor

        return result

    @classmethod
    def get_resolution(cls, quality: str = "1080p", aspect_ratio: str = "16:9") -> tuple:
        q = quality.upper()
        ar = aspect_ratio

        if ar == "16:9":
            if q == "4K": return (3840, 2160)
            if q == "720P": return (1280, 720)
            return (1920, 1080)
        elif ar == "9:16":
            if q == "4K": return (2160, 3840)
            if q == "720P": return (720, 1280)
            return (1080, 1920)
        elif ar == "1:1":
            if q == "4K": return (2160, 2160)
            if q == "720P": return (720, 720)
            return (1080, 1080)
        elif ar == "4:5":
            if q == "4K": return (1728, 2160)
            if q == "720P": return (576, 720)
            return (1080, 1350)

        return (1920, 1080)

    @classmethod
    def get_orientation_for_api(cls, aspect_ratio: str = "16:9") -> str:
        if aspect_ratio == "9:16": return "portrait"
        if aspect_ratio == "1:1": return "square"
        return "landscape"
