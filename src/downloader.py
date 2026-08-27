import os
import httpx
import asyncio
from pathlib import Path
from typing import Optional, Callable, Dict, Any

class Downloader:
    def __init__(self, concurrency: int = 5):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "*/*"
        }

    async def download_file(
        self,
        url: str,
        dest_path: Path,
        progress_cb: Optional[Callable[[str, float], None]] = None
    ) -> Path:
        """
        Downloads a media stream asynchronously with retry and size checks.
        """
        dest_path = Path(dest_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        async with self.semaphore:
            for attempt in range(3):
                try:
                    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                        async with client.stream("GET", url, headers=self.headers) as response:
                            if response.status_code != 200:
                                raise ValueError(f"HTTP error {response.status_code} downloading {url}")

                            total_bytes = int(response.headers.get("content-length", 0))
                            downloaded_bytes = 0

                            with open(dest_path, "wb") as f:
                                async for chunk in response.aiter_bytes(chunk_size=65536):
                                    f.write(chunk)
                                    downloaded_bytes += len(chunk)
                                    if progress_cb and total_bytes > 0:
                                        pct = round((downloaded_bytes / total_bytes) * 100, 1)
                                        progress_cb(dest_path.name, pct)

                    # Verify non-empty file
                    if dest_path.exists() and os.path.getsize(dest_path) > 1024:
                        return dest_path
                except Exception as e:
                    print(f"[WARN] Download attempt {attempt + 1} failed for {url}: {e}")
                    await asyncio.sleep(1.0)

            raise RuntimeError(f"Failed to download media file after 3 attempts: {url}")
