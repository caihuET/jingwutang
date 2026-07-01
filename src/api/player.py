"""角色 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.player_service import PlayerService

router = APIRouter()


class CreatePlayerRequest(BaseModel):
    name: str
    gender: int
    school_id: int


class PlayerInfoRequest(BaseModel):
    player_id: int


@router.post("/player/create")
def create_player(req: CreatePlayerRequest, db: Session = Depends(get_db)):
    """创建角色"""
    result = PlayerService(db).create(0, req.name, req.gender, req.school_id)
    return {"code": 0, "data": result, "message": "创建成功"}


@router.get("/player/info")
def get_player_info(player_id: int, db: Session = Depends(get_db)):
    """获取角色信息"""
    result = PlayerService(db).get_info(player_id)
    return {"code": 0, "data": result, "message": "ok"}
