import re
import urllib.parse
import httpx
from typing import Dict, Any, Optional, List
from src.config import Config

class StockSearcher:
    def __init__(
        self,
        pexels_key: Optional[str] = None,
        pixabay_key: Optional[str] = None
    ):
        self.pexels_key = pexels_key or Config.PEXELS_API_KEY
        self.pixabay_key = pixabay_key or Config.PIXABAY_API_KEY
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    async def find_stock(
        self,
        keyword: str,
        fallback_keyword: str = "",
        aspect_ratio: str = "16:9",
        quality: str = "1080p"
    ) -> Dict[str, Any]:
        """
        Unified multi-tier stock searcher:
        1. Pexels Video API (filtered by aspect ratio)
        2. Pixabay Video API
        3. Pinterest Scraper
        4. High-Res Image (for 3.0s Ken Burns Pan & Zoom fallback)
        """
        orientation = Config.RESOLUTIONS.get(aspect_ratio, {}).get("orientation", "landscape")
        
        # 1. Try Pexels Video
        if self.pexels_key:
            res = await self._search_pexels_video(keyword, orientation, quality)
            if not res and fallback_keyword:
                res = await self._search_pexels_video(fallback_keyword, orientation, quality)
            if res:
                return res

        # 2. Try Pixabay Video
        if self.pixabay_key:
            res = await self._search_pixabay_video(keyword, orientation)
            if not res and fallback_keyword:
                res = await self._search_pixabay_video(fallback_keyword, orientation)
            if res:
                return res

        # 3. Try Pinterest Video Scraper
        res = await self._scrape_pinterest_video(keyword)
        if not res and fallback_keyword:
            res = await self._scrape_pinterest_video(fallback_keyword)
        if res:
            return res

        # 4. Fallback to 4K Stock Image (for Ken Burns 3s Video Generator)
        img_res = await self._search_stock_image(keyword, fallback_keyword, orientation)
        if img_res:
            return img_res

        # 5. Last-resort fallback to public sample
        return {
            "provider": "sample_fallback",
            "url": "https://assets.mixkit.co/videos/preview/mixkit-software-developer-working-on-code-screen-close-up-34388-large.mp4",
            "is_image": False,
            "width": 1920,
            "height": 1080,
            "keyword": keyword
        }

    async def _search_pexels_video(self, query: str, orientation: str, quality: str) -> Optional[Dict[str, Any]]:
        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation={orientation}&per_page=5"
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
                
                # Pick the best matching video file
                video = videos[0]
                video_files = video.get("video_files", [])
                if not video_files:
                    return None

                # Find file matching requested quality
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

    async def _search_pixabay_video(self, query: str, orientation: str) -> Optional[Dict[str, Any]]:
        url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={urllib.parse.quote(query)}&per_page=5"
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

    async def _scrape_pinterest_video(self, query: str) -> Optional[Dict[str, Any]]:
        url = f"https://www.pinterest.com/search/pins/?q={urllib.parse.quote(query + ' video aesthetic')}&rs=typed"
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code != 200:
                    return None
                
                # Search for direct mp4 links in HTML
                mp4_matches = re.findall(r'https://v1\.pinimg\.com/videos/mc/[^\"]+\.mp4', resp.text)
                if mp4_matches:
                    return {
                        "provider": "pinterest",
                        "url": mp4_matches[0],
                        "is_image": False,
                        "width": 1080,
                        "height": 1920,
                        "keyword": query,
                        "author": "Pinterest Creator"
                    }
        except Exception as e:
            print(f"[WARN] Pinterest scraper error: {e}")
        return None

    async def _search_stock_image(self, query: str, fallback_query: str, orientation: str) -> Optional[Dict[str, Any]]:
        """Searches high-res stock photo for Ken Burns 3s video conversion."""
        # Try Pexels Photo API
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

        # Unsplash Public Source fallback
        clean_q = urllib.parse.quote(query.replace(" ", "-"))
        unsplash_url = f"https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=80"
        return {
            "provider": "unsplash_image_kenburns",
            "url": unsplash_url,
            "is_image": True,
            "width": 1920,
            "height": 1080,
            "keyword": query
        }
