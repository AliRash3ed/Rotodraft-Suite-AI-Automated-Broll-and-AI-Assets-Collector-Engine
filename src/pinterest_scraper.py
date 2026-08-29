import re
import urllib.parse
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.config import Config
from src.logger import logger

class PinterestScraper:
    """
    Pinterest Aesthetic Media & Video Scraper.
    Supports session cookies, public JSON Resource queries, and direct high-res media extraction.
    """

    def __init__(self, session_cookie: Optional[str] = None):
        Config.load_saved_settings()
        self.session_cookie = session_cookie or Config.PINTEREST_SESSION_COOKIE
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*, q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "X-Pinterest-AppState": "active",
        }
        if self.session_cookie:
            self.headers["Cookie"] = self.session_cookie

    def search_pinterest(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        clean = re.sub(r"[^\w\s]", " ", query).strip()
        if not clean:
            return []

        logger.info(f"Searching Pinterest for aesthetic media: '{clean}'...", "PINTEREST")
        encoded = urllib.parse.quote_plus(clean)
        results = []

        # 1. BaseSearchResource with official app headers & optional session cookie
        try:
            url = (
                f"https://www.pinterest.com/resource/BaseSearchResource/get/?"
                f"source_url=%2Fsearch%2Fpins%2F%3Fq%3D{encoded}&"
                f"data=%7B%22options%22%3A%7B%22isPrefetch%22%3Afalse%2C%22query%22%3A%22{encoded}%22%2C%22scope%22%3A%22pins%22%2C%22no_fetch_context_on_resource%22%3Afalse%7D%2C%22context%22%3A%7B%7D%7D"
            )
            r = self.session.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                items = data.get("resource_response", {}).get("data", {}).get("results", [])
                for item in items:
                    pin_id = str(item.get("id", ""))
                    videos = item.get("videos", {})
                    v_list = videos.get("video_list", {}) if videos else {}
                    video_url = None
                    for k in ["V_720P", "V_EXP7", "V_EXP6", "V_HLSV4", "V_HLSV3"]:
                        if k in v_list and v_list[k].get("url"):
                            candidate = v_list[k]["url"]
                            if ".mp4" in candidate:
                                video_url = candidate
                                break

                    images = item.get("images", {})
                    thumb = (images.get("orig") or images.get("736x") or images.get("236x") or {}).get("url", "")
                    orig_photo = thumb.replace("/236x/", "/originals/").replace("/736x/", "/originals/").replace("/564x/", "/originals/")

                    if video_url:
                        results.append({
                            "provider": "pinterest",
                            "media_id": f"pin_{pin_id}",
                            "video_url": video_url,
                            "thumbnail_url": thumb,
                            "duration": 5.0,
                            "width": 1080,
                            "height": 1920,
                        })
                    elif orig_photo:
                        results.append({
                            "provider": "pinterest",
                            "media_id": f"pin_img_{pin_id}",
                            "photo_url": orig_photo,
                            "thumbnail_url": thumb,
                            "width": 1080,
                            "height": 1920,
                        })

                    if len(results) >= limit:
                        break
        except Exception as e:
            logger.warning(f"Pinterest Search note: {str(e)}", "PINTEREST")

        if results:
            logger.success(f"Found {len(results)} Pinterest aesthetic assets for '{clean}'", "PINTEREST")
        else:
            logger.info(f"Pinterest query '{clean}' returned 0 direct hits (Protected by login gate). Pipeline automatically utilizing remaining stock vaults.", "PINTEREST")

        return results
