import os
import sys
import shutil
import subprocess
import requests
import socket
from pathlib import Path
from typing import Dict, Any
from src.config import Config

class SystemChecker:
    @staticmethod
    def get_hardware_profile() -> Dict[str, Any]:
        """Auto-detects CPU cores, RAM, and GPU hardware encoding support for optimal execution."""
        cores = os.cpu_count() or 2
        try:
            import psutil
            ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
        except Exception:
            ram_gb = 4.0

        ff_info = SystemChecker.check_ffmpeg()
        ff_bin = ff_info.get("ffmpeg_path") or "ffmpeg"
        encoders_out = ""
        try:
            creationflags = 0x00004000 if os.name == "nt" else 0
            p = subprocess.run([ff_bin, "-hide_banner", "-encoders"], capture_output=True, text=True, creationflags=creationflags)
            encoders_out = p.stdout
        except Exception:
            pass

        # 1. GPU NVIDIA NVENC
        if "h264_nvenc" in encoders_out:
            return {
                "tier": "GPU_NVIDIA",
                "label": "[GPU Turbo] NVIDIA NVENC (RTX/GTX)",
                "vcodec": "h264_nvenc",
                "ffmpeg_preset": "p2",
                "max_ffmpeg_workers": min(cores, 6),
                "max_download_workers": 8,
                "cores": cores,
                "ram_gb": ram_gb,
                "low_memory_mode": False
            }
        
        # 2. Intel QuickSync (iGPU)
        if "h264_qsv" in encoders_out:
            return {
                "tier": "INTEL_QSV",
                "label": "[Intel QSV] QuickSync Hardware Acceleration",
                "vcodec": "h264_qsv",
                "ffmpeg_preset": "veryfast",
                "max_ffmpeg_workers": min(cores, 4),
                "max_download_workers": 6,
                "cores": cores,
                "ram_gb": ram_gb,
                "low_memory_mode": False
            }

        # 3. Potato PC / Low-End Laptop (<4 Cores or <=4GB RAM)
        if cores <= 4 or ram_gb <= 4.0:
            return {
                "tier": "POTATO_CPU",
                "label": "[Eco Mode] Low-RAM CPU (Potato PC Safe)",
                "vcodec": "libx264",
                "ffmpeg_preset": "ultrafast",
                "max_ffmpeg_workers": 1,  # Safe 1-thread to prevent CPU freeze
                "max_download_workers": 2,
                "cores": cores,
                "ram_gb": ram_gb,
                "low_memory_mode": True
            }

        # 4. Standard Multi-Core CPU
        return {
            "tier": "STANDARD_CPU",
            "label": "[Standard] Multi-Core CPU Mode",
            "vcodec": "libx264",
            "ffmpeg_preset": "veryfast",
            "max_ffmpeg_workers": min(cores // 2, 4),
            "max_download_workers": 5,
            "cores": cores,
            "ram_gb": ram_gb,
            "low_memory_mode": False
        }

    @staticmethod
    def check_internet(timeout: int = 4) -> bool:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except OSError:
            try:
                requests.get("https://www.google.com", timeout=timeout)
                return True
            except Exception:
                return False
    @staticmethod
    def check_ffmpeg() -> Dict[str, Any]:
        candidates = [
            "ffmpeg",
            r"C:\Users\aliho\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe",
        ]
        ffmpeg_bin = None
        ffprobe_bin = None

        for c in candidates:
            if shutil.which(c) or (os.path.exists(c) and os.path.isfile(c)):
                ffmpeg_bin = str(c)
                break

        probe_candidates = [
            "ffprobe",
            r"C:\Users\aliho\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffprobe.exe",
        ]
        for c in probe_candidates:
            if shutil.which(c) or (os.path.exists(c) and os.path.isfile(c)):
                ffprobe_bin = str(c)
                break

        return {
            "ffmpeg_available": ffmpeg_bin is not None,
            "ffmpeg_path": ffmpeg_bin,
            "ffprobe_available": ffprobe_bin is not None,
            "ffprobe_path": ffprobe_bin,
        }

    @staticmethod
    def benchmark_speed() -> Dict[str, Any]:
        """Measures connection latency to stock CDN servers."""
        import time
        latencies = []
        endpoints = [
            "https://images.pexels.com",
            "https://pixabay.com",
            "https://images.unsplash.com"
        ]
        for ep in endpoints:
            try:
                t0 = time.time()
                r = requests.get(ep, timeout=4)
                latencies.append(round((time.time() - t0) * 1000, 1))
            except Exception:
                pass
        avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else 250.0
        return {
            "avg_latency_ms": avg_latency,
            "speed_rating": "Fast (Fiber/Broadband)" if avg_latency < 150 else ("Normal" if avg_latency < 400 else "Slow")
        }

    @staticmethod
    def calculate_estimated_time(total_clips: int, quality: str = "1080p", parallel_workers: int = 4) -> Dict[str, Any]:
        """Estimates total pipeline execution time based on hardware and network conditions."""
        bm = SystemChecker.benchmark_speed()
        latency_factor = max(0.5, bm["avg_latency_ms"] / 150.0)

        # Base time per clip: AI (1.5s total batch) + Search (0.4s) + DL (1.5s * factor) + FFmpeg Transcode (0.8s)
        ai_time = 3.0
        search_time = (total_clips * 0.3) / max(1, parallel_workers)
        dl_time = (total_clips * 1.6 * latency_factor) / max(1, parallel_workers)
        
        quality_multiplier = 1.6 if quality == "4K" else (0.8 if quality == "720p" else 1.0)
        ffmpeg_time = (total_clips * 1.1 * quality_multiplier) / max(1, parallel_workers)

        total_sec = round(ai_time + search_time + dl_time + ffmpeg_time)
        return {
            "estimated_seconds": total_sec,
            "formatted_eta": f"{total_sec // 60}m {total_sec % 60}s" if total_sec >= 60 else f"{total_sec}s",
            "network_latency_ms": bm["avg_latency_ms"],
            "speed_rating": bm["speed_rating"],
            "parallel_workers": parallel_workers
        }

    @staticmethod
    def check_disk_space(target_path: Path, required_gb: float = 1.0) -> Dict[str, Any]:
        try:
            target_path.mkdir(parents=True, exist_ok=True)
            total, used, free = shutil.disk_usage(target_path)
            free_gb = round(free / (1024**3), 2)
            total_gb = round(total / (1024**3), 2)
            return {
                "sufficient": free_gb >= required_gb,
                "free_gb": free_gb,
                "total_gb": total_gb,
                "required_gb": required_gb,
            }
        except Exception as e:
            return {
                "sufficient": True,
                "free_gb": 99.0,
                "total_gb": 100.0,
                "required_gb": required_gb,
                "error": str(e),
            }

    @staticmethod
    def test_provider_api(provider: str, key: str = "", model: str = "", endpoint: str = "") -> Dict[str, Any]:
        p = provider.lower()
        if p == "openrouter":
            k = key or Config.OPENROUTER_API_KEY
            m = model or Config.OPENROUTER_MODEL
            if not k:
                return {"success": False, "message": "Missing OpenRouter API Key"}
            try:
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
                    json={"model": m, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5},
                    timeout=12,
                )
                if r.status_code == 200:
                    return {"success": True, "message": f"Connected to OpenRouter ({m})"}
                elif r.status_code == 401:
                    return {"success": False, "message": "Unauthorized (Invalid OpenRouter API Key)"}
                elif r.status_code == 404:
                    return {"success": False, "message": f"Model '{m}' not found (404) on OpenRouter"}
                elif r.status_code == 429:
                    return {"success": False, "message": "Rate limit / Quota exceeded (429)"}
                else:
                    return {"success": False, "message": f"OpenRouter returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Network Error: {str(e)}"}

        elif p == "cohere":
            k = key or Config.COHERE_API_KEY
            m = model or Config.COHERE_MODEL
            if not k:
                return {"success": False, "message": "Missing Cohere API Key"}
            try:
                r = requests.post(
                    "https://api.cohere.com/v2/chat",
                    headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
                    json={"model": m, "messages": [{"role": "user", "content": "Hi"}]},
                    timeout=12,
                )
                if r.status_code == 200:
                    return {"success": True, "message": f"Connected to Cohere ({m})"}
                elif r.status_code == 401:
                    return {"success": False, "message": "Unauthorized (Invalid Cohere API Key)"}
                else:
                    return {"success": False, "message": f"Cohere returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Network Error: {str(e)}"}

        elif p == "openai":
            k = key or Config.OPENAI_API_KEY
            m = model or Config.OPENAI_MODEL
            if not k:
                return {"success": False, "message": "Missing OpenAI API Key"}
            try:
                r = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
                    json={"model": m, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5},
                    timeout=12,
                )
                if r.status_code == 200:
                    return {"success": True, "message": f"Connected to OpenAI ({m})"}
                elif r.status_code == 401:
                    return {"success": False, "message": "Unauthorized (Invalid OpenAI Key)"}
                else:
                    return {"success": False, "message": f"OpenAI returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Network Error: {str(e)}"}

        elif p == "gemini":
            k = key or Config.GEMINI_API_KEY
            m = model or Config.GEMINI_MODEL
            if not k:
                return {"success": False, "message": "Missing Gemini API Key"}
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}"
                r = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={"contents": [{"parts": [{"text": "Hi"}]}]},
                    timeout=12,
                )
                if r.status_code == 200:
                    return {"success": True, "message": f"Connected to Google Gemini ({m})"}
                elif r.status_code in [400, 403]:
                    return {"success": False, "message": "Invalid Gemini API Key or Model"}
                else:
                    return {"success": False, "message": f"Gemini returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Network Error: {str(e)}"}

        elif p == "anthropic":
            k = key or Config.ANTHROPIC_API_KEY
            m = model or Config.ANTHROPIC_MODEL
            if not k:
                return {"success": False, "message": "Missing Anthropic API Key"}
            try:
                r = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": k, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                    json={"model": m, "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]},
                    timeout=12
                )
                if r.status_code == 200:
                    return {"success": True, "message": f"Connected to Anthropic ({m})"}
                else:
                    return {"success": False, "message": f"Anthropic returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Network Error: {str(e)}"}

        elif p == "groq":
            k = key or Config.GROQ_API_KEY
            m = model or Config.GROQ_MODEL
            if not k:
                return {"success": False, "message": "Missing Groq API Key"}
            try:
                r = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
                    json={"model": m, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5},
                    timeout=12
                )
                if r.status_code == 200:
                    return {"success": True, "message": f"Connected to Groq ({m})"}
                else:
                    return {"success": False, "message": f"Groq returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Network Error: {str(e)}"}

        elif p == "ollama":
            ep = endpoint or Config.OLLAMA_ENDPOINT
            m = model or Config.OLLAMA_MODEL
            try:
                r = requests.post(
                    ep,
                    json={"model": m, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5},
                    timeout=8
                )
                if r.status_code == 200:
                    return {"success": True, "message": f"Connected to Local Ollama ({m})"}
                else:
                    return {"success": False, "message": f"Ollama returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Ollama Connection Error (is Ollama running?): {str(e)}"}

        elif p in ["custom", "9router"]:
            ep = endpoint or Config.CUSTOM_AI_ENDPOINT
            k = key or Config.CUSTOM_AI_KEY
            m = model or Config.CUSTOM_AI_MODEL
            headers = {"Content-Type": "application/json"}
            if k:
                headers["Authorization"] = f"Bearer {k}"
            try:
                r = requests.post(
                    ep,
                    headers=headers,
                    json={"model": m, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5},
                    timeout=12,
                )
                if r.status_code == 200:
                    return {"success": True, "message": f"Connected to Custom AI / 9router ({ep})"}
                else:
                    return {"success": False, "message": f"Custom AI returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Connection Failed to {ep}: {str(e)}"}

        elif p == "pexels":
            k = key or Config.PEXELS_API_KEY
            if not k:
                return {"success": False, "message": "Missing Pexels API Key"}
            try:
                r = requests.get("https://api.pexels.com/v1/curated?per_page=1", headers={"Authorization": k}, timeout=10)
                if r.status_code == 200:
                    return {"success": True, "message": "Connected to Pexels API"}
                else:
                    return {"success": False, "message": f"Pexels returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Network Error: {str(e)}"}

        elif p == "pixabay":
            k = key or Config.PIXABAY_API_KEY
            if not k:
                return {"success": False, "message": "Missing Pixabay API Key"}
            try:
                r = requests.get(f"https://pixabay.com/api/?key={k}&q=nature&image_type=photo&per_page=3", timeout=10)
                if r.status_code == 200:
                    return {"success": True, "message": "Connected to Pixabay API"}
                else:
                    return {"success": False, "message": f"Pixabay returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Network Error: {str(e)}"}

        elif p == "unsplash":
            k = key or Config.UNSPLASH_API_KEY
            if not k:
                # Test public endpoint
                try:
                    r = requests.get("https://unsplash.com/napi/search/photos?query=nature&per_page=1", timeout=8)
                    if r.status_code == 200:
                        return {"success": True, "message": "Connected to Unsplash (Public Scraper Mode)"}
                except Exception:
                    pass
                return {"success": False, "message": "Missing Unsplash API Key"}
            try:
                r = requests.get(
                    "https://api.unsplash.com/photos/random?count=1",
                    headers={"Authorization": f"Client-ID {k}"},
                    timeout=10
                )
                if r.status_code == 200:
                    return {"success": True, "message": "Connected to Unsplash Official API"}
                else:
                    return {"success": False, "message": f"Unsplash returned HTTP {r.status_code}"}
            except Exception as e:
                return {"success": False, "message": f"Network Error: {str(e)}"}

        return {"success": False, "message": f"Unknown provider: {provider}"}

    @classmethod
    def get_system_health(cls) -> Dict[str, Any]:
        ffmpeg_info = cls.check_ffmpeg()
        disk_info = cls.check_disk_space(Config.OUTPUT_DIR)
        internet_ok = cls.check_internet()
        return {
            "status": "healthy" if ffmpeg_info["ffmpeg_available"] and disk_info["sufficient"] else "degraded",
            "ffmpeg": ffmpeg_info,
            "disk": disk_info,
            "internet": internet_ok,
        }
