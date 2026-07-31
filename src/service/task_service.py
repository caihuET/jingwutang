"""任务服务"""
from src.repository.task_repo import TaskRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.utils.constants import TaskType
from src.service.title_service import TitleService
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
        """获取所有任务（可用+已领取）"""
        from src.models.task import TaskDefinition
        q = self.repo.db.query(TaskDefinition)
        if task_type:
            q = q.filter(TaskDefinition.task_type == task_type)
        defs = q.order_by(TaskDefinition.sort_order).all()
        pts = self.repo.get_player_tasks(player_id)
        pt_map = {pt.task_id: pt for pt in pts}
        result = []
        for td in defs:
            pt = pt_map.get(td.id)
            if pt:
                result.append({
                    "id": pt.id, "task_id": td.id, "name": td.name,
                    "description": td.description,
                    "progress": pt.progress, "target": pt.target,
                    "status": pt.status, "accepted": True,
                    "rewards": {"exp": td.reward_exp, "gold": td.reward_gold, "reputation": td.reward_reputation},
                })
            else:
                result.append({
                    "id": None, "task_id": td.id, "name": td.name,
                    "description": td.description,
                    "progress": 0, "target": td.requirement_value,
                    "status": -1, "accepted": False,
                    "rewards": {"exp": td.reward_exp, "gold": td.reward_gold, "reputation": td.reward_reputation},
                })
        return result

    def claim_reward(self, player_id: int, task_id: int) -> dict:
        """领取任务奖励"""
        from src.models.player import Player
        pt = self.repo.get_player_task_by_def(player_id, task_id)
        if not pt:
            pt = self.repo.get_player_tasks(player_id)
            pt = next((t for t in pt if t.task_id == task_id), None)
        if not pt:
            raise GameException(ErrorCode.PARAM_INVALID, "任务不存在")
        if pt.status != 1:
            raise GameException(ErrorCode.PARAM_INVALID, "任务未完成")
        td = self.repo.get_task_def(task_id)
        # 发放奖励
        player = self.repo.db.query(Player).filter(Player.id == player_id).first()
        if player and td:
            player.exp += td.reward_exp or 0
            player.gold += td.reward_gold or 0
            player.reputation += td.reward_reputation or 0
            if td.reward_title_id:
                TitleService(self.repo.db).grant(player_id, td.reward_title_id, auto_equip=False)
        pt.status = 2
        self.repo.db.commit()
        return {
            "exp": td.reward_exp if td else 0,
            "gold": td.reward_gold if td else 0,
            "reputation": td.reward_reputation if td else 0,
            "title_id": td.reward_title_id if td else None,
        }

    
    def accept_task(self, player_id: int, task_id: int) -> dict:
        """接受任务"""
        td = self.repo.get_task_def(task_id)
        if not td:
            from src.utils.errors import GameException
            from src.utils.constants import ErrorCode
            raise GameException(ErrorCode.PARAM_INVALID, "任务不存在")
        # 检查等级要求
        from src.repository.player_repo import PlayerRepository
        player = PlayerRepository(self.repo.db).get_by_id(player_id)
        if player and td.min_level and player.level < td.min_level:
            raise GameException(ErrorCode.PARAM_INVALID, "等级不足，无法接受此任务")
        if player and td.max_level and player.level > td.max_level:
            raise GameException(ErrorCode.PARAM_INVALID, "等级过高")
        existing = self.repo.get_player_task_by_def(player_id, task_id)
        if existing:
            raise GameException(ErrorCode.PARAM_INVALID, "任务已领取")
        pt = self.repo.create_player_task(player_id, td)
        return {"task_id": pt.task_id, "status": pt.status}
