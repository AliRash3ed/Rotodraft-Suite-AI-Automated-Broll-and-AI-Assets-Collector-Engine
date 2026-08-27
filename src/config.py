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
    
    # LLM Providers & BYOK
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openrouter/free")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL_NAME: str = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL_NAME: str = os.getenv("OLLAMA_MODEL_NAME", "llama3")

    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "command-r-08-2024")
    
    # Stock Media API Keys
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
    PIXABAY_API_KEY: str = os.getenv("PIXABAY_API_KEY", "")

    # Supported Free / BYOK AI Models
    FREE_AI_MODELS = [
        {"id": "openrouter/free", "name": "OpenRouter Auto-Free (Recommended)", "provider": "openrouter"},
        {"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Llama 3.3 70B (High Quality Free)", "provider": "openrouter"},
        {"id": "google/gemini-2.0-flash-001", "name": "Google Gemini 2.0 Flash (Free Tier)", "provider": "gemini"},
        {"id": "deepseek/deepseek-chat", "name": "DeepSeek V3 (BYOK)", "provider": "deepseek"},
        {"id": "openai/gpt-4o-mini", "name": "OpenAI GPT-4o Mini (BYOK)", "provider": "openai"},
        {"id": "groq/llama-3.3-70b", "name": "Groq Ultra-Fast (BYOK)", "provider": "groq"},
        {"id": "ollama/local", "name": "Ollama Local LLM (Offline)", "provider": "ollama"}
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

    # Server Defaults
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

# Ensure downloads directory exists
Config.DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
Config.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
