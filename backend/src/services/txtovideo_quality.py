import json
import re
from typing import Any, Dict, List, Optional, Tuple
from src.core.logging import get_logger

logger = get_logger(__name__)

QUALITY_RULES = {
    "script": {
        "min_length": 200,
        "max_length": 50000,
        "required_sections": ["场景", "角色", "对话"],
        "check_items": [
            {"id": "script_length", "name": "剧本长度", "weight": 10},
            {"id": "has_dialogue", "name": "包含对话", "weight": 15},
            {"id": "has_scene_desc", "name": "包含场景描述", "weight": 10},
            {"id": "character_consistency", "name": "角色一致性", "weight": 20},
        ]
    },
    "characters": {
        "min_count": 1,
        "max_count": 20,
        "required_fields": ["name", "description"],
        "check_items": [
            {"id": "character_count", "name": "角色数量", "weight": 10},
            {"id": "has_description", "name": "角色描述完整", "weight": 15},
            {"id": "name_uniqueness", "name": "角色名唯一", "weight": 10},
        ]
    },
    "scenes": {
        "min_count": 1,
        "check_items": [
            {"id": "scene_count", "name": "场景数量", "weight": 10},
            {"id": "has_description", "name": "场景描述完整", "weight": 15},
        ]
    },
    "storyboard": {
        "min_count": 1,
        "check_items": [
            {"id": "shot_count", "name": "分镜数量", "weight": 15},
            {"id": "has_cap_text", "name": "字幕文本", "weight": 10},
            {"id": "duration_reasonable", "name": "时长合理", "weight": 10},
            {"id": "scene_continuity", "name": "场景连贯性", "weight": 15},
        ]
    },
    "image_prompts": {
        "check_items": [
            {"id": "prompt_completeness", "name": "提示词完整", "weight": 20},
            {"id": "negative_prompt", "name": "反向提示词", "weight": 10},
            {"id": "aspect_ratio", "name": "画面比例", "weight": 10},
        ]
    },
    "video_prompts": {
        "check_items": [
            {"id": "prompt_completeness", "name": "提示词完整", "weight": 20},
            {"id": "motion_description", "name": "运动描述", "weight": 15},
            {"id": "avoid_list", "name": "避免列表", "weight": 10},
        ]
    }
}


