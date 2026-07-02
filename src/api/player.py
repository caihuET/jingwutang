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
    user_id: int


class PlayerInfoRequest(BaseModel):
    player_id: int


@router.post("/player/create")
def create_player(req: CreatePlayerRequest, db: Session = Depends(get_db)):
    """创建角色"""
    result = PlayerService(db).create(req.user_id, req.name, req.gender, req.school_id)
    return {"code": 0, "data": result, "message": "创建成功"}


@router.get("/player/info")
def get_player_info(player_id: int, db: Session = Depends(get_db)):
    """获取角色信息"""
    result = PlayerService(db).get_info(player_id)
    return {"code": 0, "data": result, "message": "ok"}


@router.get("/player/by_user")
def get_player_by_user(user_id: int, db: Session = Depends(get_db)):
    """按用户ID查询角色"""
    result = PlayerService(db).get_by_user(user_id)
    return {"code": 0, "data": result, "message": "ok"}


class BuyStaminaRequest(BaseModel):
    player_id: int = 1


@router.post("/player/buy_stamina")
def buy_stamina(req: BuyStaminaRequest, db: Session = Depends(get_db)):
    """购买体力"""
    result = PlayerService(db).buy_stamina(req.player_id)
    return {"code": 0, "data": result, "message": "购买成功"}
