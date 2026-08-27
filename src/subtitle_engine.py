import re
from pathlib import Path
from typing import List, Dict, Any, Optional

SUBTITLE_STYLES = {
    "hormozi": {
        "name": "🔥 Hormozi Viral Yellow (Bold Black Outline)",
        "font_name": "Impact",
        "font_size": 26,
        "primary_color": "&H0000FFFF",  # Yellow in ASS (AABBGGRR)
        "outline_color": "&H00000000",  # Black
        "outline": 3.5,
        "shadow": 2.0,
        "bold": 1,
        "margin_v": 60
    },
    "cyber_cyan": {
        "name": "💎 Cyber Neon Cyan (High Tech)",
        "font_name": "Arial Black",
        "font_size": 24,
        "primary_color": "&H00FFFF00",  # Cyan in ASS
        "outline_color": "&H00000000",
        "outline": 3.0,
        "shadow": 1.5,
        "bold": 1,
        "margin_v": 55
    },
    "clean_white": {
        "name": "⚪ Clean Minimal White (Modern)",
        "font_name": "Arial",
        "font_size": 22,
        "primary_color": "&H00FFFFFF",  # White
        "outline_color": "&H00000000",
        "outline": 2.5,
        "shadow": 1.0,
        "bold": 1,
        "margin_v": 50
    }
}

class SubtitleEngine:
    @classmethod
    def srt_to_ass(
        cls,
        srt_path: Path,
        ass_output_path: Path,
        style_id: str = "hormozi",
        aspect_ratio: str = "16:9"
    ) -> Path:
        """
        Converts SRT subtitles into high-retention Advanced SubStation Alpha (.ass) subtitles.
        """
        srt_path = Path(srt_path)
        ass_output_path = Path(ass_output_path)
        
        if not srt_path.exists():
            raise FileNotFoundError(f"SRT file not found: {srt_path}")

        style = SUBTITLE_STYLES.get(style_id, SUBTITLE_STYLES["hormozi"])
        res_w, res_h = (1080, 1920) if aspect_ratio == "9:16" else ((1920, 1080) if aspect_ratio == "16:9" else (1080, 1080))
        
        font_size = style["font_size"]
        if aspect_ratio == "9:16":
            font_size = int(font_size * 1.3)
            margin_v = 120
        else:
            margin_v = style["margin_v"]

        header = f"""[Script Info]
Title: RotoDraft Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {res_w}
PlayResY: {res_h}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style['font_name']},{font_size},{style['primary_color']},&H000000FF,{style['outline_color']},&H00000000,{style['bold']},0,0,0,100,100,0,0,1,{style['outline']},{style['shadow']},2,20,20,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        with open(srt_path, "r", encoding="utf-8", errors="ignore") as f:
            srt_content = f.read()

        events = []
        blocks = re.split(r'\n\s*\n', srt_content.strip())
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if len(lines) >= 3:
                time_line = lines[1]
                text_lines = " ".join(lines[2:])
                
                # Match: 00:00:01,000 --> 00:00:04,500
                m = re.match(r'(\d+:\d+:\d+),(\d+)\s*-->\s*(\d+:\d+:\d+),(\d+)', time_line)
                if m:
                    start_t = f"{m.group(1)}.{m.group(2)[:2]}"
                    end_t = f"{m.group(3)}.{m.group(4)[:2]}"
                    
                    # Clean text
                    clean_text = re.sub(r'<[^>]+>', '', text_lines).strip()
                    if clean_text:
                        events.append(f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{clean_text}")

        with open(ass_output_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events))

        return ass_output_path
