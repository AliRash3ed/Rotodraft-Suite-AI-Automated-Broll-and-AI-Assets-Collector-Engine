import re
import random
import urllib.parse
import httpx
from typing import Dict, Any, Optional, List
from src.config import Config
from src.pinterest_scraper import PinterestScraper

class StockSearcher:
    def __init__(
        self,
        pexels_key: Optional[str] = None,
        pixabay_key: Optional[str] = None,
        dalle_key: Optional[str] = None
    ):
        self.pexels_key = pexels_key or Config.PEXELS_API_KEY
        self.pixabay_key = pixabay_key or Config.PIXABAY_API_KEY
        self.dalle_key = dalle_key or Config.OPENAI_API_KEY
        self.pinterest = PinterestScraper()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

    async def find_stock(
        self,
        keyword: str,
        fallback_keyword: str = "",
        aspect_ratio: str = "16:9",
        quality: str = "1080p",
        page: int = 1,
        media_filter: str = "mixed",        # "videos_only", "photos_only", "mixed", "pure_ai"
        ai_image_engine: str = "pollinations", # "pollinations", "dalle3"
        enable_pinterest: bool = True
    ) -> Dict[str, Any]:
        """
        Unified enterprise multi-tier media sourcing engine:
        - media_filter = 'pure_ai': Immediately routes to Flux / DALL-E 3
        - media_filter = 'videos_only': Skips photos
        - media_filter = 'photos_only': Skips stock videos
        - media_filter = 'mixed': Cascades videos -> photos -> AI fallback
        """
        orientation = Config.RESOLUTIONS.get(aspect_ratio, {}).get("orientation", "landscape")
        
        # 1. Pure AI mode
        if media_filter == "pure_ai":
            if ai_image_engine == "dalle3" and self.dalle_key:
                dalle_res = await self._generate_dalle3_image(keyword, aspect_ratio)
                if dalle_res:
                    return dalle_res
            return self._generate_ai_image_fallback(keyword, aspect_ratio)

        # 2. Try Video Providers (if mixed or videos_only)
        if media_filter in ["videos_only", "mixed"]:
            if self.pexels_key:
                res = await self._search_pexels_video(keyword, orientation, quality, page=page)
                if not res and fallback_keyword:
                    res = await self._search_pexels_video(fallback_keyword, orientation, quality, page=page)
                if res:
                    return res

            if self.pixabay_key:
                res = await self._search_pixabay_video(keyword, orientation, page=page)
                if not res and fallback_keyword:
                    res = await self._search_pixabay_video(fallback_keyword, orientation, page=page)
                if res:
                    return res

            if enable_pinterest:
                res = await self.pinterest.scrape_video(keyword)
                if not res and fallback_keyword:
                    res = await self.pinterest.scrape_video(fallback_keyword)
                if res:
                    return res

        # 3. Try Photo Providers (if mixed or photos_only)
        if media_filter in ["photos_only", "mixed"]:
            img_res = await self._search_stock_image(keyword, fallback_keyword, orientation)
            if img_res:
                return img_res

        # 4. Fallback to AI Image Generator (Pollinations Flux AI or DALL-E 3)
        if ai_image_engine == "dalle3" and self.dalle_key:
            dalle_res = await self._generate_dalle3_image(keyword, aspect_ratio)
            if dalle_res:
                return dalle_res

        return self._generate_ai_image_fallback(keyword, aspect_ratio)

    async def _generate_dalle3_image(self, prompt: str, aspect_ratio: str) -> Optional[Dict[str, Any]]:
        """Generates 4K photorealistic scene via OpenAI DALL-E 3."""
        try:
            size = "1024x1792" if aspect_ratio == "9:16" else "1792x1024"
            headers = {"Authorization": f"Bearer {self.dalle_key}", "Content-Type": "application/json"}
            payload = {
                "model": "dall-e-3",
                "prompt": f"8k cinematic master shot, photorealistic b-roll footage of {prompt}, dramatic lighting, hyper-detailed",
                "n": 1,
                "size": size,
                "quality": "standard"
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post("https://api.openai.com/v1/images/generations", headers=headers, json=payload)
                if resp.status_code == 200:
                    url = resp.json()["data"][0]["url"]
                    return {
                        "provider": "openai_dalle3_kenburns",
                        "url": url,
                        "thumbnail": url,
                        "type": "ai_image",
                        "quality": "dalle3_4k",
                        "duration": 3.0,
                        "author": "OpenAI DALL-E 3"
                    }
        except Exception:
            pass
        return None

    def _generate_ai_image_fallback(self, query: str, aspect_ratio: str) -> Dict[str, Any]:
        """Free AI generation via Pollinations Flux AI."""
        clean_prompt = f"8k cinematic photorealistic master shot of {query}, volumetric lighting, photorealism, award winning photography"
        encoded = urllib.parse.quote(clean_prompt)
        w, h = (1080, 1920) if aspect_ratio == "9:16" else (1920, 1080)
        img_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&model=flux&nologo=true&seed={random.randint(1000, 999999)}"

        return {
            "provider": "pollinations_ai_flux_kenburns",
            "url": img_url,
            "thumbnail": img_url,
            "type": "ai_image",
            "quality": "flux_4k_ai",
            "duration": 3.0,
            "author": "Pollinations AI (Flux Pro)"
        }

    async def _search_pexels_video(self, query: str, orientation: str, quality: str, page: int = 1) -> Optional[Dict[str, Any]]:
        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation={orientation}&per_page=5&page={page}"
        headers = {**self.headers, "Authorization": self.pexels_key}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code != 200:
                    return None
                data = resp.json()
                videos = data.get("videos", [])
                if not videos:
                    return None
                
                video = videos[0]
                video_files = video.get("video_files", [])
                hd_files = [vf for vf in video_files if vf.get("quality") == "hd"]
                target_file = hd_files[0] if hd_files else video_files[0]

                return {
                    "provider": "pexels",
                    "url": target_file["link"],
                    "thumbnail": video.get("image", ""),
                    "type": "video",
                    "quality": target_file.get("quality", "hd"),
                    "duration": float(video.get("duration", 5.0)),
                    "author": video.get("user", {}).get("name", "Pexels Creator")
                }
        except Exception:
            return None

    async def _search_pixabay_video(self, query: str, orientation: str, page: int = 1) -> Optional[Dict[str, Any]]:
        url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={urllib.parse.quote(query)}&per_page=5&page={page}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    return None
                data = resp.json()
                hits = data.get("hits", [])
                if not hits:
                    return None
                
                hit = hits[0]
                videos = hit.get("videos", {})
                target_video = videos.get("large") or videos.get("medium") or videos.get("small")
                if not target_video:
                    return None

                return {
                    "provider": "pixabay",
                    "url": target_video["url"],
                    "thumbnail": hit.get("videos", {}).get("small", {}).get("thumbnail", ""),
                    "type": "video",
                    "quality": "hd",
                    "duration": float(hit.get("duration", 5.0)),
                    "author": hit.get("user", "Pixabay Creator")
                }
        except Exception:
            return None

    async def _search_stock_image(self, query: str, fallback_query: str, orientation: str) -> Optional[Dict[str, Any]]:
        if self.pexels_key:
            url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&orientation={orientation}&per_page=5"
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(url, headers={**self.headers, "Authorization": self.pexels_key})
                    if resp.status_code == 200:
                        photos = resp.json().get("photos", [])
                        if photos:
                            p = photos[0]
                            return {
                                "provider": "pexels_image_kenburns",
                                "url": p["src"]["large2x"],
                                "thumbnail": p["src"]["medium"],
                                "type": "image",
                                "quality": "photo_hd",
                                "duration": 3.0,
                                "author": p.get("photographer", "Pexels")
                            }
            except Exception:
                pass
        return None
