import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import Config
from src.ai_engine import AIEngine
from src.stock_searcher import StockSearcher
from src.video_processor import VideoProcessor
from src.system_checker import SystemChecker
from src.nle_exporter import NLEExporter
from src.error_doctor import AIErrorDoctor
from app import parse_duration_to_seconds

class TestStockCollector(unittest.TestCase):
    def test_duration_parsing(self):
        self.assertEqual(parse_duration_to_seconds("90"), 90.0)
        self.assertEqual(parse_duration_to_seconds("1:30"), 90.0)
        self.assertEqual(parse_duration_to_seconds("4:30"), 270.0)
        self.assertEqual(parse_duration_to_seconds("0:45"), 45.0)
        self.assertEqual(parse_duration_to_seconds("1:00:00"), 3600.0)
        self.assertEqual(parse_duration_to_seconds(""), 0.0)
        self.assertEqual(parse_duration_to_seconds(None), 0.0)
        self.assertEqual(parse_duration_to_seconds("invalid"), 0.0)

    def test_config_resolutions(self):
        # 16:9
        self.assertEqual(Config.get_resolution("1080p", "16:9"), (1920, 1080))
        self.assertEqual(Config.get_resolution("720p", "16:9"), (1280, 720))
        self.assertEqual(Config.get_resolution("4K", "16:9"), (3840, 2160))

        # 9:16
        self.assertEqual(Config.get_resolution("1080p", "9:16"), (1080, 1920))

        # 1:1
        self.assertEqual(Config.get_resolution("1080p", "1:1"), (1080, 1080))

    def test_config_orientation(self):
        self.assertEqual(Config.get_orientation_for_api("16:9"), "landscape")
        self.assertEqual(Config.get_orientation_for_api("9:16"), "portrait")
        self.assertEqual(Config.get_orientation_for_api("1:1"), "square")

    def test_ai_json_parsing(self):
        ai = AIEngine()
        sample_response = """
        ```json
        [
          {
            "index": 1,
            "keyword": "city traffic sunset",
            "fallback_keyword": "busy traffic",
            "visual_description": "Time lapse of evening city traffic"
          },
          {
            "index": 2,
            "keyword": "office team meeting",
            "fallback_keyword": "business people",
            "visual_description": "Colleagues collaborating"
          }
        ]
        ```
        """
        items = ai._parse_json(sample_response, 2)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["keyword"], "city traffic sunset")
        self.assertEqual(items[1]["keyword"], "office team meeting")

    def test_ai_thinking_mode_strip(self):
        ai = AIEngine()
        reasoning_response = """
        <think>
        The user wants 2 clips about AI research labs and robotic arms.
        Clip 1: scientist in lab.
        Clip 2: robotic arm assembling circuit.
        </think>
        [
          {"index": 1, "keyword": "ai research lab scientist", "fallback_keyword": "laboratory"},
          {"index": 2, "keyword": "robotic arm assembly", "fallback_keyword": "robotics"}
        ]
        """
        items = ai._parse_json(reasoning_response, 2)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["keyword"], "ai research lab scientist")
        self.assertEqual(items[1]["keyword"], "robotic arm assembly")

    def test_video_processor_sanitize_filename(self):
        vp = VideoProcessor()
        self.assertEqual(vp.sanitize_filename("ai computer & network: test?"), "ai_computer_network_test")
        self.assertEqual(vp.sanitize_filename("a" * 100), "a" * 40)

    def test_system_checker(self):
        ff = SystemChecker.check_ffmpeg()
        self.assertTrue(ff["ffmpeg_available"])
        self.assertTrue(ff["ffprobe_available"])

    def test_nle_exporter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            sample_clips = [
                {"index": 1, "output_filename": "01_city.mp4", "keyword": "modern city", "script_segment": "Intro"},
                {"index": 2, "output_filename": "02_office.mp4", "keyword": "office team", "script_segment": "Middle"}
            ]

            xml_p = NLEExporter.export_fcp_xml("test_proj", sample_clips, tmp_path)
            self.assertTrue(xml_p.exists())
            self.assertTrue(xml_p.stat().st_size > 100)

            edl_p = NLEExporter.export_edl("test_proj", sample_clips, tmp_path)
            self.assertTrue(edl_p.exists())

            capcut_p = NLEExporter.export_capcut_draft("test_proj", sample_clips, tmp_path)
            self.assertTrue(capcut_p.exists())

    def test_error_doctor_diagnosis(self):
        d1 = AIErrorDoctor.diagnose("FFmpeg binary not found on PATH")
        self.assertEqual(d1["category"], "FFmpeg Engine")

        d2 = AIErrorDoctor.diagnose("HTTP 429 Too Many Requests rate limit exceeded")
    def test_hardware_profile_detection(self):
        profile = SystemChecker.get_hardware_profile()
        self.assertIn("tier", profile)
        self.assertIn("label", profile)
        self.assertIn("max_ffmpeg_workers", profile)
        self.assertGreaterEqual(profile["max_ffmpeg_workers"], 1)

    def test_9_16_blurred_stack_filter(self):
        vp = VideoProcessor()
        vf_916 = vp._build_video_filter(1080, 1920, "9:16")
        self.assertIn("split=2[bg][fg]", vf_916)
        self.assertIn("boxblur", vf_916)
        self.assertIn("overlay=", vf_916)

        vf_169 = vp._build_video_filter(1920, 1080, "16:9")
        self.assertNotIn("split=2", vf_169)
        self.assertIn("scale=1920:1080", vf_169)

    def test_dynamic_nle_duration_calculation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            sample_clips = [
                {"index": 1, "output_filename": "01_intro.mp4", "duration": 4.5, "final_duration": 4.5, "keyword": "intro"},
                {"index": 2, "output_filename": "02_outro.mp4", "duration": 2.0, "final_duration": 2.0, "keyword": "outro"}
            ]
            xml_p = NLEExporter.export_fcp_xml("dyn_proj", sample_clips, tmp_path, fps=30)
            self.assertTrue(xml_p.exists())
            with open(xml_p, "r", encoding="utf-8") as f:
                content = f.read()
                # 4.5s * 30 + 2.0s * 30 = 135 + 60 = 195 total frames
                self.assertIn("<duration>195</duration>", content)

if __name__ == "__main__":
    unittest.main()
