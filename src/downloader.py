import os
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional
from src.config import Config
from src.logger import logger

class MediaDownloader:
    def __init__(self, max_parallel: Optional[int] = None):
        self.max_parallel = max_parallel or Config.MAX_PARALLEL_DOWNLOADS

    def download_single(
        self,
        item: Dict[str, Any],
        raw_dir: Path,
        timeout: int = 45,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        result = dict(item)
        video_url = item.get("video_url") or item.get("photo_url")
        if not item.get("found") or not video_url:
            result["download_success"] = False
            result["download_error"] = "No valid media URL found."
            return result

        idx = item["index"]
        is_photo = item.get("is_photo_fallback") or item.get("provider", "").endswith("_photo")
        ext = ".jpg" if is_photo else ".mp4"
        raw_filename = f"raw_{idx:03d}{ext}"
        raw_path = raw_dir / raw_filename
        partial_path = raw_dir / f"{raw_filename}.partial"

        # Check if already downloaded (Resume capability)
        if raw_path.exists() and raw_path.stat().st_size > 1000:
            result["download_success"] = True
            result["raw_path"] = str(raw_path.resolve())
            result["raw_filename"] = raw_filename
            result["file_size_bytes"] = raw_path.stat().st_size
            logger.info(f"Clip #{idx:02d} already downloaded (Resuming)...", "DOWNLOAD")
            return result

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Downloading Clip #{idx:02d} from [{item.get('provider', '').upper()}] (Attempt {attempt}/{max_retries})...", "DOWNLOAD")
                with requests.get(video_url, headers=headers, stream=True, timeout=timeout) as r:
                    r.raise_for_status()
                    with open(partial_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024 * 256):
                            if chunk:
                                f.write(chunk)

                if partial_path.exists() and partial_path.stat().st_size > 500:
                    if raw_path.exists():
                        raw_path.unlink(missing_ok=True)
                    partial_path.rename(raw_path)
                    
                    result["download_success"] = True
                    result["raw_path"] = str(raw_path.resolve())
                    result["raw_filename"] = raw_filename
                    result["file_size_bytes"] = raw_path.stat().st_size
                    mb = round(raw_path.stat().st_size / (1024 * 1024), 2)
                    logger.success(f"Clip #{idx:02d} Download complete ({mb} MB) -> {raw_filename}", "DOWNLOAD")
                    return result
                else:
                    raise IOError("Downloaded file is empty or corrupted.")

            except Exception as e:
                logger.warning(f"Clip #{idx:02d} Download error (attempt {attempt}): {str(e)}", "DOWNLOAD")
                if partial_path.exists():
                    partial_path.unlink(missing_ok=True)
                if attempt < max_retries:
                    time.sleep(2 * attempt)
                else:
                    result["download_success"] = False
                    result["download_error"] = str(e)

        return result

    def download_batch(
        self,
        items: List[Dict[str, Any]],
        raw_dir: Path,
        on_progress: Optional[Callable[[int, int, Dict[str, Any]], None]] = None,
    ) -> List[Dict[str, Any]]:
        raw_dir.mkdir(parents=True, exist_ok=True)
        results_map = {}
        total = len(items)
        completed_count = 0

        logger.info(f"Starting parallel download stream ({self.max_parallel} workers) for {total} assets...", "DOWNLOAD")

        with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            future_to_item = {
                executor.submit(self.download_single, item, raw_dir): item
                for item in items
            }

            for future in as_completed(future_to_item):
                item = future_to_item[future]
                completed_count += 1
                try:
                    res = future.result()
                    results_map[res["index"]] = res
                except Exception as e:
                    results_map[item["index"]] = {
                        **item,
                        "download_success": False,
                        "download_error": str(e),
                    }

                if on_progress:
                    on_progress(completed_count, total, results_map[item["index"]])

        success_count = sum(1 for r in results_map.values() if r.get("download_success"))
        logger.success(f"Batch Download complete: {success_count}/{total} files saved to {raw_dir.name}/", "DOWNLOAD")
        return [results_map[item["index"]] for item in items if item["index"] in results_map]
