import argparse
import sys
import os
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import Config
from src.pipeline import StockCollectorPipeline
from src.system_checker import SystemChecker
from src.usage_tracker import UsageTracker
from src.error_doctor import AIErrorDoctor
from src.video_processor import VideoProcessor

def parse_duration_to_seconds(input_str) -> float:
    raw = str(input_str).strip()
    if ":" in raw:
        parts = raw.split(":")
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    try:
        return float(raw)
    except Exception:
        return 90.0

def print_creator_banner():
    print("=" * 70)
    print("   AI B-ROLL & STOCK MEDIA COLLECTOR PRO (2026 COMMERCIAL EDITION)")
    print("   Built by Ali Rasheed from Lahore, Pakistan")
    print("   Contact: alihouse512@gmail.com | LinkedIn: /in/alirasheedbhatt")
    print("   Open Source & Built to Empower Video Creators Worldwide")
    print("=" * 70)

def print_about():
    print_creator_banner()
    print("\n[ABOUT & OPEN SOURCE MANIFESTO]")
    print("-" * 50)
    print("""Creator: Ali Rasheed from Lahore, Pakistan.
Role: Full-Stack AI Developer & Tech Infrastructure Engineer.

Vision:
Traditional video editing SaaS charge $40-$60/month for simple stock footage
generation. AI Stock Media Collector Pro eliminates subscription barriers by
connecting state-of-the-art reasoning LLMs (DeepSeek-R1, Groq, Claude 3.5),
parallel stock scrapers (Pexels, Pixabay, Unsplash, Pinterest), and local
FFmpeg rendering into an autonomous pipeline with direct Premiere Pro,
DaVinci Resolve, and CapCut export capabilities.
""")

def print_contact():
    print_creator_banner()
    print("\n[CONTACT & HIRE ALI RASHEED]")
    print("-" * 50)
    print("Email:     alihouse512@gmail.com")
    print("LinkedIn:  https://www.linkedin.com/in/alirasheedbhatt")
    print("X/Twitter: https://x.com/AliRasheedBti")
    print("Instagram: https://www.instagram.com/this_is_ali_r/")
    print("Facebook:  https://www.facebook.com/profile.php?id=61579456175357")
    print("Location:  Lahore, Pakistan (Available for Global Remote AI Projects)")
    print("-" * 50 + "\n")

def print_agent_integrations():
    print_creator_banner()
    print("\n[AGENT & SKILL INTEGRATION HUB]\n")
    print("1. HERMES AGENT INTEGRATION:")
    print("-" * 50)
    print("""Add this tool function to your Hermes Agent:

import subprocess
from pathlib import Path

def collect_broll(script: str, duration: int = 60, quality: str = "1080p", aspect_ratio: str = "16:9") -> dict:
    tool_dir = Path(__file__).resolve().parent
    cmd = ["python", str(tool_dir / "cli.py"), "--script", script, "--duration", str(duration), "--quality", quality, "--aspect-ratio", aspect_ratio]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(tool_dir))
    return {"status": "success" if proc.returncode == 0 else "error", "output": proc.stdout}
""")
    print("2. OPENCLAW INTEGRATION:")
    print("-" * 50)
    print("""Add to plugins/stock_collector/plugin.json:

{
  "plugin_name": "ai-stock-collector-pro",
  "version": "2.0.0",
  "author": "Ali Rasheed",
  "entrypoint": "cli.py",
  "capabilities": ["script_analysis", "stock_search", "ffmpeg_rendering"],
  "supported_ratios": ["16:9", "9:16", "1:1", "4:5"]
}
""")
    print("3. CLAUDE CODE & CODEX CLI ONE-LINER:")
    print("-" * 50)
    print('python cli.py --script "Your script here" --duration 45 --quality 1080p\n')

