"""任务 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.task_service import TaskService

router = APIRouter()


@router.get("/task/list")
def get_tasks(task_type: int = None, player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": TaskService(db).get_tasks(player_id, task_type), "message": "ok"}


class ClaimRequest(BaseModel):
    task_id: int


@router.post("/task/claim")
def claim_reward(req: ClaimRequest, player_id: int = 1, db: Session = Depends(get_db)):
    result = TaskService(db).claim_reward(player_id, req.task_id)
    return {"code": 0, "data": result, "message": "领取成功"}
