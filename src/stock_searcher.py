import re
import urllib.parse
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional, List
from src.config import Config
from src.logger import logger
from src.pinterest_scraper import PinterestScraper

class StockSearcher:
    """
    Universal Multi-Platform Stock Media Retriever & Scraper.
    Supports:
    - Pexels (API & Scraper)
    - Pixabay (API)
    - Unsplash (API & Scraper)
    - Pinterest (Aesthetic 9:16 & 1080p Video Scraper)
    - Storyblocks (API & Direct Search)
    - Coverr.co (Free HD/4K Video CDN)
    - Mixkit.co (Envato Free Stock Video Library)
    - Videvo.net (Free Footage & Motion Graphics)
    - Wikimedia Commons (Public Domain Historical Archives)
    """

    def __init__(
        self,
        pexels_key: Optional[str] = None,
        pixabay_key: Optional[str] = None,
        unsplash_key: Optional[str] = None,
        storyblocks_key: Optional[str] = None,
        coverr_key: Optional[str] = None,
    ):
        Config.load_saved_settings()
        self.pexels_key = pexels_key or Config.PEXELS_API_KEY
        self.pixabay_key = pixabay_key or Config.PIXABAY_API_KEY
        self.unsplash_key = unsplash_key or Config.UNSPLASH_API_KEY
        self.storyblocks_key = storyblocks_key or Config.STORYBLOCKS_API_KEY
        self.coverr_key = coverr_key or Config.COVERR_API_KEY

        self.pexels_headers = {"Authorization": self.pexels_key} if self.pexels_key else {}
        self.unsplash_headers = {"Authorization": f"Client-ID {self.unsplash_key}"} if self.unsplash_key else {}
        self.pinterest = PinterestScraper()
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        if Config.HTTP_PROXY or Config.HTTPS_PROXY:
            proxies = {}
            if Config.HTTP_PROXY: proxies["http"] = Config.HTTP_PROXY
            if Config.HTTPS_PROXY: proxies["https"] = Config.HTTPS_PROXY
            self.session.proxies.update(proxies)

    def search_media_for_item(
        self,
        item: Dict[str, Any],
        quality: str = "1080p",
        aspect_ratio: str = "16:9",
        media_type: str = "videos",
        providers: Optional[List[str]] = None,
        enable_fallback: bool = True,
    ) -> Dict[str, Any]:
        Config.load_saved_settings()
        self.pexels_key = self.pexels_key or Config.PEXELS_API_KEY
        self.pixabay_key = self.pixabay_key or Config.PIXABAY_API_KEY
        self.unsplash_key = self.unsplash_key or Config.UNSPLASH_API_KEY
        self.storyblocks_key = self.storyblocks_key or Config.STORYBLOCKS_API_KEY
        self.coverr_key = self.coverr_key or Config.COVERR_API_KEY

        self.pexels_headers = {"Authorization": self.pexels_key} if self.pexels_key else {}
        self.unsplash_headers = {"Authorization": f"Client-ID {self.unsplash_key}"} if self.unsplash_key else {}

        keyword = item.get("keyword", "")
        fallback_keyword = item.get("fallback_keyword", "")
        orientation = Config.get_orientation_for_api(aspect_ratio)
        
        raw_provs = providers or ["pexels", "pixabay", "coverr", "mixkit", "storyblocks", "videvo", "unsplash", "pinterest", "wikimedia"]
        allowed_providers = []
        for rp in raw_provs:
            for piece in str(rp).split(","):
                p_clean = piece.strip().lower()
                if p_clean and p_clean not in allowed_providers:
                    allowed_providers.append(p_clean)

        logger.info(f"Searching stock for Clip #{item['index']:02d}: '{keyword}' (Type: {media_type}, AR: {aspect_ratio})...", "STOCK")

        media = None

        # 1. Search Videos
        if media_type in ["videos", "both"]:
            # Primary keyword video cascade
            for prov in allowed_providers:
                if media: break
                if prov == "pexels": media = self._search_pexels_video(keyword, quality, orientation)
                elif prov == "pixabay": media = self._search_pixabay_video(keyword, quality, orientation)
                elif prov == "coverr": media = self._search_coverr_video(keyword, quality)
                elif prov == "mixkit": media = self._search_mixkit_video(keyword, quality)
                elif prov == "storyblocks": media = self._search_storyblocks_video(keyword, quality)
                elif prov == "videvo": media = self._search_videvo_video(keyword, quality)
                elif prov == "pinterest":
                    pin_res = self.pinterest.search_pinterest(keyword, limit=3)
                    vids = [p for p in pin_res if "video_url" in p]
                    if vids: media = vids[0]
                elif prov == "wikimedia": media = self._search_wikimedia_media(keyword, media_type="video")

            # Fallback keyword video search
            if not media and enable_fallback and fallback_keyword:
                logger.warning(f"Clip #{item['index']:02d}: Trying fallback video keyword '{fallback_keyword}'...", "STOCK")
                for prov in allowed_providers:
                    if media: break
                    if prov == "pexels": media = self._search_pexels_video(fallback_keyword, quality, orientation)
                    elif prov == "pixabay": media = self._search_pixabay_video(fallback_keyword, quality, orientation)
                    elif prov == "coverr": media = self._search_coverr_video(fallback_keyword, quality)
                    elif prov == "mixkit": media = self._search_mixkit_video(fallback_keyword, quality)
                    elif prov == "storyblocks": media = self._search_storyblocks_video(fallback_keyword, quality)

        # 2. Search Photos (for Photo Mode or as Ken Burns fallback)
        if not media and (media_type in ["photos", "both"] or enable_fallback):
            logger.info(f"Clip #{item['index']:02d}: Searching high-res stock photo for '{keyword}'...", "STOCK")
            for prov in allowed_providers:
                if media: break
                if prov == "pexels": media = self._search_pexels_photo(keyword, orientation)
                elif prov == "pixabay": media = self._search_pixabay_photo(keyword, orientation)
                elif prov == "unsplash": media = self._search_unsplash_photo(keyword, orientation)
                elif prov == "storyblocks": media = self._search_storyblocks_photo(keyword)
                elif prov == "pinterest":
                    pin_res = self.pinterest.search_pinterest(keyword, limit=3)
                    photos = [p for p in pin_res if "photo_url" in p]
                    if photos: media = photos[0]
                elif prov == "wikimedia": media = self._search_wikimedia_media(keyword, media_type="photo")

            if not media and enable_fallback and fallback_keyword:
                for prov in allowed_providers:
                    if media: break
                    if prov == "unsplash": media = self._search_unsplash_photo(fallback_keyword, orientation)
                    elif prov == "pexels": media = self._search_pexels_photo(fallback_keyword, orientation)
                    elif prov == "pixabay": media = self._search_pixabay_photo(fallback_keyword, orientation)

        result = dict(item)
        if media:
            result.update(media)
            result["found"] = True
            is_photo = "photo_url" in media and "video_url" not in media
            result["is_photo_fallback"] = is_photo
            if is_photo:
                result["video_url"] = media["photo_url"]
            logger.success(
                f"Found Clip #{item['index']:02d} from [{media.get('provider', '').upper()}] -> '{keyword}'",
                "STOCK"
            )
        else:
            result["found"] = False
            result["error"] = f"No media found across {', '.join(allowed_providers)} for '{keyword}'"
            logger.warning(f"Clip #{item['index']:02d} Not Found: '{keyword}'", "STOCK")

        return result

    def search_batch(
        self,
        items: List[Dict[str, Any]],
        quality: str = "1080p",
        aspect_ratio: str = "16:9",
        media_type: str = "videos",
        providers: Optional[List[str]] = None,
        enable_fallback: bool = True,
        max_workers: int = 6,
    ) -> List[Dict[str, Any]]:
        results_map = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(
                    self.search_media_for_item,
                    item,
                    quality,
                    aspect_ratio,
                    media_type,
                    providers,
                    enable_fallback,
                ): item["index"]
                for item in items
            }
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results_map[idx] = future.result()
                except Exception as e:
                    logger.error(f"Search exception on Clip #{idx:02d}: {str(e)}", "STOCK")
                    orig = next((i for i in items if i["index"] == idx), {"index": idx})
                    results_map[idx] = dict(orig, found=False, error=str(e))

        return [results_map[i["index"]] for i in items]

    # ── 1. PEXELS ──
    def _search_pexels_video(self, keyword: str, quality: str = "1080p", orientation: str = "landscape") -> Optional[Dict[str, Any]]:
        if not self.pexels_key: return None
        target_width = 1280 if quality == "720p" else (3840 if quality == "4K" else 1920)
        for ori in [orientation, ""]:
            try:
                ori_param = f"&orientation={ori}" if ori else ""
                url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(keyword)}&per_page=5{ori_param}"
                resp = self.session.get(url, headers=self.pexels_headers, timeout=12)
                if resp.status_code == 200:
                    videos = resp.json().get("videos", [])
                    if videos:
                        v = videos[0]
                        files = v.get("video_files", [])
                        if files:
                            # Pick the file closest to user-selected target width (e.g. 1280 for 720p, 1920 for 1080p)
                            best = min(files, key=lambda f: abs(f.get("width", 1920) - target_width))
                            return {
                                "provider": "pexels",
                                "media_id": str(v.get("id")),
                                "video_url": best.get("link"),
                                "thumbnail_url": v.get("image"),
                                "duration": v.get("duration", 3.0),
                                "width": best.get("width", target_width),
                                "height": best.get("height", 1080),
                            }
            except Exception:
                pass
        return None

    def _search_pexels_photo(self, keyword: str, orientation: str = "landscape") -> Optional[Dict[str, Any]]:
        if not self.pexels_key: return None
        for ori in [orientation, ""]:
            try:
                ori_param = f"&orientation={ori}" if ori else ""
                url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(keyword)}&per_page=5{ori_param}"
                resp = self.session.get(url, headers=self.pexels_headers, timeout=12)
                if resp.status_code == 200:
                    photos = resp.json().get("photos", [])
                    if photos:
                        p = photos[0]
                        src = p.get("src", {})
                        return {
                            "provider": "pexels",
                            "media_id": str(p.get("id")),
                            "photo_url": src.get("large2x") or src.get("original") or src.get("large"),
                            "thumbnail_url": src.get("medium"),
                            "width": p.get("width", 1920),
                            "height": p.get("height", 1080),
                        }
            except Exception:
                pass
        return None

    # ── 2. PIXABAY ──
    def _search_pixabay_video(self, keyword: str, quality: str = "1080p", orientation: str = "landscape") -> Optional[Dict[str, Any]]:
        if not self.pixabay_key: return None
        try:
            url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={urllib.parse.quote(keyword)}&per_page=5"
            resp = self.session.get(url, timeout=12)
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                if hits:
                    h = hits[0]
                    vids = h.get("videos", {})
                    if quality == "720p":
                        chosen = vids.get("medium") or vids.get("small") or vids.get("large")
                    elif quality == "4K":
                        chosen = vids.get("large") or vids.get("medium")
                    else:
                        chosen = vids.get("large") or vids.get("medium") or vids.get("small")
                    if chosen and chosen.get("url"):
                        return {
                            "provider": "pixabay",
                            "media_id": str(h.get("id")),
                            "video_url": chosen.get("url"),
                            "thumbnail_url": f"https://i.vimeocdn.com/video/{h.get('picture_id')}_640x360.jpg",
                            "duration": h.get("duration", 3.0),
                            "width": chosen.get("width", 1920),
                            "height": chosen.get("height", 1080),
                        }
        except Exception:
            pass
        return None

    def _search_pixabay_photo(self, keyword: str, orientation: str = "landscape") -> Optional[Dict[str, Any]]:
        if not self.pixabay_key: return None
        try:
            url = f"https://pixabay.com/api/?key={self.pixabay_key}&q={urllib.parse.quote(keyword)}&image_type=photo&per_page=5"
            resp = self.session.get(url, timeout=12)
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                if hits:
                    h = hits[0]
                    return {
                        "provider": "pixabay",
                        "media_id": str(h.get("id")),
                        "photo_url": h.get("largeImageURL") or h.get("webformatURL"),
                        "thumbnail_url": h.get("previewURL"),
                        "width": h.get("imageWidth", 1920),
                        "height": h.get("imageHeight", 1080),
                    }
        except Exception:
            pass
        return None

    # ── 3. COVERR.CO (FREE 1080P/4K FOOTAGE) ──
    def _search_coverr_video(self, keyword: str, quality: str = "1080p") -> Optional[Dict[str, Any]]:
        try:
            # Direct search on Coverr's public discovery catalog
            url = f"https://api.coverr.co/videos?query={urllib.parse.quote(keyword)}&page_size=5"
            headers = {}
            if self.coverr_key:
                headers["Authorization"] = f"Bearer {self.coverr_key}"
            resp = self.session.get(url, headers=headers, timeout=12)
            if resp.status_code == 200:
                results = resp.json().get("hits") or resp.json().get("videos") or []
                if results:
                    v = results[0]
                    v_url = v.get("urls", {}).get("mp4") or v.get("video_url") or v.get("urls", {}).get("mp4_download")
                    if v_url:
                        return {
                            "provider": "coverr",
                            "media_id": str(v.get("id", "coverr_1")),
                            "video_url": v_url,
                            "thumbnail_url": v.get("thumbnail_url") or v.get("poster"),
                            "duration": v.get("duration", 3.0),
                            "width": 1920,
                            "height": 1080
                        }
        except Exception:
            pass
        return None

    # ── 4. MIXKIT.CO (ENVATO FREE STOCK B-ROLL) ──
    def _search_mixkit_video(self, keyword: str, quality: str = "1080p") -> Optional[Dict[str, Any]]:
        try:
            # Mixkit query API
            query_slug = re.sub(r"[^\w\s-]", "", keyword).strip().replace(" ", "-")
            url = f"https://mixkit.co/api/v1/search/free-stock-video/{query_slug}/"
            resp = self.session.get(url, timeout=12)
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                if items:
                    it = items[0]
                    v_url = it.get("video_url") or it.get("download_url") or it.get("preview_video_url")
                    if v_url:
                        return {
                            "provider": "mixkit",
                            "media_id": str(it.get("id", "mixkit_1")),
                            "video_url": v_url,
                            "thumbnail_url": it.get("thumbnail_url"),
                            "duration": 3.0,
                            "width": 1920,
                            "height": 1080
                        }
        except Exception:
            pass
        return None

    # ── 5. STORYBLOCKS (API & SEARCH) ──
    def _search_storyblocks_video(self, keyword: str, quality: str = "1080p") -> Optional[Dict[str, Any]]:
        if not self.storyblocks_key and not Config.STORYBLOCKS_ENABLED:
            return None
        try:
            url = f"https://api.graphicstock.com/api/v2/videos/search?keywords={urllib.parse.quote(keyword)}&num_results=5"
            headers = {"Authorization": f"Basic {self.storyblocks_key}"} if self.storyblocks_key else {}
            resp = self.session.get(url, headers=headers, timeout=12)
            if resp.status_code == 200:
                info = resp.json().get("info", []) or resp.json().get("results", [])
                if info:
                    first = info[0]
                    return {
                        "provider": "storyblocks",
                        "media_id": str(first.get("id", "sb_1")),
                        "video_url": first.get("preview_url") or first.get("download_url"),
                        "thumbnail_url": first.get("thumbnail_url"),
                        "duration": first.get("duration", 3.0),
                        "width": 1920,
                        "height": 1080
                    }
        except Exception:
            pass
        return None

    def _search_storyblocks_photo(self, keyword: str) -> Optional[Dict[str, Any]]:
        if not self.storyblocks_key and not Config.STORYBLOCKS_ENABLED:
            return None
        try:
            url = f"https://api.graphicstock.com/api/v2/images/search?keywords={urllib.parse.quote(keyword)}&num_results=5"
            headers = {"Authorization": f"Basic {self.storyblocks_key}"} if self.storyblocks_key else {}
            resp = self.session.get(url, headers=headers, timeout=12)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    first = results[0]
                    return {
                        "provider": "storyblocks",
                        "media_id": str(first.get("id", "sb_img_1")),
                        "photo_url": first.get("preview_url") or first.get("download_url"),
                        "thumbnail_url": first.get("thumbnail_url"),
                        "width": 1920,
                        "height": 1080
                    }
        except Exception:
            pass
        return None

    # ── 6. VIDEVO.NET (FREE FOOTAGE) ──
    def _search_videvo_video(self, keyword: str, quality: str = "1080p") -> Optional[Dict[str, Any]]:
        try:
            url = f"https://www.videvo.net/api/search/?query={urllib.parse.quote(keyword)}&type=video"
            resp = self.session.get(url, timeout=12)
            if resp.status_code == 200:
                data = resp.json().get("videos", [])
                if data:
                    v = data[0]
                    return {
                        "provider": "videvo",
                        "media_id": str(v.get("id", "vd_1")),
                        "video_url": v.get("preview_url") or v.get("clip_url"),
                        "thumbnail_url": v.get("thumbnail"),
                        "duration": v.get("duration", 3.0),
                        "width": 1920,
                        "height": 1080
                    }
        except Exception:
            pass
        return None

    # ── 7. UNSPLASH ──
    def _search_unsplash_photo(self, keyword: str, orientation: str = "landscape") -> Optional[Dict[str, Any]]:
        if self.unsplash_key:
            try:
                url = f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(keyword)}&per_page=5&orientation={orientation}"
                resp = self.session.get(url, headers=self.unsplash_headers, timeout=12)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        p = results[0]
                        urls = p.get("urls", {})
                        return {
                            "provider": "unsplash",
                            "media_id": str(p.get("id")),
                            "photo_url": urls.get("full") or urls.get("regular"),
                            "thumbnail_url": urls.get("small"),
                            "width": p.get("width", 1920),
                            "height": p.get("height", 1080),
                        }
            except Exception:
                pass

        # Unsplash Scraper fallback
        try:
            url = f"https://unsplash.com/napi/search/photos?query={urllib.parse.quote(keyword)}&per_page=5"
            resp = self.session.get(url, timeout=12)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    p = results[0]
                    urls = p.get("urls", {})
                    return {
                        "provider": "unsplash",
                        "media_id": str(p.get("id")),
                        "photo_url": urls.get("regular") or urls.get("small"),
                        "thumbnail_url": urls.get("thumb"),
                        "width": 1920,
                        "height": 1080,
                    }
        except Exception:
            pass
        return None

    # ── 8. WIKIMEDIA COMMONS (PUBLIC DOMAIN ARCHIVES) ──
    def _search_wikimedia_media(self, keyword: str, media_type: str = "video") -> Optional[Dict[str, Any]]:
        try:
            url = (
                f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
                f"&gsrsearch={urllib.parse.quote(keyword)}&gsrnamespace=6&prop=imageinfo"
                f"&iiprop=url|size|mime&format=json"
            )
            resp = self.session.get(url, timeout=12)
            if resp.status_code == 200:
                pages = resp.json().get("query", {}).get("pages", {})
                for _, page in pages.items():
                    infos = page.get("imageinfo", [])
                    if infos:
                        info = infos[0]
                        mime = info.get("mime", "")
                        media_url = info.get("url", "")
                        if media_type == "video" and "video" in mime or media_url.endswith((".mp4", ".webm", ".ogv")):
                            return {
                                "provider": "wikimedia",
                                "media_id": str(page.get("pageid", "wiki_1")),
                                "video_url": media_url,
                                "thumbnail_url": info.get("thumburl") or media_url,
                                "duration": 3.0,
                                "width": info.get("width", 1920),
                                "height": info.get("height", 1080)
                            }
                        elif media_type == "photo" and "image" in mime:
                            return {
                                "provider": "wikimedia",
                                "media_id": str(page.get("pageid", "wiki_img_1")),
                                "photo_url": media_url,
                                "thumbnail_url": info.get("thumburl") or media_url,
                                "width": info.get("width", 1920),
                                "height": info.get("height", 1080)
                            }
        except Exception:
            pass
        return None