def interactive_wizard():
    print_creator_banner()

    # Hardware Profile
    hw = SystemChecker.get_hardware_profile()
    print(f"\n[HARDWARE ACCELERATION] {hw['label']} ({hw['cores']} Cores | {hw['ram_gb']}GB RAM)")
    
    summary = UsageTracker.get_summary()
    pex = summary.get("pexels", {})
    pix = summary.get("pixabay", {})
    print(f"[QUOTA STATUS] Pexels: {pex.get('remaining', 200)}/hr left | Pixabay: {pix.get('remaining', 5000)}/hr left\n")

    print("[?] Enter your video voiceover script (or type 'SAMPLE'):")
    script = input("> ").strip()
    if not script or script.upper() == "SAMPLE":
        script = (
            "Artificial intelligence is transforming global computing at breakneck speed. "
            "Engineers and roboticists design autonomous systems inside modern high-tech research laboratories. "
            "From busy metropolis streets to high-speed data centers, digital networks process petabytes of real-time data."
        )
        print(f"-> Loaded Sample Script ({len(script)} characters).")

    words = len(script.split())
    est_secs = max(6, round(words / 2.5))
    print(f"-> Script Statistics: {len(script)} chars, {words} words (~{est_secs}s @ 150 WPM)")

    print("\n[?] Do you have a voiceover audio file? (Drag & drop file or press Enter to skip):")
    audio_path_input = input("> ").strip().strip("\"'")
    dur_secs = float(est_secs)
    voiceover_file = None

    if audio_path_input and Path(audio_path_input).exists() and Path(audio_path_input).is_file():
        voiceover_file = Path(audio_path_input)
        # Probe duration with ffprobe
        import subprocess, json
        try:
            cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(voiceover_file)]
            out = subprocess.check_output(cmd, creationflags=0x00004000 if sys.platform == "win32" else 0)
            data = json.loads(out)
            dur_secs = float(data.get("format", {}).get("duration", est_secs))
            print(f"-> Detected Audio Duration: {dur_secs:.1f}s ({voiceover_file.name})")
        except Exception:
            print(f"-> Audio file loaded ({voiceover_file.name}).")
    else:
        print(f"\n[?] Enter voiceover duration in seconds or MM:SS (e.g. 1:30 or {est_secs}):")
        dur_input = input(f"[Default: {est_secs}]> ").strip() or str(est_secs)
        dur_secs = parse_duration_to_seconds(dur_input)

    num_clips = max(1, round(dur_secs / 3.0))

    print("\n[?] Select Output Quality (1: 1080p Full HD, 2: 720p HD, 3: 4K UHD):")
    q_choice = input("[Default: 1]> ").strip()
    q_map = {"1": "1080p", "2": "720p", "3": "4K"}
    quality = q_map.get(q_choice, "1080p")

    print("\n[?] Select Aspect Ratio (1: 16:9 Landscape, 2: 9:16 Vertical, 3: 1:1 Square, 4: 4:5 Feed):")
    ar_choice = input("[Default: 1]> ").strip()
    ar_map = {"1": "16:9", "2": "9:16", "3": "1:1", "4": "4:5"}
    aspect_ratio = ar_map.get(ar_choice, "16:9")

    print("\n[?] Select AI Brain Provider (1: OpenRouter, 2: DeepSeek, 3: Groq, 4: Gemini, 5: OpenAI, 6: Claude, 7: Ollama):")
    ai_choice = input("[Default: 1]> ").strip()
    ai_map = {
        "1": "openrouter",
        "2": "deepseek",
        "3": "groq",
        "4": "gemini",
        "5": "openai",
        "6": "anthropic",
        "7": "ollama"
    }
    ai_provider = ai_map.get(ai_choice, "openrouter")

    print("\n[?] Stitch full video into one continuous MP4 file? (y/n):")
    full_vid_choice = input("[Default: y]> ").strip().lower()
    export_full = full_vid_choice != "n"

    eta_info = SystemChecker.calculate_estimated_time(total_clips=num_clips, quality=quality)
    print(f"\n⚡ ESTIMATED TIME: ~{eta_info['formatted_eta']} ({eta_info['speed_rating']}, Direct Stream Engine)")

    print(f"\n[*] Starting parallel collection for {dur_secs:.1f}s ({num_clips} clips)...")
    pipeline = StockCollectorPipeline()
    try:
        res = pipeline.run(
            script=script,
            duration_seconds=dur_secs,
            clip_duration=3.0,
            project_name="cli_interactive_run",
            quality=quality,
            aspect_ratio=aspect_ratio,
            media_type="videos",
            providers=["pexels", "pixabay", "unsplash", "pinterest"],
            enable_fallback=True,
            ai_provider=ai_provider,
            export_full_video=export_full,
        )

        # If audio provided and master video stitched, mux audio
        if voiceover_file and res.get("master_video_filename"):
            proj_dir = Path(res["clips_dir"]).parent
            master_p = proj_dir / res["master_video_filename"]
            muxed_p = proj_dir / f"{proj_dir.name}_master_with_audio.mp4"
            vp = VideoProcessor()
            vp.mux_audio_with_video(master_p, voiceover_file, muxed_p)
            print(f"🎙️ Muxed Voiceover Audio: {muxed_p.name}")

        print("\n" + "=" * 70)
        print(f"[OK] COMPLETED: {res['success_clips']} / {res['required_clips']} clips ready on disk!")
        print(f"Clips Directory: {res['clips_dir']}")
        print("Generated NLE Exports: Premiere XML, DaVinci EDL, CapCut Draft")
        if res.get("master_video_filename"):
            print(f"Master Video: {res['master_video_filename']}")
        print("=" * 70 + "\n")
    except Exception as e:
        diag = AIErrorDoctor.diagnose(str(e))
        print("\n[🩺 AI ERROR DOCTOR DIAGNOSIS]")
        print(f"Issue: {diag['title']}")
        print(f"Explanation: {diag['explanation']}")
        print("Solution Steps:")
        for s in diag.get("solution_steps", []):
            print(f" - {s}")

