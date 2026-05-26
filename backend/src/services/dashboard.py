"""
仪表盘数据服务 - 提供用户统计和概览数据

提供服务：
- 用户综合统计信息
- 最近项目列表
- 最近活动记录
- 任务队列状态
- 成本估算

设计原则：
- 使用BaseService统一管理数据库会话
- 优化查询性能，使用聚合查询
- 方法职责单一，保持简洁
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.models.project import Project, ProjectStatus
from src.models.chapter import Chapter, ChapterStatus
from src.models.paragraph import Paragraph
from src.models.sentence import Sentence, SentenceStatus
from src.services.base import BaseService

logger = get_logger(__name__)


class DashboardService(BaseService):
    """
    仪表盘数据服务
    
    负责提供用户仪表盘所需的各类统计数据和概览信息。
    所有数据库操作都通过基类提供的会话管理功能进行。
    """

    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        初始化仪表盘服务
        
        Args:
            db_session: 可选的数据库会话
        """
        super().__init__(db_session)
        logger.debug(f"DashboardService 初始化完成")

    async def get_user_statistics(self, owner_id: str) -> Dict[str, Any]:
        """
        获取用户综合统计信息
        
        Args:
            owner_id: 用户ID
            
        Returns:
            包含各类统计数据的字典
        """
        try:
            # 1. 项目统计
            project_stats = await self._get_project_statistics(owner_id)
            
            # 2. 内容统计
            content_stats = await self._get_content_statistics(owner_id)
            
            # 3. 生成统计
            generation_stats = await self._get_generation_statistics(owner_id)
            
            # 4. 任务统计
            task_stats = await self._get_task_statistics(owner_id)
            
            # 5. 成本估算
            cost_estimate = await self._estimate_total_cost(owner_id)
            
            return {
                "projects": project_stats,
                "content": content_stats,
                "generation": generation_stats,
                "tasks": task_stats,
                "cost": cost_estimate,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取用户统计信息失败: {e}")
            raise

    async def _get_project_statistics(self, owner_id: str) -> Dict[str, Any]:
        """获取项目统计"""
        # 总项目数
        total_query = select(func.count(Project.id)).filter(Project.owner_id == owner_id)
        total_result = await self.execute(total_query)
        total_projects = total_result.scalar() or 0
        
        # 按状态分组统计
        status_query = select(
            Project.status,
            func.count(Project.id)
        ).filter(Project.owner_id == owner_id).group_by(Project.status)
        
        status_result = await self.execute(status_query)
        status_distribution = {row[0]: row[1] for row in status_result}
        
        return {
            "total": total_projects,
            "by_status": status_distribution,
            "uploaded": status_distribution.get(ProjectStatus.UPLOADED.value, 0),
            "parsing": status_distribution.get(ProjectStatus.PARSING.value, 0),
            "parsed": status_distribution.get(ProjectStatus.PARSED.value, 0),
            "generating": status_distribution.get(ProjectStatus.GENERATING.value, 0),
            "completed": status_distribution.get(ProjectStatus.COMPLETED.value, 0),
            "failed": status_distribution.get(ProjectStatus.FAILED.value, 0),
            "archived": status_distribution.get(ProjectStatus.ARCHIVED.value, 0)
        }

    async def _get_content_statistics(self, owner_id: str) -> Dict[str, Any]:
        """获取内容统计"""
        # 章节统计
        chapter_query = select(func.count(Chapter.id)).where(
            Chapter.project_id.in_(
                select(Project.id).where(Project.owner_id == owner_id)
            )
        )
        chapter_result = await self.execute(chapter_query)
        total_chapters = chapter_result.scalar() or 0
        
        # 段落统计
        paragraph_query = select(func.count(Paragraph.id)).where(
            Paragraph.chapter_id.in_(
                select(Chapter.id).where(
                    Chapter.project_id.in_(
                        select(Project.id).where(Project.owner_id == owner_id)
                    )
                )
            )
        )
        paragraph_result = await self.execute(paragraph_query)
        total_paragraphs = paragraph_result.scalar() or 0
        
        # 句子统计
        sentence_query = select(func.count(Sentence.id)).where(
            Sentence.paragraph_id.in_(
                select(Paragraph.id).where(
                    Paragraph.chapter_id.in_(
                        select(Chapter.id).where(
                            Chapter.project_id.in_(
                                select(Project.id).where(Project.owner_id == owner_id)
                            )
                        )
                    )
                )
            )
        )
        sentence_result = await self.execute(sentence_query)
        total_sentences = sentence_result.scalar() or 0
        
        return {
            "total_chapters": total_chapters,
            "total_paragraphs": total_paragraphs,
            "total_sentences": total_sentences
        }

    async def _get_generation_statistics(self, owner_id: str) -> Dict[str, Any]:
        """获取生成统计"""
        # 已生成图片数量
        image_query = select(func.count(Sentence.id)).where(
            Sentence.paragraph_id.in_(
                select(Paragraph.id).where(
                    Paragraph.chapter_id.in_(
                        select(Chapter.id).where(
                            Chapter.project_id.in_(
                                select(Project.id).where(Project.owner_id == owner_id)
                            )
                        )
                    )
                )
            ),
            Sentence.image_url.isnot(None)
        )
        image_result = await self.execute(image_query)
        generated_images = image_result.scalar() or 0
        
        # 已生成音频数量
        audio_query = select(func.count(Sentence.id)).where(
            Sentence.paragraph_id.in_(
                select(Paragraph.id).where(
                    Paragraph.chapter_id.in_(
                        select(Chapter.id).where(
                            Chapter.project_id.in_(
                                select(Project.id).where(Project.owner_id == owner_id)
                            )
                        )
                    )
                )
            ),
            Sentence.audio_url.isnot(None)
        )
        audio_result = await self.execute(audio_query)
        generated_audios = audio_result.scalar() or 0
        
        # 已生成视频数量（章节级别）
        video_query = select(func.count(Chapter.id)).where(
            Chapter.project_id.in_(
                select(Project.id).where(Project.owner_id == owner_id)
            ),
            Chapter.video_url.isnot(None)
        )
        video_result = await self.execute(video_query)
        generated_videos = video_result.scalar() or 0
        
        return {
            "generated_images": generated_images,
            "generated_audios": generated_audios,
            "generated_videos": generated_videos
        }

    async def _get_task_statistics(self, owner_id: str) -> Dict[str, Any]:
        """获取任务统计"""
        # 进行中的项目（parsing或generating状态）
        running_query = select(func.count(Project.id)).where(
            Project.owner_id == owner_id,
            or_(
                Project.status == ProjectStatus.PARSING.value,
                Project.status == ProjectStatus.GENERATING.value
            )
        )
        running_result = await self.execute(running_query)
        running_tasks = running_result.scalar() or 0
        
        # 进行中的章节生成任务
        chapter_generating_query = select(func.count(Chapter.id)).where(
            Chapter.project_id.in_(
                select(Project.id).where(Project.owner_id == owner_id)
            ),
            or_(
                Chapter.status == ChapterStatus.GENERATING_PROMPTS.value,
                Chapter.status == ChapterStatus.GENERATING_VIDEO.value
            )
        )
        chapter_result = await self.execute(chapter_generating_query)
        chapter_tasks = chapter_result.scalar() or 0
        
        return {
            "running_tasks": running_tasks + chapter_tasks,
            "project_tasks": running_tasks,
            "chapter_tasks": chapter_tasks
        }

    async def _estimate_total_cost(self, owner_id: str) -> Dict[str, Any]:
        """估算总成本 - 仅统计已生成的内容"""
        # 获取生成统计
        gen_stats = await self._get_generation_statistics(owner_id)
        
        # 成本单价（可以从配置文件读取）
        IMAGE_COST = 0.04  # 每张图片成本
        AUDIO_COST = 0.02  # 每条音频成本
        PROMPT_COST = 0.001  # 每次提示词生成成本
        
        # 计算已生成内容的成本
        image_cost = gen_stats["generated_images"] * IMAGE_COST
        audio_cost = gen_stats["generated_audios"] * AUDIO_COST
        
        # 提示词成本 - 只统计已生成提示词的句子
        prompt_query = select(func.count(Sentence.id)).where(
            Sentence.paragraph_id.in_(
                select(Paragraph.id).where(
                    Paragraph.chapter_id.in_(
                        select(Chapter.id).where(
                            Chapter.project_id.in_(
                                select(Project.id).where(Project.owner_id == owner_id)
                            )
                        )
                    )
                )
            ),
            Sentence.image_prompt.isnot(None)  # 只统计已生成提示词的
        )
        prompt_result = await self.execute(prompt_query)
        generated_prompts = prompt_result.scalar() or 0
        prompt_cost = generated_prompts * PROMPT_COST
        
        total_cost = image_cost + audio_cost + prompt_cost
        
        return {
            "total": round(total_cost, 2),
            "image_cost": round(image_cost, 2),
            "audio_cost": round(audio_cost, 2),
            "prompt_cost": round(prompt_cost, 2),
            "currency": "CNY",
            "is_estimate": True,  # 标记这是估算值
            "generated_count": {  # 已生成数量明细
                "images": gen_stats["generated_images"],
                "audios": gen_stats["generated_audios"],
                "prompts": generated_prompts
            }
        }

    async def get_recent_projects(self, owner_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取最近的项目列表
        
        Args:
            owner_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            最近项目列表
        """
        query = select(Project).filter(
            Project.owner_id == owner_id
        ).order_by(desc(Project.updated_at)).limit(limit)
        
        result = await self.execute(query)
        projects = result.scalars().all()

        if projects:
            chapter_counts_stmt = select(
                Chapter.project_id, func.count(Chapter.id)
            ).where(
                Chapter.project_id.in_([p.id for p in projects])
            ).group_by(Chapter.project_id)
            chapter_result = await self.execute(chapter_counts_stmt)
            chapter_counts = dict(chapter_result.all())
        else:
            chapter_counts = {}

        project_list = []
        for project in projects:
            chapter_count = chapter_counts.get(project.id, 0)
            
            project_list.append({
                "id": str(project.id),
                "title": project.title,
                "status": project.status,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                "chapter_count": chapter_count,
                "word_count": project.word_count or 0
            })
        
        return project_list

    async def get_recent_activities(self, owner_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的活动记录
        
        Args:
            owner_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            最近活动列表
        """
        activities = []
        
        # 1. 最近创建的项目
        recent_projects_query = select(Project).filter(
            Project.owner_id == owner_id
        ).order_by(desc(Project.created_at)).limit(limit)
        
        projects_result = await self.execute(recent_projects_query)
        recent_projects = projects_result.scalars().all()
        
        for project in recent_projects:
            activities.append({
                "id": str(project.id),
                "type": "project_created",
                "description": f"创建项目: {project.title}",
                "timestamp": project.created_at.isoformat() if project.created_at else None,
                "related_id": str(project.id),
                "status": project.status
            })
        
        # 2. 最近确认的章节
        recent_chapters_query = select(Chapter).where(
            Chapter.project_id.in_(
                select(Project.id).where(Project.owner_id == owner_id)
            ),
            Chapter.is_confirmed == True
        ).order_by(desc(Chapter.confirmed_at)).limit(limit)
        
        chapters_result = await self.execute(recent_chapters_query)
        recent_chapters = chapters_result.scalars().all()
        
        for chapter in recent_chapters:
            if chapter.confirmed_at:
                activities.append({
                    "id": str(chapter.id),
                    "type": "chapter_confirmed",
                    "description": f"确认章节: {chapter.title}",
                    "timestamp": chapter.confirmed_at.isoformat(),
                    "related_id": str(chapter.project_id),
                    "status": chapter.status
                })
        
        # 3. 最近生成的视频
        recent_videos_query = select(Chapter).where(
            Chapter.project_id.in_(
                select(Project.id).where(Project.owner_id == owner_id)
            ),
            Chapter.video_url.isnot(None)
        ).order_by(desc(Chapter.updated_at)).limit(limit)
        
        videos_result = await self.execute(recent_videos_query)
        recent_videos = videos_result.scalars().all()
        
        for chapter in recent_videos:
            activities.append({
                "id": str(chapter.id),
                "type": "video_generated",
                "description": f"生成视频: {chapter.title}",
                "timestamp": chapter.updated_at.isoformat() if chapter.updated_at else None,
                "related_id": str(chapter.project_id),
                "status": chapter.status
            })
        
        # 按时间排序并限制数量
        activities.sort(key=lambda x: x["timestamp"] or "", reverse=True)
        return activities[:limit]

    async def get_task_queue_status(self, owner_id: str) -> Dict[str, Any]:
        """
        获取任务队列状态
        
        Args:
            owner_id: 用户ID
            
        Returns:
            任务队列状态信息
        """
        # 获取进行中的项目
        running_projects_query = select(Project).where(
            Project.owner_id == owner_id,
            or_(
                Project.status == ProjectStatus.PARSING.value,
                Project.status == ProjectStatus.GENERATING.value
            )
        ).order_by(desc(Project.updated_at))
        
        projects_result = await self.execute(running_projects_query)
        running_projects = projects_result.scalars().all()
        
        tasks = []
        for project in running_projects:
            tasks.append({
                "id": str(project.id),
                "type": "project_processing",
                "title": project.title,
                "status": project.status,
                "progress": project.processing_progress or 0,
                "started_at": project.updated_at.isoformat() if project.updated_at else None
            })
        
        # 获取进行中的章节生成任务
        generating_chapters_query = select(Chapter).where(
            Chapter.project_id.in_(
                select(Project.id).where(Project.owner_id == owner_id)
            ),
            or_(
                Chapter.status == ChapterStatus.GENERATING_PROMPTS.value,
                Chapter.status == ChapterStatus.GENERATING_VIDEO.value
            )
        ).order_by(desc(Chapter.updated_at))
        
        chapters_result = await self.execute(generating_chapters_query)
        generating_chapters = chapters_result.scalars().all()
        
        for chapter in generating_chapters:
            tasks.append({
                "id": str(chapter.id),
                "type": "chapter_generating",
                "title": chapter.title,
                "status": chapter.status,
                "progress": 0,  # 章节没有进度字段
                "started_at": chapter.updated_at.isoformat() if chapter.updated_at else None
            })
        
        return {
            "running_tasks": len(tasks),
            "tasks": tasks
        }


__all__ = [
    "DashboardService",
]
