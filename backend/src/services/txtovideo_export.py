import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.logging import get_logger

logger = get_logger(__name__)


class TxtovideoExportService:
    def __init__(self):
        pass

    async def export_package(
        self,
        package_name: str,
        project_id: Optional[str],
        source: Optional[Dict[str, Any]],
        outputs: Dict[str, Any],
        prompt_used: Optional[Dict[str, Any]],
    ) -> str:
        safe_name = "".join(
            c for c in package_name if c.isalnum() or c in "._- "
        ) or "txtovideo_export"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{safe_name}_{timestamp}.zip"
        temp_dir = tempfile.mkdtemp(prefix="txtovideo_export_")
        zip_path = os.path.join(temp_dir, zip_filename)

        manifest = self._build_manifest(
            package_name, project_id, source, outputs, prompt_used
        )

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

            if source and source.get("text"):
                zf.writestr("source.txt", source["text"])

            script_text = outputs.get("script", "")
            if script_text:
                zf.writestr("script.txt", script_text)

            self._write_json_entry(zf, "characters.json", outputs.get("characters"))
            self._write_json_entry(zf, "scenes.json", outputs.get("scenes"))
            self._write_json_entry(zf, "props.json", outputs.get("props"))
            self._write_json_entry(zf, "storyboard.json", outputs.get("storyboard"))
            self._write_json_entry(zf, "image_prompts.json", outputs.get("imagePrompts"))
            self._write_json_entry(zf, "video_prompts.json", outputs.get("videoPrompts"))
            self._write_json_entry(zf, "quality_report.json", outputs.get("quality"))

            notes = self._build_notes(source, outputs)
            zf.writestr("notes.md", notes)

        logger.info(f"Txtovideo ZIP exported: {zip_path}")
        return zip_path

    def _build_manifest(
        self,
        package_name: str,
        project_id: Optional[str],
        source: Optional[Dict[str, Any]],
        outputs: Dict[str, Any],
        prompt_used: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        files = ["manifest.json"]
        if source and source.get("text"):
            files.append("source.txt")
        if outputs.get("script"):
            files.append("script.txt")
        for key, filename in [
            ("characters", "characters.json"),
            ("scenes", "scenes.json"),
            ("props", "props.json"),
            ("storyboard", "storyboard.json"),
            ("imagePrompts", "image_prompts.json"),
            ("videoPrompts", "video_prompts.json"),
            ("quality", "quality_report.json"),
        ]:
            if outputs.get(key):
                files.append(filename)
        files.append("notes.md")

        manifest = {
            "package_name": package_name,
            "project_id": project_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files": files,
            "meta": {
                "title": source.get("text", "")[:50] if source else "",
                "era": source.get("era", "") if source else "",
                "style": source.get("style", "") if source else "",
                "platform": source.get("platform", "") if source else "",
                "aspect_ratio": source.get("aspectRatio", "") if source else "",
            },
        }
        if prompt_used:
            manifest["prompt_template_versions"] = {
                k: f"{v.get('template_id', '')}@{v.get('version', '')}"
                for k, v in prompt_used.items()
                if isinstance(v, dict)
            }
        return manifest

    def _write_json_entry(
        self, zf: zipfile.ZipFile, filename: str, data: Any
    ):
        if not data:
            return
        try:
            if isinstance(data, str):
                parsed = json.loads(data)
                zf.writestr(filename, json.dumps(parsed, ensure_ascii=False, indent=2))
            else:
                zf.writestr(filename, json.dumps(data, ensure_ascii=False, indent=2))
        except (json.JSONDecodeError, TypeError):
            if isinstance(data, str):
                zf.writestr(filename, data)

    def _build_notes(
        self,
        source: Optional[Dict[str, Any]],
        outputs: Dict[str, Any],
    ) -> str:
        lines = [f"# Export Notes", ""]
        if source:
            lines.append(f"- Era: {source.get('era', 'N/A')}")
            lines.append(f"- Style: {source.get('style', 'N/A')}")
            lines.append(f"- Platform: {source.get('platform', 'N/A')}")
            lines.append(f"- Aspect Ratio: {source.get('aspectRatio', 'N/A')}")
            lines.append("")
        lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat()}")
        return "\n".join(lines)
