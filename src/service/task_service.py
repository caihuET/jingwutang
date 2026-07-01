"""任务服务"""
from src.repository.task_repo import TaskRepository
from src.utils.errors import GameException, ErrorCode


class TaskService:
    def __init__(self, db):
        self.repo = TaskRepository(db)

    def get_tasks(self, player_id: int, task_type: int = None) -> list:
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
