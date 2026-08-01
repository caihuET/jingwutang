"""任务数据访问"""
from src.models.task import PlayerTask, TaskDefinition
from sqlalchemy import and_
import datetime
from typing import List, Optional


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
            daily_reset_date=datetime.date.today() if task_def.daily_refresh else None,
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

    def get_task_defs_by_type(self, task_type: int) -> list:
        return self.db.query(TaskDefinition).filter(
            TaskDefinition.task_type == task_type
        ).order_by(TaskDefinition.sort_order).all()

    def get_player_task_by_def(self, player_id: int, task_def_id: int):
        return self.db.query(PlayerTask).filter(and_(
            PlayerTask.player_id == player_id,
            PlayerTask.task_id == task_def_id
        )).first()

    def get_completed_tasks(self, player_id: int) -> list:
        return self.db.query(PlayerTask).filter(and_(
            PlayerTask.player_id == player_id,
            PlayerTask.status >= 1
        )).all()

    def delete_player_tasks(self, player_id: int, task_type: int):
        defs = self.get_task_defs_by_type(task_type)
        def_ids = [d.id for d in defs]
        if not def_ids:
            return
        self.db.query(PlayerTask).filter(and_(
            PlayerTask.player_id == player_id,
            PlayerTask.task_id.in_(def_ids)
        )).delete(synchronize_session=False)
        self.db.commit()

    def create_player_tasks_batch(self, player_id: int, task_defs: list):
        for td in task_defs:
            existing = self.get_player_task_by_def(player_id, td.id)
            if not existing:
                pt = PlayerTask(
                    player_id=player_id,
                    task_id=td.id,
                    progress=0,
                    target=td.requirement_value,
                    status=0,
                    daily_reset_date=datetime.date.today() if td.daily_refresh else None,
                )
                self.db.add(pt)
        self.db.commit()

    def get_task_defs_by_ids(self, ids: list) -> dict:
        q = self.db.query(TaskDefinition).filter(TaskDefinition.id.in_(ids)).all()
        return {t.id: t for t in q}
