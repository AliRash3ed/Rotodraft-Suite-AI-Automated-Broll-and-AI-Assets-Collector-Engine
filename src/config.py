import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # Base Directories
    ROOT_DIR: Path = BASE_DIR
    DOWNLOADS_DIR: Path = BASE_DIR / "downloads"
    ASSETS_DIR: Path = BASE_DIR / "static" / "assets"
    
    # AI API Keys
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openrouter/free")
    
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "command-r-08-2024")
    
    # Stock Media API Keys
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
    PIXABAY_API_KEY: str = os.getenv("PIXABAY_API_KEY", "")

    # Supported Free OpenRouter Models for quick toggle
    FREE_AI_MODELS = [
        {"id": "openrouter/free", "name": "OpenRouter Auto-Free (Recommended)"},
        {"id": "liquid/lfm-2.5-2.6b:free", "name": "Liquid LFM 2.5 (Fast Free)"},
        {"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Llama 3.3 70B (High Quality Free)"},
        {"id": "deepseek/deepseek-chat", "name": "DeepSeek V3 (BYOK)"},
        {"id": "google/gemini-2.0-flash-001", "name": "Gemini 2.0 Flash (BYOK)"}
    ]

    # Aspect Ratio Resolutions
    RESOLUTIONS = {
        "16:9": {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "4K": (3840, 2160),
            "orientation": "landscape"
        },
        "9:16": {
            "720p": (720, 1280),
            "1080p": (1080, 1920),
            "4K": (2160, 3840),
            "orientation": "portrait"
        },
        "1:1": {
            "720p": (720, 720),
            "1080p": (1080, 1080),
            "4K": (2160, 2160),
            "orientation": "square"
        }
    }

    # Edge-TTS Neural Voices List
    TTS_VOICES = [
        {"id": "en-US-ChristopherNeural", "name": "Christopher (US Male - Narrative / Deep)", "lang": "en-US"},
        {"id": "en-US-GuyNeural", "name": "Guy (US Male - Casual / Energetic)", "lang": "en-US"},
        {"id": "en-US-AriaNeural", "name": "Aria (US Female - Professional)", "lang": "en-US"},
        {"id": "en-US-JennyNeural", "name": "Jenny (US Female - Natural / Friendly)", "lang": "en-US"},
        {"id": "en-GB-RyanNeural", "name": "Ryan (UK Male - Cinematic / British)", "lang": "en-GB"},
        {"id": "en-GB-SoniaNeural", "name": "Sonia (UK Female - Documentary)", "lang": "en-GB"},
        {"id": "ur-PK-AsadNeural", "name": "Asad (Urdu Male - Professional)", "lang": "ur-PK"},
        {"id": "ur-PK-UzmaNeural", "name": "Uzma (Urdu Female - Clear)", "lang": "ur-PK"},
        {"id": "hi-IN-MadhurNeural", "name": "Madhur (Hindi Male - Storyteller)", "lang": "hi-IN"},
        {"id": "hi-IN-SwaraNeural", "name": "Swara (Hindi Female - Smooth)", "lang": "hi-IN"}
    ]

    # Server Defaults
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

# Ensure downloads directory exists
Config.DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
Config.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
