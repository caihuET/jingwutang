"""经脉 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.meridian_service import MeridianService


router = APIRouter()


class BreakthroughRequest(BaseModel):
    meridian_id: int


@router.get("/meridian/list")
def get_meridians(player_id: int = 1, db: Session = Depends(get_db)):
    """获取经脉状态"""
    return {"code": 0, "data": MeridianService(db).get_meridians(player_id), "message": "ok"}


@router.post("/meridian/breakthrough")
def breakthrough(req: BreakthroughRequest, player_id: int = 1, db: Session = Depends(get_db)):
    """打通穴位"""
    result = MeridianService(db).breakthrough(player_id, req.meridian_id)
    return {"code": 0, "data": result, "message": "打通成功"}
