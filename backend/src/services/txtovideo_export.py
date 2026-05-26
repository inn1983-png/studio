import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logging import get_logger

logger = get_logger(__name__)

JIANYING_IMPORT_NOTES = """Txtovideo Studio -> 剪映 导入说明
=====================================

1. 图片素材导入
   - 将 image_prompts.json 中每个分镜的 positive_prompt 复制到 AI 图片生成工具
   - 生成图片后导入剪映，按 storyboard.json 中的 order_index 排列

2. 视频素材导入
   - 将 video_prompts.json 中每个分镜的 prompt 复制到 AI 视频生成工具
   - 生成视频后导入剪映，按 storyboard.json 中的 order_index 排列
   - 建议使用 first_frame_ref (首帧参考图) 保证画面连贯

3. 字幕导入
   - 剪映支持导入 SRT 字幕文件
   - 导入 subtitles.srt 即可自动对齐时间轴

4. 音频对齐
   - 建议先铺音频轨道，再对齐视频和字幕
   - 每个分镜默认 8-12 秒

5. 注意事项
   - 保持角色一致性：使用相同 seed 或参考图
   - 保持场景一致性：同一场景使用相同参考图
   - 画面比例：{aspect_ratio}
   - 目标平台：{platform}
"""

COMFYUI_NOTES = """Txtovideo Studio -> ComfyUI 使用说明
=====================================

1. 图片生成工作流
   - 读取 image_prompts.json
   - 每个分镜包含 positive_prompt 和 negative_prompt
   - model_hint 字段建议使用的模型
   - aspect_ratio 字段指定画面比例
   - seed 字段可用于复现结果

2. 视频生成工作流
   - 读取 video_prompts.json
   - engine 字段指定视频引擎 (ltx / seedance / runninghub)
   - first_frame_ref: 首帧参考图路径
   - last_frame_ref: 末帧参考图路径
   - camera_motion: 镜头运动描述
   - character_motion: 角色动作描述
   - avoid: 需要避免的内容

3. 批量处理建议
   - 按 storyboard.json 中的 order_index 顺序处理
   - 先完成所有图片生成，再进行视频生成
   - 视频生成使用对应图片作为首帧参考

4. LTX 稳定策略
   - 动作轻、镜头慢
   - 角色不大幅移动
   - 场景不跳变
   - 光线不突变
   - 避免快速转身
   - 避免多人复杂交互
"""


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
            self._write_json_entry(zf, "video_prompts_ltx.json", outputs.get("videoPrompts"))
            self._write_json_entry(zf, "quality_report.json", outputs.get("quality"))

            srt_content = self._build_srt(outputs)
            if srt_content:
                zf.writestr("subtitles.srt", srt_content)

            aspect_ratio = source.get("aspectRatio", "9:16") if source else "9:16"
            platform = source.get("platform", "douyin") if source else "douyin"
            zf.writestr("jianying_import_notes.txt", JIANYING_IMPORT_NOTES.format(
                aspect_ratio=aspect_ratio, platform=platform
            ))
            zf.writestr("comfyui_notes.txt", COMFYUI_NOTES)

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
            ("videoPrompts", "video_prompts_ltx.json"),
            ("quality", "quality_report.json"),
        ]:
            if outputs.get(key):
                files.append(filename)
        files.append("subtitles.srt")
        files.append("jianying_import_notes.txt")
        files.append("comfyui_notes.txt")
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

    def _build_srt(self, outputs: Dict[str, Any]) -> str:
        storyboard = self._parse_json(outputs.get("storyboard", ""))
        if not storyboard or not isinstance(storyboard, list):
            return ""

        default_duration = 10.0
        entries: List[str] = []
        current_time = 0.0

        for i, shot in enumerate(storyboard):
            duration = shot.get("duration_seconds", default_duration)
            if not duration or duration <= 0:
                duration = default_duration

            start_time = current_time
            end_time = current_time + duration

            cap_text = shot.get("cap", "").strip()
            if not cap_text:
                cap_text = shot.get("desc_promopt", "").strip()
            if not cap_text:
                cap_text = f"Shot {i + 1}"

            entries.append(str(i + 1))
            entries.append(f"{self._format_srt_time(start_time)} --> {self._format_srt_time(end_time)}")
            entries.append(cap_text)
            entries.append("")

            current_time = end_time

        return "\n".join(entries)

    def _format_srt_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _parse_json(self, data: Any) -> Any:
        if not data:
            return None
        if isinstance(data, (list, dict)):
            return data
        if isinstance(data, str):
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

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
        lines = ["# Export Notes", ""]
        if source:
            lines.append(f"- Era: {source.get('era', 'N/A')}")
            lines.append(f"- Style: {source.get('style', 'N/A')}")
            lines.append(f"- Platform: {source.get('platform', 'N/A')}")
            lines.append(f"- Aspect Ratio: {source.get('aspectRatio', 'N/A')}")
            lines.append("")

        storyboard = self._parse_json(outputs.get("storyboard", ""))
        if storyboard and isinstance(storyboard, list):
            lines.append(f"- Shot count: {len(storyboard)}")
            total_duration = sum(s.get("duration_seconds", 10) or 10 for s in storyboard)
            lines.append(f"- Total duration: ~{total_duration:.0f}s ({total_duration / 60:.1f}min)")
            lines.append("")

        lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat()}")
        return "\n".join(lines)
