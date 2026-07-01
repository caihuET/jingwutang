"""任务数据访问"""
from src.models.task import PlayerTask, TaskDefinition
from sqlalchemy import and_
import datetime


class TaskRepository:
    def __init__(self, db):
        self.db = db

    def get_player_tasks(self, player_id: int, task_type: int = None):
        q = self.db.query(PlayerTask).filter(PlayerTask.player_id == player_id)
        if task_type:
            q = q.join(TaskDefinition).filter(TaskDefinition.task_type == task_type)
        return q.all()

    def get_task_def(self, task_id: int):
        return self.db.query(TaskDefinition).filter(TaskDefinition.id == task_id).first()

    def create_player_task(self, player_id: int, task_def):
        pt = PlayerTask(
            player_id=player_id,
            task_id=task_def.id,
            progress=0,
            target=task_def.requirement_value,
            status=0,
        )
        self.db.add(pt)
        self.db.commit()
        return pt

    def update_progress(self, player_task_id: int, progress: int):
        pt = self.db.query(PlayerTask).filter(PlayerTask.id == player_task_id).first()
        if pt:
            pt.progress = min(progress, pt.target)
            if pt.progress >= pt.target and pt.status == 0:
                pt.status = 1
            self.db.commit()
