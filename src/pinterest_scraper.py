import asyncio
import re
import urllib.parse
from typing import Optional, Dict, Any, List
import httpx

class PinterestScraper:
    def __init__(self, headless: bool = True, timeout_ms: int = 12000):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

    async def scrape_video(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Production-grade Pinterest video scraper:
        1. Launches Playwright headless browser with network stream interception.
        2. Scrapes dynamically rendered video elements & v1.pinimg.com video CDN URLs.
        3. Falls back to direct HTTP pin parser if headless browser times out.
        """
        clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', query).strip()
        search_term = f"{clean_query} aesthetic 4k broll video"
        
        # 1. Try Playwright Stealth Interceptor
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                )
                context = await browser.new_context(
                    user_agent=self.user_agent,
                    viewport={"width": 1280, "height": 800}
                )
                page = await context.new_page()

                captured_videos: List[str] = []

                # Intercept network media streams
                page.on("response", lambda resp: self._check_response(resp, captured_videos))

                url = f"https://www.pinterest.com/search/pins/?q={urllib.parse.quote(search_term)}&rs=typed"
                try:
                    await page.goto(url, timeout=self.timeout_ms, wait_until="domcontentloaded")
                    await page.wait_for_timeout(2000)
                except Exception:
                    pass

                # Scan DOM for video tags
                video_elements = await page.query_selector_all("video")
                for v in video_elements:
                    src = await v.get_attribute("src")
                    if src and ("pinimg.com" in src or src.endswith(".mp4")):
                        captured_videos.append(src)

                # Scan page content for direct video regex
                content = await page.content()
                matches = re.findall(r'https://v1\.pinimg\.com/videos/mc/[^\"]+\.mp4', content)
                captured_videos.extend(matches)

                await browser.close()

                if captured_videos:
                    chosen_url = captured_videos[0]
                    return {
                        "provider": "pinterest_playwright",
                        "url": chosen_url,
                        "is_image": False,
                        "width": 1080,
                        "height": 1920,
                        "keyword": query,
                        "author": "Pinterest Aesthetic Creator"
                    }
        except Exception as e:
            print(f"[DEBUG] Playwright scraper fallback triggered: {e}")

        # 2. Fast HTTP Fallback
        return await self._http_fallback(query)

    def _check_response(self, response, captured_videos: List[str]):
        try:
            url = response.url
            if "v1.pinimg.com/videos/" in url and (".mp4" in url or ".m3u8" in url):
                if url not in captured_videos:
                    captured_videos.append(url)
        except Exception:
            pass

    async def _http_fallback(self, query: str) -> Optional[Dict[str, Any]]:
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        url = f"https://www.pinterest.com/search/pins/?q={urllib.parse.quote(query + ' video aesthetic')}&rs=typed"
        try:
            async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    matches = re.findall(r'https://v1\.pinimg\.com/videos/mc/[^\"]+\.mp4', resp.text)
                    if matches:
                        return {
                            "provider": "pinterest_fast",
                            "url": matches[0],
                            "is_image": False,
                            "width": 1080,
                            "height": 1920,
                            "keyword": query,
                            "author": "Pinterest Creator"
                        }
        except Exception:
            pass
        return None
