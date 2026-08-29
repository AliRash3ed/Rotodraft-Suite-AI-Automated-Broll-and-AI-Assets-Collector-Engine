import json
import re
import requests
from typing import List, Dict, Any, Optional
from src.config import Config
from src.logger import logger

class AIEngine:
    """
    Universal Multi-Provider AI Brain with Reasoning / Thinking Mode support.
    Supports OpenRouter, DeepSeek (Chat & R1 Reasoner), Groq, Google Gemini, Anthropic Claude, OpenAI, Cohere, Ollama, and Custom OpenAI-compatible endpoints.
    """

    def __init__(self, default_provider: Optional[str] = None):
        Config.load_saved_settings()
        self.default_provider = (default_provider or Config.DEFAULT_AI_PROVIDER).lower()
        self.proxies = {}
        if Config.HTTP_PROXY:
            self.proxies["http"] = Config.HTTP_PROXY
        if Config.HTTPS_PROXY:
            self.proxies["https"] = Config.HTTPS_PROXY

    def generate_keywords(
        self,
        script: str,
        duration_seconds: float,
        clip_duration: float = 3.0,
        provider: Optional[str] = None,
        custom_model: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        Config.load_saved_settings()
        active_provider = (provider or self.default_provider).lower()
        num_clips = max(1, int(round(duration_seconds / clip_duration)))

        logger.info(
            f"Analyzing script ({duration_seconds}s -> {num_clips} sequential {clip_duration}s clips) via [{active_provider.upper()}]...",
            "AI"
        )

        prompt = self._build_prompt(script, duration_seconds, clip_duration, num_clips)
        errors = []

        # 1. Primary Call
        try:
            raw_response = self._dispatch_call(active_provider, prompt, custom_model)
            keywords = self._parse_json(raw_response, num_clips)
            if len(keywords) > 0:
                logger.success(f"Generated {len(keywords)} sequential stock keywords successfully via {active_provider.upper()}!", "AI")
                return keywords
        except Exception as e:
            logger.error(f"Primary AI Provider [{active_provider.upper()}] Error: {str(e)}", "AI")
            errors.append(f"{active_provider}: {str(e)}")

        # 2. Automatic Fallback Cascade
        fallback_order = ["openrouter", "deepseek", "groq", "gemini", "cohere", "openai", "anthropic", "ollama", "custom"]
        if active_provider in fallback_order:
            fallback_order.remove(active_provider)

        for fb_prov in fallback_order:
            if self._has_key(fb_prov):
                logger.warning(f"Cascading fallback to AI Provider [{fb_prov.upper()}]...", "AI")
                try:
                    raw_response = self._dispatch_call(fb_prov, prompt)
                    keywords = self._parse_json(raw_response, num_clips)
                    if len(keywords) > 0:
                        logger.success(f"Fallback to {fb_prov.upper()} succeeded with {len(keywords)} keywords!", "AI")
                        return keywords
                except Exception as fb_err:
                    logger.error(f"Fallback [{fb_prov.upper()}] failed: {str(fb_err)}", "AI")
                    errors.append(f"{fb_prov}: {str(fb_err)}")

        raise RuntimeError(f"AI Keyword generation failed across all providers. Details: {'; '.join(errors)}")

    def _has_key(self, prov: str) -> bool:
        if prov == "openrouter": return bool(Config.OPENROUTER_API_KEY)
        if prov == "deepseek": return bool(Config.DEEPSEEK_API_KEY)
        if prov == "groq": return bool(Config.GROQ_API_KEY)
        if prov == "gemini": return bool(Config.GEMINI_API_KEY)
        if prov == "cohere": return bool(Config.COHERE_API_KEY)
        if prov == "openai": return bool(Config.OPENAI_API_KEY)
        if prov == "anthropic": return bool(Config.ANTHROPIC_API_KEY)
        if prov == "ollama": return bool(Config.OLLAMA_ENDPOINT)
        if prov in ["custom", "9router"]: return bool(Config.CUSTOM_AI_ENDPOINT)
        return False

    def _dispatch_call(self, prov: str, prompt: str, model_override: Optional[str] = None) -> str:
        if prov == "openrouter":
            return self._call_openrouter(prompt, model=model_override)
        elif prov == "deepseek":
            return self._call_deepseek(prompt, model=model_override)
        elif prov == "groq":
            return self._call_groq(prompt, model=model_override)
        elif prov == "gemini":
            return self._call_gemini(prompt, model=model_override)
        elif prov == "cohere":
            return self._call_cohere(prompt, model=model_override)
        elif prov == "openai":
            return self._call_openai(prompt, model=model_override)
        elif prov == "anthropic":
            return self._call_anthropic(prompt, model=model_override)
        elif prov == "ollama":
            return self._call_ollama(prompt, model=model_override)
        elif prov in ["custom", "9router"]:
            return self._call_custom(prompt, model=model_override)
        else:
            return self._call_openrouter(prompt, model=model_override)

    def _build_prompt(
        self, script: str, duration_seconds: float, clip_duration: float, num_clips: int
    ) -> str:
        return f"""You are an elite video editor and b-roll director.
Analyze the following video voiceover script and divide it into EXACTLY {num_clips} sequential {clip_duration}-second visual scenes.
Total voiceover duration: {duration_seconds} seconds.
Each scene duration: {clip_duration} seconds.

SCRIPT:
\"\"\"{script.strip()}\"\"\"

Generate EXACTLY {num_clips} sequential visual stock search keywords mapped to each {clip_duration}-second portion of the script in narrative chronological order.
The keywords MUST be:
1. Highly searchable, cinematic, generic stock footage queries (2 to 4 words, e.g. "busy city traffic", "modern office meeting", "stock market chart", "cyber security network", "person using laptop").
2. Real-world visual objects, actions, or environments that physically exist on stock media platforms (Pexels, Pixabay, Unsplash, Pinterest).
3. Avoid abstract philosophical sentences or overly specific names.

You MUST output ONLY a valid JSON array of objects with NO surrounding text, no markdown explanation, no conversational filler.
Schema for each item:
{{
  "index": 1,
  "time_start": 0.0,
  "time_end": {clip_duration},
  "script_segment": "short snippet of script for this moment",
  "keyword": "primary stock search query",
  "fallback_keyword": "generic secondary stock search query",
  "visual_description": "short description of visual action"
}}

Output strictly the JSON array of {num_clips} items."""

    def _call_openrouter(self, prompt: str, model: str = None) -> str:
        key = Config.OPENROUTER_API_KEY
        if not key:
            raise ValueError("OpenRouter API key is missing. Configure it in Settings -> AI Providers.")
        model = model or Config.OPENROUTER_MODEL
        headers = {
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Stock B-Roll Collector Pro",
            "Content-Type": "application/json",
        }
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a professional video b-roll director that outputs strictly valid JSON arrays."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=45, proxies=self.proxies)
        if resp.status_code != 200:
            raise RuntimeError(f"OpenRouter HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.json()["choices"][0]["message"]["content"]

    def _call_deepseek(self, prompt: str, model: str = None) -> str:
        key = Config.DEEPSEEK_API_KEY
        if not key:
            raise ValueError("DeepSeek API key is missing. Get one at platform.deepseek.com/api_keys.")
        model = model or Config.DEEPSEEK_MODEL or "deepseek-chat"
        base_url = Config.DEEPSEEK_BASE_URL.rstrip("/")
        url = f"{base_url}/chat/completions" if not base_url.endswith("/chat/completions") else base_url
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a professional b-roll director that outputs strictly valid JSON arrays."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        resp = requests.post(url, headers=headers, json=data, timeout=60, proxies=self.proxies)
        if resp.status_code != 200:
            raise RuntimeError(f"DeepSeek returned HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.json()["choices"][0]["message"]["content"]

    def _call_groq(self, prompt: str, model: str = None) -> str:
        key = Config.GROQ_API_KEY
        if not key:
            raise ValueError("Groq API key is missing. Get one free at console.groq.com/keys.")
        model = model or Config.GROQ_MODEL
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a b-roll director that outputs strictly valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=30, proxies=self.proxies)
        if resp.status_code != 200:
            raise RuntimeError(f"Groq returned HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.json()["choices"][0]["message"]["content"]

    def _call_gemini(self, prompt: str, model: str = None) -> str:
        key = Config.GEMINI_API_KEY
        if not key:
            raise ValueError("Google Gemini API key is missing. Get one free on Google AI Studio.")
        model = model or Config.GEMINI_MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2}
        }
        resp = requests.post(url, headers=headers, json=data, timeout=45, proxies=self.proxies)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini returned HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _call_openai(self, prompt: str, model: str = None) -> str:
        key = Config.OPENAI_API_KEY
        if not key:
            raise ValueError("OpenAI API key is missing.")
        model = model or Config.OPENAI_MODEL
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a b-roll director that outputs strictly valid JSON arrays."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=45, proxies=self.proxies)
        if resp.status_code != 200:
            raise RuntimeError(f"OpenAI returned HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.json()["choices"][0]["message"]["content"]

    def _call_anthropic(self, prompt: str, model: str = None) -> str:
        key = Config.ANTHROPIC_API_KEY
        if not key:
            raise ValueError("Anthropic API key is missing.")
        model = model or Config.ANTHROPIC_MODEL
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        data = {
            "model": model,
            "max_tokens": 4096,
            "system": "You are a b-roll director that outputs strictly valid JSON arrays.",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data, timeout=45, proxies=self.proxies)
        if resp.status_code != 200:
            raise RuntimeError(f"Anthropic returned HTTP {resp.status_code}: {resp.text[:200]}")
        content = resp.json().get("content", [])
        if content and "text" in content[0]:
            return content[0]["text"]
        return str(resp.json())

    def _call_cohere(self, prompt: str, model: str = None) -> str:
        key = Config.COHERE_API_KEY
        if not key:
            raise ValueError("Cohere API key is missing.")
        model = model or Config.COHERE_MODEL
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        resp = requests.post("https://api.cohere.com/v2/chat", headers=headers, json=data, timeout=45, proxies=self.proxies)
        if resp.status_code != 200:
            raise RuntimeError(f"Cohere returned HTTP {resp.status_code}: {resp.text[:200]}")
        content = resp.json().get("message", {}).get("content", [])
        if content and isinstance(content, list) and "text" in content[0]:
            return content[0]["text"]
        return str(resp.json())

    def _call_ollama(self, prompt: str, model: str = None) -> str:
        ep = Config.OLLAMA_ENDPOINT
        model = model or Config.OLLAMA_MODEL
        headers = {"Content-Type": "application/json"}
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a b-roll director that outputs strictly valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        resp = requests.post(ep, headers=headers, json=data, timeout=60, proxies=self.proxies)
        if resp.status_code != 200:
            raise RuntimeError(f"Ollama returned HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.json()["choices"][0]["message"]["content"]

    def _call_custom(self, prompt: str, model: str = None) -> str:
        ep = Config.CUSTOM_AI_ENDPOINT
        key = Config.CUSTOM_AI_KEY
        model = model or Config.CUSTOM_AI_MODEL
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a b-roll director that outputs strictly valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            "temperature": Config.CUSTOM_AI_TEMPERATURE,
            "max_tokens": Config.CUSTOM_AI_MAX_TOKENS,
        }
        resp = requests.post(ep, headers=headers, json=data, timeout=60, proxies=self.proxies)
        if resp.status_code != 200:
            raise RuntimeError(f"Custom AI returned HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.json()["choices"][0]["message"]["content"]

    def _parse_json(self, raw_text: str, expected_count: int) -> List[Dict[str, Any]]:
        text = raw_text.strip()
        
        # 🧠 Thinking Mode Strip: Remove <think>...</think> monologue if present
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            text = text.strip()

        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            json_str = text[start : end + 1]
        else:
            json_str = text

        try:
            items = json.loads(json_str)
        except Exception:
            cleaned = re.sub(r",\s*([\]}])", r"\1", json_str)
            items = json.loads(cleaned)

        if not isinstance(items, list):
            raise ValueError("Parsed AI output is not a JSON array.")

        validated: List[Dict[str, Any]] = []
        for i, item in enumerate(items, 1):
            if isinstance(item, str):
                item = {
                    "index": i,
                    "keyword": item,
                    "fallback_keyword": item.split()[0] if item.split() else "abstract background",
                    "script_segment": "",
                    "visual_description": item,
                }
            
            kw = item.get("keyword", "").strip() or f"scene {i}"
            fb = item.get("fallback_keyword", "").strip() or "cinematic background"
            
            validated.append({
                "index": i,
                "time_start": round((i - 1) * 3.0, 1),
                "time_end": round(i * 3.0, 1),
                "script_segment": item.get("script_segment", "").strip(),
                "keyword": kw,
                "fallback_keyword": fb,
                "visual_description": item.get("visual_description", "").strip(),
            })

        return validated
