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
from src.pipeline import RotoDraftPipeline

class TestRotoDraftSuite(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = Config.DOWNLOADS_DIR / "_unit_test_run"
        cls.test_dir.mkdir(parents=True, exist_ok=True)

    async def test_01_tts_engine(self):
        """Test Edge-TTS synthesis and SRT subtitle output."""
        tts = TTSEngine()
        out_audio = self.test_dir / "test_voice.mp3"
        res = await tts.generate_speech(
            text="Welcome to RotoDraft Suite, the AI powered stock media collector.",
            output_path=out_audio,
            voice="en-US-ChristopherNeural"
        )
        self.assertTrue(out_audio.exists(), "Audio file must exist")
        self.assertTrue(Path(res["srt_path"]).exists(), "SRT subtitle file must exist")
        self.assertGreater(res["duration"], 1.0, "Audio duration must be > 1.0s")
        print(f"[PASS] TTS Engine: Generated {out_audio.name} ({res['duration']:.2f}s)")

    async def test_02_ai_engine_decomposition(self):
        """Test AI 1-Shot script decomposition into sequential scenes."""
        ai = AIEngine()
        script = "In the modern financial world, algorithmic trading accounts for over 70% of market volume. Neural networks analyze stock price movements in fractions of a second."
        clips = await ai.analyze_script(script, duration_seconds=6.0, clip_duration=3.0)
        self.assertEqual(len(clips), 2, "Expected 6.0s / 3.0s = 2 clips")
        self.assertEqual(clips[0]["index"], 1)
        self.assertEqual(clips[1]["index"], 2)
        self.assertTrue(len(clips[0]["keyword"]) > 0)
        print(f"[PASS] AI Engine: Decomposed into {len(clips)} scenes: {[c['keyword'] for c in clips]}")

    async def test_03_stock_search_and_kenburns(self):
        """Test stock search with fallback mechanism."""
        stock = StockSearcher()
        res = await stock.find_stock("modern city skyscraper", aspect_ratio="16:9")
        self.assertIn("url", res)
        self.assertTrue(res["url"].startswith("http"))
        print(f"[PASS] Stock Searcher: Found provider '{res['provider']}' -> URL: {res['url'][:60]}...")

    async def test_04_video_processor_and_kenburns(self):
        """Test FFmpeg precision clip rendering."""
        processor = VideoProcessor()
        # Create a sample image for Ken Burns test
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
            is_image=True
        )
        self.assertTrue(out_clip.exists(), "Processed clip must exist")
        self.assertGreater(os.path.getsize(out_clip), 1024, "Clip size must be > 1KB")
        print(f"[PASS] Video Processor: Created 3.0s clip {out_clip.name} ({os.path.getsize(out_clip)} bytes)")

    async def test_05_timeline_exporters(self):
        """Test CapCut and Premiere Pro XML generation."""
        dummy_clips = [self.test_dir / "01_sample_clip.mp4", self.test_dir / "01_sample_clip.mp4"]
        
        # CapCut
        capcut_res = TimelineExporter.export_capcut_draft(
            clip_paths=dummy_clips,
            output_dir=self.test_dir,
            project_name="TestProject"
        )
        self.assertTrue(capcut_res["draft_info"].exists())
        self.assertTrue(capcut_res["draft_content"].exists())

        # Premiere XML
        xml_path = self.test_dir / "test_timeline.xml"
        TimelineExporter.export_premiere_xml(
            clip_paths=dummy_clips,
            output_xml_path=xml_path,
            project_name="TestProject"
        )
        self.assertTrue(xml_path.exists())
        print(f"[PASS] Timeline Exporter: Created CapCut JSON & Premiere XML files")

    async def test_06_video_merger(self):
        """Test master video concatenation."""
        merger = VideoMerger()
        clip1 = self.test_dir / "01_sample_clip.mp4"
        audio = self.test_dir / "test_voice.mp3"
        master_out = self.test_dir / "Full_Video_Master.mp4"

        merger.merge_clips(
            clip_paths=[clip1, clip1],
            output_master_path=master_out,
            audio_path=audio
        )
        self.assertTrue(master_out.exists(), "Master video must exist")
        self.assertGreater(os.path.getsize(master_out), 5000, "Master video must have content")
        print(f"[PASS] Video Merger: Rendered Master Video ({os.path.getsize(master_out)} bytes)")

if __name__ == "__main__":
    unittest.main()