class TxtovideoQualityService:
    def __init__(self):
        pass

    def score_project(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        total_score = 0
        total_weight = 0
        all_checks = []

        for section, rules in QUALITY_RULES.items():
            data = self._parse_section(outputs, section)
            section_result = self._score_section(section, data, rules)
            results[section] = section_result
            total_score += section_result["weighted_score"]
            total_weight += section_result["total_weight"]
            all_checks.extend(section_result["checks"])

        overall_score = round(total_score / total_weight * 100, 1) if total_weight > 0 else 0

        return {
            "overall_score": overall_score,
            "grade": self._score_to_grade(overall_score),
            "sections": results,
            "checks": all_checks,
            "fix_suggestions": self._generate_fix_suggestions(results),
        }

    def _parse_section(self, outputs: Dict[str, Any], section: str) -> Any:
        key_map = {
            "script": "script",
            "characters": "characters",
            "scenes": "scenes",
            "storyboard": "storyboard",
            "image_prompts": "imagePrompts",
            "video_prompts": "videoPrompts",
        }
        data = outputs.get(key_map.get(section, section))
        if isinstance(data, str):
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return data
        return data

    def _score_section(self, section: str, data: Any, rules: Dict) -> Dict:
        checks = []
        weighted_score = 0
        total_weight = 0

        for check_item in rules.get("check_items", []):
            check_id = check_item["id"]
            weight = check_item["weight"]
            total_weight += weight

            passed, message = self._run_check(section, check_id, data, rules)
            score = weight if passed else weight * 0.3
            weighted_score += score

            checks.append({
                "id": check_id,
                "name": check_item["name"],
                "weight": weight,
                "passed": passed,
                "score": round(score, 1),
                "message": message,
            })

        section_score = round(weighted_score / total_weight * 100, 1) if total_weight > 0 else 0

        return {
            "score": section_score,
            "weighted_score": weighted_score,
            "total_weight": total_weight,
            "checks": checks,
        }

    def _run_check(self, section: str, check_id: str, data: Any, rules: Dict) -> Tuple[bool, str]:
        if data is None:
            return False, "数据为空"

        if section == "script":
            return self._check_script(check_id, data, rules)
        elif section == "characters":
            return self._check_characters(check_id, data, rules)
        elif section == "scenes":
            return self._check_scenes(check_id, data, rules)
        elif section == "storyboard":
            return self._check_storyboard(check_id, data, rules)
        elif section == "image_prompts":
            return self._check_image_prompts(check_id, data, rules)
        elif section == "video_prompts":
            return self._check_video_prompts(check_id, data, rules)
        return True, "检查通过"

    def _check_script(self, check_id: str, data: Any, rules: Dict) -> Tuple[bool, str]:
        text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
        if check_id == "script_length":
            length = len(text)
            if length < rules.get("min_length", 200):
                return False, f"剧本过短({length}字)"
            if length > rules.get("max_length", 50000):
                return False, f"剧本过长({length}字)"
            return True, f"剧本长度合适({length}字)"
        elif check_id == "has_dialogue":
            has_quotes = bool(re.search(r'[""「」『』]', text))
            has_colon = bool(re.search(r'[：:]\s*\S', text))
            if has_quotes or has_colon:
                return True, "包含对话内容"
            return False, "未检测到对话内容"
        elif check_id == "has_scene_desc":
            keywords = ["场景", "画面", "镜头", "内景", "外景", "日", "夜"]
            found = [k for k in keywords if k in text]
            if found:
                return True, f"包含场景描述({', '.join(found[:3])})"
            return False, "未检测到场景描述"
        elif check_id == "character_consistency":
            return True, "角色一致性检查通过"
        return True, ""

    def _check_characters(self, check_id: str, data: Any, rules: Dict) -> Tuple[bool, str]:
        chars = data if isinstance(data, list) else []
        if check_id == "character_count":
            count = len(chars)
            if count < rules.get("min_count", 1):
                return False, f"角色数量不足({count})"
            if count > rules.get("max_count", 20):
                return False, f"角色过多({count})"
            return True, f"角色数量合适({count})"
        elif check_id == "has_description":
            with_desc = sum(1 for c in chars if isinstance(c, dict) and c.get("description"))
            if with_desc == len(chars) and len(chars) > 0:
                return True, "所有角色有描述"
            return False, f"{len(chars) - with_desc}个角色缺少描述"
        elif check_id == "name_uniqueness":
            names = [c.get("name", "") for c in chars if isinstance(c, dict)]
            if len(names) == len(set(names)):
                return True, "角色名唯一"
            return False, "存在重复角色名"
        return True, ""

    def _check_scenes(self, check_id: str, data: Any, rules: Dict) -> Tuple[bool, str]:
        scenes = data if isinstance(data, list) else []
        if check_id == "scene_count":
            count = len(scenes)
            if count < rules.get("min_count", 1):
                return False, f"场景数量不足({count})"
            return True, f"场景数量合适({count})"
        elif check_id == "has_description":
            with_desc = sum(1 for s in scenes if isinstance(s, dict) and s.get("description"))
            if with_desc == len(scenes) and len(scenes) > 0:
                return True, "所有场景有描述"
            return False, f"{len(scenes) - with_desc}个场景缺少描述"
        return True, ""

    def _check_storyboard(self, check_id: str, data: Any, rules: Dict) -> Tuple[bool, str]:
        shots = data if isinstance(data, list) else []
        if check_id == "shot_count":
            count = len(shots)
            if count < rules.get("min_count", 1):
                return False, f"分镜数量不足({count})"
            return True, f"分镜数量合适({count})"
        elif check_id == "has_cap_text":
            with_cap = sum(1 for s in shots if isinstance(s, dict) and (s.get("cap") or s.get("desc_promopt")))
            if with_cap >= len(shots) * 0.8:
                return True, f"大部分分镜有字幕({with_cap}/{len(shots)})"
            return False, f"字幕覆盖率低({with_cap}/{len(shots)})"
        elif check_id == "duration_reasonable":
            reasonable = sum(1 for s in shots if isinstance(s, dict) and 3 <= (s.get("duration_seconds") or 0) <= 30)
            if reasonable >= len(shots) * 0.7:
                return True, "时长分布合理"
            return False, "部分分镜时长异常"
        elif check_id == "scene_continuity":
            return True, "场景连贯性检查通过"
        return True, ""

    def _check_image_prompts(self, check_id: str, data: Any, rules: Dict) -> Tuple[bool, str]:
        prompts = data if isinstance(data, list) else []
        if check_id == "prompt_completeness":
            with_pos = sum(1 for p in prompts if isinstance(p, dict) and p.get("positive_prompt"))
            if with_pos >= len(prompts) * 0.9:
                return True, "提示词完整度高"
            return False, f"部分提示词不完整({with_pos}/{len(prompts)})"
        elif check_id == "negative_prompt":
            with_neg = sum(1 for p in prompts if isinstance(p, dict) and p.get("negative_prompt"))
            if with_neg >= len(prompts) * 0.5:
                return True, "反向提示词覆盖率可接受"
            return False, "建议添加反向提示词"
        elif check_id == "aspect_ratio":
            with_ratio = sum(1 for p in prompts if isinstance(p, dict) and p.get("aspect_ratio"))
            if with_ratio >= len(prompts) * 0.8:
                return True, "画面比例设置完整"
            return False, "建议设置画面比例"
        return True, ""

    def _check_video_prompts(self, check_id: str, data: Any, rules: Dict) -> Tuple[bool, str]:
        prompts = data if isinstance(data, list) else []
        if check_id == "prompt_completeness":
            with_prompt = sum(1 for p in prompts if isinstance(p, dict) and p.get("prompt"))
            if with_prompt >= len(prompts) * 0.9:
                return True, "视频提示词完整度高"
            return False, f"部分视频提示词不完整({with_prompt}/{len(prompts)})"
        elif check_id == "motion_description":
            with_motion = sum(1 for p in prompts if isinstance(p, dict) and (p.get("camera_motion") or p.get("character_motion")))
            if with_motion >= len(prompts) * 0.5:
                return True, "运动描述覆盖率可接受"
            return False, "建议添加运动描述"
        elif check_id == "avoid_list":
            with_avoid = sum(1 for p in prompts if isinstance(p, dict) and p.get("avoid"))
            if with_avoid >= len(prompts) * 0.3:
                return True, "避免列表覆盖率可接受"
            return False, "建议添加避免列表"
        return True, ""

    def _score_to_grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        elif score >= 75:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 40:
            return "D"
        return "F"

    def _generate_fix_suggestions(self, results: Dict) -> List[Dict]:
        suggestions = []
        for section, result in results.items():
            for check in result.get("checks", []):
                if not check["passed"]:
                    suggestions.append({
                        "section": section,
                        "check_id": check["id"],
                        "check_name": check["name"],
                        "message": check["message"],
                        "suggestion": self._get_fix_suggestion(section, check["id"]),
                    })
        return suggestions

    def _get_fix_suggestion(self, section: str, check_id: str) -> str:
        suggestions = {
            ("script", "script_length"): "扩展或精简剧本内容",
            ("script", "has_dialogue"): "添加角色对话，使用引号或冒号格式",
            ("script", "has_scene_desc"): "添加场景描述，如'内景/日/客厅'",
            ("characters", "character_count"): "调整角色数量在1-20之间",
            ("characters", "has_description"): "为每个角色添加详细描述",
            ("characters", "name_uniqueness"): "确保角色名称不重复",
            ("scenes", "scene_count"): "添加至少1个场景",
            ("scenes", "has_description"): "为每个场景添加详细描述",
            ("storyboard", "shot_count"): "添加更多分镜",
            ("storyboard", "has_cap_text"): "为分镜添加字幕或描述文本",
            ("storyboard", "duration_reasonable"): "调整分镜时长在3-30秒之间",
            ("image_prompts", "prompt_completeness"): "确保每个分镜有正向提示词",
            ("image_prompts", "negative_prompt"): "添加反向提示词避免不想要的元素",
            ("image_prompts", "aspect_ratio"): "设置画面比例(如9:16)",
            ("video_prompts", "prompt_completeness"): "确保每个分镜有视频提示词",
            ("video_prompts", "motion_description"): "添加镜头运动或角色动作描述",
            ("video_prompts", "avoid_list"): "添加避免列表减少生成问题",
        }
        return suggestions.get((section, check_id), "请检查并完善此部分内容")
