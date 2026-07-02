"""任务服务"""
from src.repository.task_repo import TaskRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.utils.constants import TaskType
from src.models.task import TaskDefinition
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


REQ_TYPES = [
    "reach_level", "kill_monster", "kill_boss", "pve_battle",
    "equip_item", "enhance_equip", "embed_gem", "breakthrough",
    "arena_battle", "add_friend", "join_guild", "skill_level",
]


class TaskService:
    def __init__(self, db):
        self.repo = TaskRepository(db)

    def check_progress(self, player_id: int, req_type: str, value: int = 1):
        """更新玩家任务进度（各模块调用）"""
        if req_type not in REQ_TYPES:
            return
        tasks = self.repo.get_player_tasks(player_id)
        for pt in tasks:
            if pt.status != 0:
                continue
            td = self.repo.get_task_def(pt.task_id)
            if not td or td.requirement_type != req_type:
                continue
            self.repo.update_progress(pt.id, pt.progress + value)

    def get_tasks(self, player_id: int, task_type: int = None) -> list:
        """获取玩家任务列表"""
        tasks = self.repo.get_player_tasks(player_id, task_type)
        if not tasks:
            self.auto_assign_tasks(player_id)
            tasks = self.repo.get_player_tasks(player_id, task_type)
        result = []
        for pt in tasks:
            td = self.repo.get_task_def(pt.task_id)
            result.append({
                "id": pt.id,
                "task_id": pt.task_id,
                "name": td.name if td else "未知",
                "description": td.description if td else "",
                "progress": pt.progress,
                "target": pt.target,
                "status": pt.status,
                "rewards": {
                    "exp": td.reward_exp if td else 0,
                    "gold": td.reward_gold if td else 0,
                    "reputation": td.reward_reputation if td else 0,
                }
            })
        return result

    def claim_reward(self, player_id: int, task_id: int) -> dict:
        """领取任务奖励"""
        pt = self.repo.get_player_tasks(player_id)
        pt = next((t for t in pt if t.task_id == task_id), None)
        if not pt:
            raise GameException(ErrorCode.PARAM_INVALID, "任务不存在")
        if pt.status != 1:
            raise GameException(ErrorCode.PARAM_INVALID, "任务未完成")
        td = self.repo.get_task_def(task_id)
        pt.status = 2
        self.repo.db.commit()
        return {
            "exp": td.reward_exp if td else 0,
            "gold": td.reward_gold if td else 0,
            "reputation": td.reward_reputation if td else 0,
        }

    def auto_assign_tasks(self, player_id: int, level: int = 1):
        """自动分配任务"""
        # 主线: 分配下一个未完成的主线
        main_defs = self.repo.get_task_defs_by_type(TaskType.MAIN)
        completed = set(pt.task_id for pt in self.repo.get_completed_tasks(player_id))
        player_tasks = self.repo.get_player_tasks(player_id)
        assigned = set(pt.task_id for pt in player_tasks)

        for td in main_defs:
            if td.id not in completed and td.id not in assigned:
                self.repo.create_player_task(player_id, td)
                break

        # 日常: 分配未接取的
        daily_defs = self.repo.get_task_defs_by_type(TaskType.DAILY)
        for td in daily_defs:
            if td.id not in assigned:
                self.repo.create_player_task(player_id, td)

        # 成就: 分配未接取的
        achieve_defs = self.repo.get_task_defs_by_type(TaskType.ACHIEVEMENT)
        for td in achieve_defs:
            if td.id not in assigned:
                self.repo.create_player_task(player_id, td)

    def daily_refresh(self, player_id: int):
        """每日刷新: 重置日常任务"""
        self.repo.delete_player_tasks(player_id, TaskType.DAILY)
        self.auto_assign_tasks(player_id)
