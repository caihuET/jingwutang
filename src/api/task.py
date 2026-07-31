"""浠诲姟 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.task_service import TaskService

router = APIRouter()


class AcceptRequest(BaseModel):
    task_id: int
    player_id: int = 1


@router.get("/task/list")
def get_tasks(task_type: int = None, player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": TaskService(db).get_tasks(player_id, task_type), "message": "ok"}


class ClaimRequest(BaseModel):
    task_id: int
    player_id: int = 1


@router.post("/task/claim")
def claim_reward(req: ClaimRequest, db: Session = Depends(get_db)):
    result = TaskService(db).claim_reward(req.player_id, req.task_id)
    return {"code": 0, "data": result, "message": "棰嗗彇鎴愬姛"}


@router.post("/task/accept")
def accept_task(req: AcceptRequest, db: Session = Depends(get_db)):
    result = TaskService(db).accept_task(req.player_id, req.task_id)
    return {"code": 0, "data": result, "message": "棰嗗彇鎴愬姛"}

