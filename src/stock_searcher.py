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
        pixabay_key: Optional[str] = None
    ):
        self.pexels_key = pexels_key or Config.PEXELS_API_KEY
        self.pixabay_key = pixabay_key or Config.PIXABAY_API_KEY
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
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Unified enterprise multi-tier media sourcing engine:
        1. Pexels Video API (1080p/4K filtered by aspect ratio)
        2. Pixabay Video API
        3. Playwright Pinterest Video Scraper
        4. High-Res Stock Photography
        5. 100% Free AI Image Generation (Pollinations / Flux Engine) with 60fps Ken Burns Motion
        """
        orientation = Config.RESOLUTIONS.get(aspect_ratio, {}).get("orientation", "landscape")
        
        # 1. Try Pexels Video
        if self.pexels_key:
            res = await self._search_pexels_video(keyword, orientation, quality, page=page)
            if not res and fallback_keyword:
                res = await self._search_pexels_video(fallback_keyword, orientation, quality, page=page)
            if res:
                return res

        # 2. Try Pixabay Video
        if self.pixabay_key:
            res = await self._search_pixabay_video(keyword, orientation, page=page)
            if not res and fallback_keyword:
                res = await self._search_pixabay_video(fallback_keyword, orientation, page=page)
            if res:
                return res

        # 3. Try Production Playwright Pinterest Scraper
        res = await self.pinterest.scrape_video(keyword)
        if not res and fallback_keyword:
            res = await self.pinterest.scrape_video(fallback_keyword)
        if res:
            return res

        # 4. Try Stock Image
        img_res = await self._search_stock_image(keyword, fallback_keyword, orientation)
        if img_res:
            return img_res

        # 5. Free AI Image Generator (Pollinations Flux AI Engine)
        return self._generate_ai_image_fallback(keyword, aspect_ratio)

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
                
                video = videos[0] if len(videos) > 0 else None
                if not video:
                    return None
                video_files = video.get("video_files", [])
                if not video_files:
                    return None

                target_h = 1080 if quality == "1080p" else (2160 if quality == "4K" else 720)
                best_file = min(video_files, key=lambda f: abs(f.get("height", 720) - target_h))
                
                return {
                    "provider": "pexels",
                    "url": best_file.get("link"),
                    "is_image": False,
                    "width": best_file.get("width", 1920),
                    "height": best_file.get("height", 1080),
                    "keyword": query,
                    "author": video.get("user", {}).get("name", "Pexels Creator")
                }
        except Exception as e:
            print(f"[WARN] Pexels video search error: {e}")
            return None

    async def _search_pixabay_video(self, query: str, orientation: str, page: int = 1) -> Optional[Dict[str, Any]]:
        url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={urllib.parse.quote(query)}&per_page=5&page={page}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code != 200:
                    return None
                data = resp.json()
                hits = data.get("hits", [])
                if not hits:
                    return None
                
                hit = hits[0]
                videos = hit.get("videos", {})
                chosen = videos.get("large") or videos.get("medium") or videos.get("small")
                if not chosen or not chosen.get("url"):
                    return None

                return {
                    "provider": "pixabay",
                    "url": chosen.get("url"),
                    "is_image": False,
                    "width": chosen.get("width", 1920),
                    "height": chosen.get("height", 1080),
                    "keyword": query,
                    "author": hit.get("user", "Pixabay Creator")
                }
        except Exception as e:
            print(f"[WARN] Pixabay search error: {e}")
            return None

    async def _search_stock_image(self, query: str, fallback_query: str, orientation: str) -> Optional[Dict[str, Any]]:
        if self.pexels_key:
            url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query or fallback_query)}&orientation={orientation}&per_page=3"
            headers = {**self.headers, "Authorization": self.pexels_key}
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        photos = data.get("photos", [])
                        if photos:
                            photo = photos[0]
                            img_url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                            return {
                                "provider": "pexels_image_kenburns",
                                "url": img_url,
                                "is_image": True,
                                "width": photo.get("width", 1920),
                                "height": photo.get("height", 1080),
                                "keyword": query
                            }
            except Exception:
                pass
        return None

    def _generate_ai_image_fallback(self, query: str, aspect_ratio: str) -> Dict[str, Any]:
        """Free AI Image Generator (Pollinations Flux Engine) with Ken Burns motion."""
        clean_kw = re.sub(r'[^a-zA-Z0-9\s]', '', query).strip() or "cinematic futuristic visual"
        prompt = f"8k cinematic photorealistic master shot of {clean_kw}, octane render, dramatic volumetric lighting, highly detailed"
        
        w, h = (1920, 1080) if aspect_ratio == "16:9" else ((1080, 1920) if aspect_ratio == "9:16" else (1080, 1080))
        seed = random.randint(1000, 999999)
        encoded_prompt = urllib.parse.quote(prompt)
        ai_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={w}&height={h}&nologo=true&seed={seed}"

        return {
            "provider": "pollinations_ai_flux_kenburns",
            "url": ai_url,
            "is_image": True,
            "width": w,
            "height": h,
            "keyword": query,
            "author": "Pollinations Flux AI"
        }
