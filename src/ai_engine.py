import json
import re
import math
import httpx
from typing import List, Dict, Any, Optional
from src.config import Config

class AIEngine:
    def __init__(
        self,
        openrouter_key: Optional[str] = None,
        openrouter_model: Optional[str] = None,
        cohere_key: Optional[str] = None,
        cohere_model: Optional[str] = None
    ):
        self.openrouter_key = openrouter_key or Config.OPENROUTER_API_KEY
        self.openrouter_model = openrouter_model or Config.OPENROUTER_MODEL
        self.cohere_key = cohere_key or Config.COHERE_API_KEY
        self.cohere_model = cohere_model or Config.COHERE_MODEL

    async def analyze_script(
        self,
        script: str,
        duration_seconds: float,
        clip_duration: float = 3.0,
        mood: str = "Cinematic"
    ) -> List[Dict[str, Any]]:
        """
        1-Shot Script Analysis:
        Calculates exact clip count = duration / clip_duration
        Decomposes the script sequentially into visual search queries.
        """
        clean_script = script.strip()
        if not clean_script:
            raise ValueError("Script cannot be empty")

        total_clips = max(1, math.ceil(duration_seconds / clip_duration))

        # Try OpenRouter
        if self.openrouter_key:
            try:
                clips = await self._call_openrouter(clean_script, total_clips, clip_duration, mood)
                if clips and len(clips) > 0:
                    return self._normalize_clips(clips, total_clips, clip_duration)
            except Exception as e:
                print(f"[WARN] OpenRouter failed: {e}. Attempting fallback...")

        # Try Cohere Fallback
        if self.cohere_key:
            try:
                clips = await self._call_cohere(clean_script, total_clips, clip_duration, mood)
                if clips and len(clips) > 0:
                    return self._normalize_clips(clips, total_clips, clip_duration)
            except Exception as e:
                print(f"[WARN] Cohere fallback failed: {e}. Attempting offline heuristic...")

        # Offline heuristic fallback (zero API dependency)
        return self._heuristic_fallback(clean_script, total_clips, clip_duration)

    async def rewrite_script(self, raw_text: str, style: str = "viral_hook") -> Dict[str, Any]:
        """
        AI Script Rewriter & Hook Enhancer.
        Transforms rough bullet points into high-retention video scripts.
        """
        raw_text = raw_text.strip()
        if not raw_text:
            raise ValueError("Text cannot be empty")

        style_prompts = {
            "viral_hook": "Rewrite this into a viral, high-retention video voiceover (MrBeast / Hormozi style). The first 3 seconds MUST have an irresistible hook, followed by high-energy pacing, actionable insight, and a sharp closing takeaway.",
            "storytelling": "Rewrite this into a cinematic documentary narrative (Vox / Kurzgesagt style). Evocative, atmospheric, with intellectual depth and curiosity loops.",
            "shorts": "Rewrite this into a fast-paced 20-30 second viral TikTok/Shorts script with extreme retention hooks and zero filler words.",
            "educational": "Rewrite this into a clean, authoritative, clear tutorial/explainer script for professional creators."
        }
        instruction = style_prompts.get(style, style_prompts["viral_hook"])

        prompt = f"""{instruction}

ORIGINAL DRAFT / BULLET POINTS:
\"\"\"{raw_text}\"\"\"

CRITICAL RULES:
1. Provide the enhanced voiceover script.
2. Estimated duration should be around 30 to 60 seconds (approx 70 - 140 words).
3. Output ONLY a valid JSON object with keys: "enhanced_script", "hook", "estimated_words", "estimated_seconds".

JSON FORMAT:
{{
  "hook": "The single opening sentence...",
  "enhanced_script": "Full rewritten voiceover text...",
  "estimated_words": 85,
  "estimated_seconds": 34
}}
"""
        if self.openrouter_key:
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/AliRash3ed/rotodraft-suite",
                    "X-Title": "RotoDraft Suite"
                }
                payload = {
                    "model": self.openrouter_model,
                    "messages": [
                        {"role": "system", "content": "You are a world-class viral video copywriter. Output strict JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    if match:
                        return json.loads(match.group(0))
            except Exception as e:
                print(f"[WARN] AI Script Rewrite failed: {e}. Using offline enhancement...")

        # Offline enhancement fallback
        words = raw_text.split()
        return {
            "hook": f"What if everything you knew about this was about to change?",
            "enhanced_script": f"What if everything you knew was wrong? {raw_text}. If you want to stay ahead of the curve, you must understand this now.",
            "estimated_words": len(words) + 20,
            "estimated_seconds": max(20, round((len(words) + 20) / 2.5))
        }

    async def generate_viral_metadata(self, script: str, topic: str = "") -> Dict[str, Any]:
        """
        Generates 5 Viral YouTube Titles, SEO Description with Timestamps, Tags, and Thumbnail Prompt.
        """
        clean_script = script.strip()
        prompt = f"""Generate YouTube and TikTok viral distribution metadata for this video script.

SCRIPT:
\"\"\"{clean_script[:1500]}\"\"\"

Generate:
1. 5 High-CTR Viral Titles (Curiosity gap, numbers, power words).
2. SEO Description (compelling summary + auto-formatted timestamps).
3. Top 15 Search Hashtags (e.g. #Tech #AI #ViralShorts).
4. Photorealistic Midjourney / Flux Prompt for a high-converting YouTube Thumbnail.

Output ONLY a JSON object:
{{
  "titles": ["Title 1", "Title 2", "Title 3", "Title 4", "Title 5"],
  "description": "Video description with timestamps...",
  "hashtags": ["#tag1", "#tag2", ...],
  "thumbnail_prompt": "Hyper-realistic 8k cinematic thumbnail of..."
}}
"""
        if self.openrouter_key:
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.openrouter_model,
                    "messages": [
                        {"role": "system", "content": "You are a YouTube growth & viral SEO specialist. Output strict JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.6
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    if match:
                        return json.loads(match.group(0))
            except Exception as e:
                print(f"[WARN] AI Metadata generation failed: {e}. Using offline metadata...")

        # Fallback offline generator
        first_sentence = clean_script.split(".")[0] if "." in clean_script else clean_script[:50]
        return {
            "titles": [
                f"The Truth Behind {first_sentence[:30]} (Nobody Tells You This)",
                f"Why 99% Of People Fail At This In 2026",
                f"This AI Secret Changes Everything We Know",
                f"How I Mastered This In 30 Seconds",
                f"Stop Doing This Right Now! (Watch Before It's Too Late)"
            ],
            "description": f"{clean_script}\n\n⏱️ TIMESTAMPS:\n00:00 - The Unseen Reality\n00:03 - Deep Dive & Strategy\n00:15 - Key Takeaway\n\n🔔 Subscribe for more high-value insights!",
            "hashtags": ["#ViralVideo", "#TechRevolution", "#ContentCreator", "#YouTubeGrowth", "#IndieHacker", "#ArtificialIntelligence"],
            "thumbnail_prompt": f"Hyperrealistic 8K cinematic YouTube thumbnail, dramatic neon blue lighting, glowing focal subject showing {first_sentence[:40]}, extreme depth of field, high contrast, 16:9 widescreen, octane render."
        }

    async def _call_openrouter(self, script: str, total_clips: int, clip_duration: float, mood: str) -> List[Dict[str, Any]]:
        prompt = self._build_prompt(script, total_clips, clip_duration, mood)
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/AliRash3ed/rotodraft-suite",
            "X-Title": "RotoDraft Suite"
        }
        payload = {
            "model": self.openrouter_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional Hollywood video editor and B-roll visual director. Output ONLY strict JSON. No conversational text."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return self._extract_json(content)

    async def _call_cohere(self, script: str, total_clips: int, clip_duration: float, mood: str) -> List[Dict[str, Any]]:
        prompt = self._build_prompt(script, total_clips, clip_duration, mood)
        url = "https://api.cohere.ai/v1/chat"
        headers = {
            "Authorization": f"Bearer {self.cohere_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.cohere_model,
            "message": prompt,
            "temperature": 0.3
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("text", "")
            return self._extract_json(content)

    def _build_prompt(self, script: str, total_clips: int, clip_duration: float, mood: str) -> str:
        return f"""Break down this video voiceover script into exactly {total_clips} sequential visual b-roll stock clips.
Each clip represents {clip_duration:.1f} seconds of visual narrative.
Visual Mood: {mood}

VOICEOVER SCRIPT:
\"\"\"{script}\"\"\"

CRITICAL RULES:
1. Generate EXACTLY {total_clips} clips in chronological sequence.
2. 'keyword': A 2-4 word high-intent generic stock video search query (e.g. 'businessman typing laptop', 'dark server room glowing led', 'crowded city street night'). DO NOT use abstract words or punctuation.
3. 'fallback_keyword': A simpler visual keyword (e.g. 'technology office', 'modern city').
4. Output MUST be a valid JSON array of objects.

JSON FORMAT EXAMPLE:
[
  {{
    "index": 1,
    "time_start": 0.0,
    "time_end": 3.0,
    "script_segment": "In today's fast moving world...",
    "keyword": "fast paced city traffic timelapse",
    "fallback_keyword": "city traffic"
  }}
]
"""

    def _extract_json(self, text: str) -> List[Dict[str, Any]]:
        text = text.strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict) and "clips" in parsed:
                return parsed["clips"]
        except Exception:
            pass

        match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        raise ValueError("Could not parse JSON array from AI response.")

    def _normalize_clips(self, clips: List[Dict[str, Any]], total_clips: int, clip_duration: float) -> List[Dict[str, Any]]:
        normalized = []
        for i in range(total_clips):
            if i < len(clips):
                c = clips[i]
                kw = re.sub(r'[^a-zA-Z0-9\s]', '', str(c.get("keyword", f"cinematic scene {i+1}"))).strip()
                fb = re.sub(r'[^a-zA-Z0-9\s]', '', str(c.get("fallback_keyword", "abstract visual"))).strip()
                seg = str(c.get("script_segment", ""))
            else:
                kw = f"visual footage {i+1}"
                fb = "background broll"
                seg = ""

            t_start = round(i * clip_duration, 2)
            t_end = round((i + 1) * clip_duration, 2)

            normalized.append({
                "index": i + 1,
                "time_start": t_start,
                "time_end": t_end,
                "duration": clip_duration,
                "script_segment": seg,
                "keyword": kw or f"stock video {i+1}",
                "fallback_keyword": fb or "nature background"
            })
        return normalized

    def _heuristic_fallback(self, script: str, total_clips: int, clip_duration: float) -> List[Dict[str, Any]]:
        words = script.split()
        words_per_clip = max(1, len(words) // total_clips)
        
        stock_seeds = [
            "modern business meeting", "cyberpunk digital technology", "ai neural network data",
            "stock market trading graph", "cinematic nature drone", "busy urban city street",
            "creative team brainstorming", "future abstract lights", "global network communication"
        ]

        clips = []
        for i in range(total_clips):
            start_w = i * words_per_clip
            end_w = (i + 1) * words_per_clip if i < total_clips - 1 else len(words)
            chunk = " ".join(words[start_w:end_w])
            
            clean_chunk = re.sub(r'[^a-zA-Z0-9\s]', '', chunk)
            chunk_words = [w for w in clean_chunk.split() if len(w) > 3]
            kw = " ".join(chunk_words[:3]) if chunk_words else stock_seeds[i % len(stock_seeds)]

            clips.append({
                "index": i + 1,
                "time_start": round(i * clip_duration, 2),
                "time_end": round((i + 1) * clip_duration, 2),
                "duration": clip_duration,
                "script_segment": chunk,
                "keyword": kw,
                "fallback_keyword": stock_seeds[(i + 1) % len(stock_seeds)]
            })
        return clips
