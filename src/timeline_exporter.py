import json
import uuid
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

class TimelineExporter:
    @staticmethod
    def export_capcut_draft(
        clip_paths: List[Path],
        output_dir: Path,
        project_name: str = "RotoDraft_Project",
        aspect_ratio: str = "16:9",
        duration_per_clip: float = 3.0
    ) -> Dict[str, Path]:
        """
        Generates CapCut Desktop compatible draft files (draft_info.json & draft_content.json).
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        width, height = (1920, 1080) if aspect_ratio == "16:9" else ((1080, 1920) if aspect_ratio == "9:16" else (1080, 1080))
        fps = 30
        
        draft_id = str(uuid.uuid4())
        total_duration_us = int(len(clip_paths) * duration_per_clip * 1000000)

        # 1. draft_info.json
        draft_info = {
            "draft_id": draft_id,
            "draft_name": project_name,
            "draft_cover": "",
            "draft_fold_path": str(output_dir.resolve()),
            "draft_timeline_materials_size_": len(clip_paths),
            "tm_draft_create": int(time.time()),
            "tm_draft_modified": int(time.time()),
            "tm_duration": total_duration_us
        }
        draft_info_path = output_dir / "draft_info.json"
        with open(draft_info_path, "w", encoding="utf-8") as f:
            json.dump(draft_info, f, indent=2)

        # 2. draft_content.json
        videos = []
        segments = []
        curr_time = 0

        for i, clip in enumerate(clip_paths):
            mat_id = str(uuid.uuid4())
            dur_us = int(duration_per_clip * 1000000)
            
            videos.append({
                "id": mat_id,
                "path": str(Path(clip).resolve()),
                "duration": dur_us,
                "width": width,
                "height": height,
                "material_name": Path(clip).name,
                "type": "video"
            })

            segments.append({
                "id": str(uuid.uuid4()),
                "material_id": mat_id,
                "target_timerange": {
                    "duration": dur_us,
                    "start": curr_time
                },
                "source_timerange": {
                    "duration": dur_us,
                    "start": 0
                },
                "speed": 1.0,
                "volume": 1.0
            })
            curr_time += dur_us

        draft_content = {
            "id": draft_id,
            "canvas_config": {
                "width": width,
                "height": height,
                "ratio": "16:9" if aspect_ratio == "16:9" else ("9:16" if aspect_ratio == "9:16" else "1:1")
            },
            "duration": total_duration_us,
            "fps": fps,
            "materials": {
                "videos": videos,
                "audios": [],
                "texts": []
            },
            "tracks": [
                {
                    "id": str(uuid.uuid4()),
                    "type": "video",
                    "segments": segments
                }
            ]
        }
        draft_content_path = output_dir / "draft_content.json"
        with open(draft_content_path, "w", encoding="utf-8") as f:
            json.dump(draft_content, f, indent=2)

        return {
            "draft_info": draft_info_path,
            "draft_content": draft_content_path
        }

    @staticmethod
    def export_premiere_xml(
        clip_paths: List[Path],
        output_xml_path: Path,
        project_name: str = "RotoDraft_Sequence",
        aspect_ratio: str = "16:9",
        duration_per_clip: float = 3.0
    ) -> Path:
        """
        Generates Apple Final Cut Pro XML (compatible with Adobe Premiere Pro and DaVinci Resolve).
        """
        output_xml_path = Path(output_xml_path)
        output_xml_path.parent.mkdir(parents=True, exist_ok=True)

        width, height = (1920, 1080) if aspect_ratio == "16:9" else ((1080, 1920) if aspect_ratio == "9:16" else (1080, 1080))
        fps = 30
        frames_per_clip = int(duration_per_clip * fps)
        total_frames = frames_per_clip * len(clip_paths)

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!DOCTYPE xmeml>',
            '<xmeml version="4">',
            f'  <sequence id="{uuid.uuid4()}">',
            f'    <name>{project_name}</name>',
            f'    <duration>{total_frames}</duration>',
            '    <rate>',
            f'      <timebase>{fps}</timebase>',
            '      <ntsc>FALSE</ntsc>',
            '    </rate>',
            '    <media>',
            '      <video>',
            '        <format>',
            '          <samplecharacteristics>',
            f'            <width>{width}</width>',
            f'            <height>{height}</height>',
            '            <rate>',
            f'              <timebase>{fps}</timebase>',
            '              <ntsc>FALSE</ntsc>',
            '            </rate>',
            '          </samplecharacteristics>',
            '        </format>',
            '        <track>'
        ]

        curr_frame = 0
        for i, clip in enumerate(clip_paths):
            clip_name = Path(clip).name
            file_url = "file://localhost/" + str(Path(clip).resolve()).replace("\\", "/")
            end_frame = curr_frame + frames_per_clip

            xml_lines.extend([
                f'          <clipitem id="clipitem-{i+1}">',
                f'            <name>{clip_name}</name>',
                f'            <duration>{frames_per_clip}</duration>',
                '            <rate>',
                f'              <timebase>{fps}</timebase>',
                '            </rate>',
                f'            <start>{curr_frame}</start>',
                f'            <end>{end_frame}</end>',
                '            <in>0</in>',
                f'            <out>{frames_per_clip}</out>',
                f'            <file id="file-{i+1}">',
                f'              <name>{clip_name}</name>',
                f'              <pathurl>{file_url}</pathurl>',
                '              <rate>',
                f'                <timebase>{fps}</timebase>',
                '              </rate>',
                f'              <duration>{frames_per_clip}</duration>',
                '              <media>',
                '                <video>',
                '                  <samplecharacteristics>',
                f'                    <width>{width}</width>',
                f'                    <height>{height}</height>',
                '                  </samplecharacteristics>',
                '                </video>',
                '              </media>',
                '            </file>',
                '          </clipitem>'
            ])
            curr_frame = end_frame

        xml_lines.extend([
            '        </track>',
            '      </video>',
            '    </media>',
            '  </sequence>',
            '</xmeml>'
        ])

        with open(output_xml_path, "w", encoding="utf-8") as f:
            f.write("\n".join(xml_lines))

        return output_xml_path
