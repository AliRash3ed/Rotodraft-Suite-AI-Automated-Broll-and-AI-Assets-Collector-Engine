import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any

class NLEExporter:
    """
    Exports rendered b-roll timelines directly into:
    1. Adobe Premiere Pro (FCP XML / XML)
    2. DaVinci Resolve (FCP XML / EDL)
    3. CapCut (Draft JSON / CSV Media List)
    """

    @staticmethod
    def export_fcp_xml(
        project_name: str,
        clips: List[Dict[str, Any]],
        output_dir: Path,
        fps: int = 30,
        width: int = 1920,
        height: int = 1080
    ) -> Path:
        """Generates standard Final Cut Pro 7 XML compatible with Adobe Premiere Pro and DaVinci Resolve."""
        root = ET.Element("xmeml", version="4")
        sequence = ET.SubElement(root, "sequence")
        ET.SubElement(sequence, "name").text = project_name
        ET.SubElement(sequence, "duration").text = str(len(clips) * int(fps * 3.0))

        rate = ET.SubElement(sequence, "rate")
        ET.SubElement(rate, "timebase").text = str(fps)
        ET.SubElement(rate, "ntsc").text = "FALSE"

        media = ET.SubElement(sequence, "media")
        video = ET.SubElement(media, "video")
        format_el = ET.SubElement(video, "format")
        sample = ET.SubElement(format_el, "samplecharacteristics")
        ET.SubElement(sample, "width").text = str(width)
        ET.SubElement(sample, "height").text = str(height)

        track = ET.SubElement(video, "track")

        current_frame = 0
        clip_frames = int(fps * 3.0)

        for i, clip in enumerate(clips, 1):
            clipitem = ET.SubElement(track, "clipitem", id=f"clipitem-{i}")
            ET.SubElement(clipitem, "name").text = clip.get("output_filename", f"clip_{i}.mp4")
            ET.SubElement(clipitem, "duration").text = str(clip_frames)
            ET.SubElement(clipitem, "start").text = str(current_frame)
            ET.SubElement(clipitem, "end").text = str(current_frame + clip_frames)
            ET.SubElement(clipitem, "in").text = "0"
            ET.SubElement(clipitem, "out").text = str(clip_frames)

            file_el = ET.SubElement(clipitem, "file", id=f"file-{i}")
            ET.SubElement(file_el, "name").text = clip.get("output_filename", f"clip_{i}.mp4")
            
            # Relative file path for universal import
            rel_path = f"clips/{clip.get('output_filename', f'clip_{i}.mp4')}"
            ET.SubElement(file_el, "pathurl").text = f"file://localhost/{rel_path}"

            # Markers for Keywords
            keyword = clip.get("keyword", f"Scene {i}")
            marker = ET.SubElement(clipitem, "marker")
            ET.SubElement(marker, "name").text = keyword
            ET.SubElement(marker, "comment").text = f"Script: {clip.get('script_segment', '')}"
            ET.SubElement(marker, "in").text = "0"

            current_frame += clip_frames

        xml_path = output_dir / f"{project_name}_premiere_davinci.xml"
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(str(xml_path), encoding="utf-8", xml_declaration=True)
        return xml_path

    @staticmethod
    def export_edl(
        project_name: str,
        clips: List[Dict[str, Any]],
        output_dir: Path,
        fps: int = 30
    ) -> Path:
        """Generates standard CMX 3600 EDL for DaVinci Resolve and Premiere Pro."""
        edl_lines = [
            f"TITLE: {project_name}",
            f"FCM: NON-DROP FRAME",
            ""
        ]

        def frames_to_tc(frames: int) -> str:
            hrs = frames // (3600 * fps)
            rem = frames % (3600 * fps)
            mins = rem // (60 * fps)
            rem = rem % (60 * fps)
            secs = rem // fps
            f = rem % fps
            return f"{hrs:02d}:{mins:02d}:{secs:02d}:{f:02d}"

        current_rec_frame = 0
        clip_frames = int(fps * 3.0)

        for i, clip in enumerate(clips, 1):
            src_in = frames_to_tc(0)
            src_out = frames_to_tc(clip_frames)
            rec_in = frames_to_tc(current_rec_frame)
            rec_out = frames_to_tc(current_rec_frame + clip_frames)
            
            clip_name = clip.get("output_filename", f"clip_{i}.mp4")
            edl_lines.append(f"{i:03d}  AX       V     C        {src_in} {src_out} {rec_in} {rec_out}")
            edl_lines.append(f"* FROM CLIP NAME: {clip_name}")
            edl_lines.append(f"* KEYWORD: {clip.get('keyword', '')}")
            edl_lines.append("")

            current_rec_frame += clip_frames

        edl_path = output_dir / f"{project_name}_davinci.edl"
        with open(edl_path, "w", encoding="utf-8") as f:
            f.write("\n".join(edl_lines))
        return edl_path

    @staticmethod
    def export_capcut_draft(
        project_name: str,
        clips: List[Dict[str, Any]],
        output_dir: Path
    ) -> Path:
        """Generates CapCut compatible JSON sequence schema and CSV import sheet."""
        capcut_data = {
            "project_name": project_name,
            "version": "2.0.0",
            "tracks": [
                {
                    "type": "video",
                    "clips": [
                        {
                            "index": c.get("index", i),
                            "file": f"clips/{c.get('output_filename', '')}",
                            "duration": 3.0,
                            "keyword": c.get("keyword", ""),
                            "script_snippet": c.get("script_segment", ""),
                            "start_time": (i - 1) * 3.0,
                            "end_time": i * 3.0
                        }
                        for i, c in enumerate(clips, 1)
                    ]
                }
            ]
        }

        json_path = output_dir / f"{project_name}_capcut_draft.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(capcut_data, f, indent=2)

        # Also write CSV for easy CapCut / Batch Media import
        csv_path = output_dir / f"{project_name}_timeline.csv"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("Index,Filename,Start Time,End Time,Keyword,Script Segment\n")
            for i, c in enumerate(clips, 1):
                f.write(f"{i},\"{c.get('output_filename','')}\",{(i-1)*3.0},{i*3.0},\"{c.get('keyword','')}\",\"{c.get('script_segment','')}\"\n")

        return json_path
