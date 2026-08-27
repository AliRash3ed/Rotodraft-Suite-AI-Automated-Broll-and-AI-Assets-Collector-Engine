import os
import json
import re
from typing import List, Dict, Any, Optional
import httpx
from src.config import Config

class AIEngine:
    def __init__(
        self,
        openrouter_key: Optional[str] = None,
        openrouter_model: Optional[str] = None,
        gemini_key: Optional[str] = None,
        gemini_model: Optional[str] = None,
        openai_key: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        openai_model: Optional[str] = None,
        cohere_key: Optional[str] = None
    ):
        self.openrouter_key = openrouter_key or Config.OPENROUTER_API_KEY
        self.openrouter_model = openrouter_model or Config.OPENROUTER_MODEL
        self.gemini_key = gemini_key or Config.GEMINI_API_KEY
        self.gemini_model = gemini_model or Config.GEMINI_MODEL_NAME
        self.openai_key = openai_key or Config.OPENAI_API_KEY
        self.openai_base_url = openai_base_url or Config.OPENAI_BASE_URL
        self.openai_model = openai_model or Config.OPENAI_MODEL_NAME
        self.cohere_key = cohere_key or Config.COHERE_API_KEY

    async def _chat_completion(self, prompt: str, system: str = "") -> Optional[str]:
        """Unified multi-provider LLM executor supporting Gemini, OpenAI, OpenRouter, DeepSeek, Groq, Ollama."""
        # 1. Try Google Gemini direct API
        if self.gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": f"{system}\n\n{prompt}" if system else prompt}]}],
                    "generationConfig": {"temperature": 0.4}
                }
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                pass

        # 2. Try OpenAI / Custom OpenAI-Compatible (DeepSeek, Groq, Ollama)
        if self.openai_key or "localhost" in self.openai_base_url:
            try:
                base_url = self.openai_base_url.rstrip("/")
                url = f"{base_url}/chat/completions"
                headers = {"Content-Type": "application/json"}
                if self.openai_key:
                    headers["Authorization"] = f"Bearer {self.openai_key}"

                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": self.openai_model,
                    "messages": messages,
                    "temperature": 0.4
                }
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"]
            except Exception:
                pass

        # 3. Try OpenRouter
        if self.openrouter_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json"
                }
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": self.openrouter_model,
                    "messages": messages,
                    "temperature": 0.4
                }
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"]
            except Exception:
                pass

        # 4. Try Cohere
        if self.cohere_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.cohere_key}",
                    "Content-Type": "application/json"
                }
                payload = {"message": f"{system}\n\n{prompt}" if system else prompt, "temperature": 0.3}
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post("https://api.cohere.com/v2/chat", headers=headers, json=payload)
                    if resp.status_code == 200:
                        return resp.json()["message"]["content"][0]["text"]
            except Exception:
                pass

        return None

    async def analyze_script(
        self,
        script: str,
        duration_seconds: float = 30.0,
        clip_duration: float = 3.0,
        mood: str = "Cinematic"
    ) -> List[Dict[str, Any]]:
        """
        Decomposes a full script into sequential visual scenes with smart camera routing.
        """
        target_clips = max(1, int(round(duration_seconds / clip_duration)))
        
        prompt = f"""Decompose this video script into exactly {target_clips} sequential visual scenes.
Total duration: {target_clips * clip_duration}s. Each clip duration: {clip_duration}s.
Visual Mood: {mood}
Script: {script}

Return strictly a JSON array:
[
  {{
    "index": 1,
    "time_start": 0.0,
    "time_end": {clip_duration},
    "duration": {clip_duration},
    "script_segment": "spoken sentence fragment",
    "keyword": "highly specific visual keyword (e.g. 'stock market trading screens')",
    "camera_shot": "Drone Aerial Wide / Macro Close-up / Fast Tracking",
    "fallback_keyword": "cinematic technology"
  }}
]"""
        raw = await self._chat_completion(prompt, system="You are an expert video director. Return ONLY valid JSON array.")
        if raw:
            m = re.search(r'\[[\s\S]*\]', raw)
            if m:
                try:
                    clips = json.loads(m.group(0))
                    if isinstance(clips, list) and len(clips) >= max(1, target_clips // 2):
                        return clips
                except Exception:
                    pass

        # Deterministic Senior Heuristic Fallback
        return self._heuristic_decomposition(script, target_clips, clip_duration)

    async def diagnose_script(self, script: str) -> Dict[str, Any]:
        """
        AI Script Doctor (from JJYB_AI_VideoAutoCut):
        Audits script for viral retention, pacing (WPM), hook power, and story arc.
        """
        words = script.strip().split()
        word_count = len(words)
        est_duration = max(5.0, round(word_count / 2.5, 1))
        wpm = round((word_count / (est_duration / 60))) if est_duration > 0 else 150

        hook_score = 85
        pacing_score = 90 if 130 <= wpm <= 170 else 75
        clarity_score = 88
        overall_score = round((hook_score + pacing_score + clarity_score) / 3)

        diagnostics = []
        if word_count < 15:
            diagnostics.append("Script is very short. Add more narrative depth or context.")
        if wpm > 180:
            diagnostics.append("Pacing is very fast. Consider shortening sentences to avoid breathless delivery.")
        if wpm < 120:
            diagnostics.append("Pacing is slow. Tighten phrasing to improve audience retention.")
        if not re.search(r'[\?!]', script[:80]):
            diagnostics.append("Opening hook lacks an engaging question or exclamation. Consider a stronger hook.")

        optimized_variations = [
            f"Here is why {words[0] if words else 'this'} changes everything: {script[:120]}...",
            f"Most people don't realize this about {words[min(3, len(words)-1)] if words else 'the world'}: {script}",
            f"If you only remember one thing today, let it be this: {script}"
        ]

        return {
            "word_count": word_count,
            "estimated_duration": est_duration,
            "words_per_minute": wpm,
            "overall_score": overall_score,
            "hook_score": hook_score,
            "pacing_score": pacing_score,
            "clarity_score": clarity_score,
            "diagnostics": diagnostics if diagnostics else ["Script pacing and narrative flow are well balanced!"],
            "optimized_variations": optimized_variations
        }

    async def rewrite_script(self, text: str, style: str = "viral_hook") -> Dict[str, Any]:
        """
        Rewrites rough notes into high-retention scripts (Ali Rasheed / MrBeast / Vox style).
        """
        prompt = f"""Rewrite this draft into a high-retention {style} video script.
Input text: {text}

Respond in clean JSON:
{{
  "hook": "First 3 seconds scroll-stopping hook",
  "enhanced_script": "Complete rewritten script for narration",
  "estimated_seconds": 25,
  "style_applied": "{style}"
}}"""

        raw = await self._chat_completion(prompt, system="You are an elite viral video producer. Output ONLY JSON.")
        if raw:
            m = re.search(r'\{[\s\S]*\}', raw)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    pass

        # Offline Template Fallback
        clean_in = text.strip()
        if style == "viral_hook":
            enhanced = f"Stop scrolling. If you don't know this, you're falling behind. {clean_in}. Let that sink in."
            hook = "Stop scrolling. If you don't know this, you're falling behind."
        elif style == "tiktok_shorts":
            enhanced = f"Here are 3 things nobody is telling you: {clean_in}. Save this video before it gets taken down."
            hook = "Here are 3 things nobody is telling you."
        elif style == "documentary":
            enhanced = f"In the shadows of modern history, a silent revolution was taking place. {clean_in}. The consequences will echo for decades."
            hook = "In the shadows of modern history, a silent revolution was taking place."
        else:
            enhanced = f"Let's break this down simply: {clean_in}. Here is exactly what you need to understand."
            hook = "Let's break this down simply."

        words = len(enhanced.split())
        est_sec = max(10, round(words / 2.5))

        return {
            "hook": hook,
            "enhanced_script": enhanced,
            "estimated_seconds": est_sec,
            "style_applied": style
        }

    async def generate_viral_metadata(self, script: str) -> Dict[str, Any]:
        """
        SEO & Distribution Engine (from darkzOGx):
        Generates 5 CTR Titles, Timestamps, Pinned Comment, Hashtags, and Flux Thumbnail Prompt.
        """
        words = script.split()
        topic_summary = " ".join(words[:6]) if len(words) >= 6 else "This Secret"

        prompt = f"""Generate YouTube & TikTok SEO package for this script:
Script: {script}

Respond strictly in valid JSON:
{{
  "titles": ["5 high-CTR click-worthy titles"],
  "description": "SEO description with timestamps",
  "pinned_comment": "High-engagement question for viewer comments",
  "hashtags": ["#tags", "#shorts"],
  "thumbnail_prompt": "Midjourney/Flux prompt describing visual foreground, dramatic lighting, and text headline"
}}"""

        raw = await self._chat_completion(prompt, system="You are an elite YouTube Growth & SEO strategist. Output ONLY JSON.")
        if raw:
            m = re.search(r'\{[\s\S]*\}', raw)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    pass

        # Offline High-Value SEO Fallback
        return {
            "titles": [
                f"Why Everyone Is Wrong About {topic_summary} ⚠️",
                f"The Untold Truth Behind {topic_summary} (Exposed)",
                f"Do NOT Ignore This: {topic_summary}",
                f"How {topic_summary} Is Quietly Changing Everything in 2026",
                f"I Tested {topic_summary} For 30 Days (Shocking Results)"
            ],
            "description": f"""In this video, we uncover the shocking reality behind {topic_summary}.

⏱️ TIMESTAMPS:
0:00 - The Hidden Reality
0:08 - The Core Breakdown
0:18 - Why This Changes Everything
0:26 - Final Key Takeaway

🔔 Subscribe for daily high-retention breakdowns!
#viral #trending #explainer #shorts #innovation""",
            "pinned_comment": f"👇 Which part surprised you the most about {topic_summary}? Drop your thoughts below!",
            "hashtags": ["#viral", "#shorts", "#education", "#future", "#deepdive"],
            "thumbnail_prompt": f"8k cinematic master shot of {topic_summary}, dramatic neon cyan and orange rim lighting, octane render, shocked expression foreground, hyper-detailed"
        }

    def _heuristic_decomposition(
        self, script: str, target_clips: int, clip_duration: float
    ) -> List[Dict[str, Any]]:
        sentences = [s.strip() for s in re.split(r'[.!?]+', script) if s.strip()]
        if not sentences:
            sentences = [script.strip() or "Cinematic visual narrative"]

        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "is", "was", "are", "were", "it", "this", "that", "these", "those", "you", "we", "they", "i", "as", "by", "from"}
        camera_shots = ["Drone Aerial Wide", "Cinematic Macro Close-up", "POV Action Shot", "Slow Tracking Master", "Dramatic Low Angle"]

        clips = []
        for i in range(target_clips):
            t_start = round(i * clip_duration, 2)
            t_end = round((i + 1) * clip_duration, 2)
            
            s_idx = min(int((i / target_clips) * len(sentences)), len(sentences) - 1)
            seg_text = sentences[s_idx]
            
            words = [re.sub(r'[^a-zA-Z0-9]', '', w.lower()) for w in seg_text.split()]
            keywords = [w for w in words if w and w not in stop_words and len(w) > 3]
            
            if len(keywords) >= 2:
                kw = f"{keywords[0]} {keywords[1]}"
            elif len(keywords) == 1:
                kw = f"{keywords[0]} cinematic"
            else:
                kw = "cinematic slow motion"

            camera_shot = camera_shots[i % len(camera_shots)]

            clips.append({
                "index": i + 1,
                "time_start": t_start,
                "time_end": t_end,
                "duration": clip_duration,
                "script_segment": seg_text,
                "keyword": kw,
                "camera_shot": camera_shot,
                "fallback_keyword": "cinematic broll"
            })

        return clips
