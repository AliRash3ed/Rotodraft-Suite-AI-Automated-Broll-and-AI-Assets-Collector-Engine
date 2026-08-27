import os
import sys
import asyncio
import unittest
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.config import Config
from src.tts_engine import TTSEngine
from src.ai_engine import AIEngine
from src.stock_searcher import StockSearcher
from src.downloader import Downloader
from src.video_processor import VideoProcessor
from src.video_merger import VideoMerger
from src.timeline_exporter import TimelineExporter
from src.voices_catalog import VoiceCatalog
from src.lead_manager import LeadManager
from src.pinterest_scraper import PinterestScraper
from src.bgm_engine import BGMEngine
from src.subtitle_engine import SubtitleEngine

class TestRotoDraftSuite(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = Config.DOWNLOADS_DIR / "_unit_test_run"
        cls.test_dir.mkdir(parents=True, exist_ok=True)

    async def test_01_voice_catalog_and_language_detection(self):
        """Test full 300+ Edge-TTS voice list, recommended badges & auto-detect."""
        voices = await VoiceCatalog.get_all_voices()
        self.assertGreater(len(voices), 100, f"Expected 100+ voices, got {len(voices)}")
        
        rec_count = sum(1 for v in voices if v["is_recommended"])
        self.assertGreater(rec_count, 10, "Expected at least 10 recommended voices")

        urdu_voice = VoiceCatalog.detect_best_voice("یہ ایک اردو ٹیسٹ سکرپٹ ہے")
        self.assertEqual(urdu_voice, "ur-PK-AsadNeural")

        hindi_voice = VoiceCatalog.detect_best_voice("यह एक हिंदी वीडियो स्क्रिप्ट है")
        self.assertEqual(hindi_voice, "hi-IN-MadhurNeural")

        en_voice = VoiceCatalog.detect_best_voice("In today's fast moving world of AI")
        self.assertEqual(en_voice, "en-US-ChristopherNeural")

        print(f"[PASS] Voice Catalog: Loaded {len(voices)} voices ({rec_count} recommended) + Auto-detect verified")

    async def test_02_lead_manager_and_privacy_db(self):
        """Test private SQLite lead storage and analytics calculation."""
        lm = LeadManager()
        res = await lm.save_lead("test.creator@gmail.com", "Test Creator", video_count=1)
        self.assertTrue(res["success"])
        
        lm.record_whatsapp_click("test.creator@gmail.com")
        lm.record_video_generation("Test_Proj", "full", "16:9", "Cinematic", "en-US-ChristopherNeural", 30.0, 10)
        
        stats = lm.get_dashboard_stats()
        self.assertGreaterEqual(stats["total_leads"], 1)
        self.assertGreaterEqual(stats["whatsapp_conversions"], 1)
        
        csv_export = lm.export_leads_csv()
        self.assertIn("test.creator@gmail.com", csv_export)
        print(f"[PASS] Lead Manager: SQLite DB operational, Stats calculated, CSV exported")

    async def test_03_tts_engine_and_subtitles(self):
        """Test Edge-TTS synthesis and SRT subtitle output with speed rate."""
        tts = TTSEngine()
        out_audio = self.test_dir / "test_voice.mp3"
        res = await tts.generate_speech(
            text="Welcome to RotoDraft Suite, the AI powered stock media collector.",
            output_path=out_audio,
            voice="en-US-ChristopherNeural",
            rate="+10%"
        )
        self.assertTrue(out_audio.exists(), "Audio file must exist")
        self.assertTrue(Path(res["srt_path"]).exists(), "SRT subtitle file must exist")
        
        # Test ASS conversion
        ass_out = self.test_dir / "test_subtitles.ass"
        SubtitleEngine.srt_to_ass(res["srt_path"], ass_out, style_id="hormozi", aspect_ratio="16:9")
        self.assertTrue(ass_out.exists())
        self.assertGreater(ass_out.stat().st_size, 50)
        print(f"[PASS] TTS Engine & ASS Subtitles: Generated audio + Hormozi ASS subtitle")

    async def test_04_ai_engine_and_viral_enhancers(self):
        """Test AI 1-Shot script decomposition, rewriter, and viral metadata generation."""
        ai = AIEngine()
        script = "In the modern financial world, algorithmic trading accounts for over 70% of market volume. Neural networks analyze stock price movements in fractions of a second."
        
        clips = await ai.analyze_script(script, duration_seconds=6.0, clip_duration=3.0)
        self.assertEqual(len(clips), 2)
        
        rewritten = await ai.rewrite_script("AI is replacing traders on Wall Street", style="viral_hook")
        self.assertIn("enhanced_script", rewritten)
        
        meta = await ai.generate_viral_metadata(script)
        self.assertEqual(len(meta["titles"]), 5)
        print(f"[PASS] AI Engine: Decomposed {len(clips)} scenes, Rewrote script, Generated 5 Viral Titles & SEO Metadata")

    async def test_05_pinterest_and_stock_search_flux_fallback(self):
        """Test stock search with integrated Pinterest scraper and Pollinations Flux AI fallback."""
        stock = StockSearcher()
        res = await stock.find_stock("cyberpunk holographic city", aspect_ratio="16:9", page=1)
        self.assertIn("url", res)
        self.assertTrue(res["url"].startswith("http"))
        print(f"[PASS] Stock Searcher: Sourced via provider '{res['provider']}' -> URL: {res['url'][:60]}...")

    async def test_06_bgm_engine_and_color_grading(self):
        """Test BGM engine and color grading video processing."""
        tracks = BGMEngine.get_available_tracks()
        self.assertGreaterEqual(len(tracks), 5)
        
        processor = VideoProcessor()
        from PIL import Image
        img_path = self.test_dir / "sample_img.jpg"
        img = Image.new("RGB", (1920, 1080), color=(30, 60, 90))
        img.save(img_path)

        out_clip = self.test_dir / "01_sample_clip.mp4"
        processor.process_clip(
            input_path=img_path,
            output_path=out_clip,
            duration=3.0,
            aspect_ratio="16:9",
            quality="720p",
            color_filter="teal_orange",
            is_image=True
        )
        self.assertTrue(out_clip.exists())

        merger = VideoMerger()
        voice_audio = self.test_dir / "test_voice.mp3"
        master_out = self.test_dir / "Full_Video_Master.mp4"

        # Merge with voice
        merger.merge_clips(
            clip_paths=[out_clip, out_clip],
            output_master_path=master_out,
            audio_path=voice_audio
        )
        self.assertTrue(master_out.exists())
        print(f"[PASS] Video Processor & Merger: Rendered Master Video with Teal & Orange color grade ({os.path.getsize(master_out)} bytes)")

if __name__ == "__main__":
    unittest.main()