def main():
    parser = argparse.ArgumentParser(description="AI B-Roll & Stock Media Collector Pro CLI")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive terminal wizard")
    parser.add_argument("--agent-help", "-a", action="store_true", help="Print Hermes Agent, OpenClaw & Claude Code integration guide")
    parser.add_argument("--about", action="store_true", help="Print project manifesto and Ali Rasheed bio")
    parser.add_argument("--contact", action="store_true", help="Print contact information and social channels")
    parser.add_argument("--swap", action="store_true", help="Swap a single clip in an existing project")
    parser.add_argument("--project", type=str, default=None, help="Target project folder name for clip swap")
    parser.add_argument("--clip", type=int, default=None, help="Clip index (1-based) to swap")
    parser.add_argument("--keyword", type=str, default=None, help="New keyword for single-clip swap")
    parser.add_argument("--script", type=str, default=None, help="Video voiceover script or file path")
    parser.add_argument("--duration", type=float, default=90.0, help="Total duration in seconds (default: 90)")
    parser.add_argument("--clip-duration", type=float, default=3.0, help="Target clip duration in seconds (default: 3.0)")
    parser.add_argument("--project-name", type=str, default="cli_broll_project", help="Project name")
    parser.add_argument("--quality", type=str, default="1080p", choices=["720p", "1080p", "4K"], help="Output quality")
    parser.add_argument("--aspect-ratio", type=str, default="16:9", choices=["16:9", "9:16", "1:1", "4:5"], help="Aspect ratio")
    parser.add_argument("--media-type", type=str, default="videos", choices=["videos", "photos", "both"], help="Media type")
    parser.add_argument("--providers", nargs="+", default=["pexels", "pixabay", "unsplash", "pinterest"], help="Stock providers")
    parser.add_argument("--ai-provider", type=str, default="openrouter", choices=["openrouter", "deepseek", "groq", "cohere", "openai", "gemini", "anthropic", "ollama", "custom"], help="AI Provider")
    parser.add_argument("--ai-model", type=str, default=None, help="Custom AI model slug")
    parser.add_argument("--full-video", action="store_true", help="Concatenate into full master video MP4")
    parser.add_argument("--no-fallback", action="store_true", help="Disable fallback rewriting")

    args = parser.parse_args()

    if args.about:
        print_about()
        return

    if args.contact:
        print_contact()
        return

    if args.agent_help:
        print_agent_integrations()
        return

    if args.swap:
        if not args.project or not args.clip or not args.keyword:
            print("[ERROR] Single-clip swap requires --project <folder>, --clip <index>, and --keyword <query>")
            return
        pipeline = StockCollectorPipeline()
        try:
            print(f"[*] Swapping Clip #{args.clip} in project '{args.project}' with query '{args.keyword}'...")
            updated_clip = pipeline.swap_single_clip(args.project, args.clip, args.keyword)
            print(f"[OK] Clip #{args.clip} successfully swapped: {updated_clip.get('output_filename')}")
        except Exception as e:
            print(f"[ERROR] Swap failed: {e}")
        return

    if args.interactive or not args.script:
        interactive_wizard()
        return

    print_creator_banner()
    script_text = args.script
    if Path(script_text).exists() and Path(script_text).is_file():
        with open(script_text, "r", encoding="utf-8") as f:
            script_text = f.read()

    provs = []
    for p in args.providers:
        for sub in p.split(","):
            if sub.strip(): provs.append(sub.strip().lower())

    pipeline = StockCollectorPipeline()
    try:
        res = pipeline.run(
            script=script_text,
            duration_seconds=args.duration,
            clip_duration=args.clip_duration,
            project_name=args.project_name,
            quality=args.quality,
            aspect_ratio=args.aspect_ratio,
            media_type=args.media_type,
            providers=provs,
            enable_fallback=not args.no_fallback,
            ai_provider=args.ai_provider,
            ai_model=args.ai_model,
            export_full_video=args.full_video,
        )
        print(f"\n[OK] Completed: {res['success_clips']} / {res['required_clips']} clips saved to {res['clips_dir']}")
        print("Generated NLE Exports: Premiere XML, DaVinci EDL, CapCut Draft")
    except Exception as e:
        diag = AIErrorDoctor.diagnose(str(e))
        print(f"\n[🩺 AI ERROR DOCTOR] {diag['title']}")
        print(f"Explanation: {diag['explanation']}")
        for s in diag.get("solution_steps", []):
            print(f" -> {s}")

if __name__ == "__main__":
    main()
