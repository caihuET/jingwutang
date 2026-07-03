"""角色 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.player_service import PlayerService
from src.service.meridian_service import MeridianService

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


class AllocateAttributeRequest(BaseModel):
    player_id: int
    strength: int = 0
    agility: int = 0
    constitution: int = 0
    spirit: int = 0


@router.post("/player/allocate_attr")
def allocate_attribute(req: AllocateAttributeRequest, db: Session = Depends(get_db)):
    """分配属性点"""
    result = PlayerService(db).allocate_attribute(req.player_id, req.strength, req.agility, req.constitution, req.spirit)
    return {"code": 0, "data": result, "message": "分配成功"}


@router.post("/player/buy_stamina")
def buy_stamina(req: BuyStaminaRequest, db: Session = Depends(get_db)):
    """购买体力"""
    result = PlayerService(db).buy_stamina(req.player_id)
    return {"code": 0, "data": result, "message": "购买成功"}


class MeridianBreakthroughRequest(BaseModel):
    meridian_id: int


@router.get("/meridian/list")
def get_meridians(player_id: int = 1, db: Session = Depends(get_db)):
    """获取经脉状态"""
    return {"code": 0, "data": MeridianService(db).get_meridians(player_id), "message": "ok"}


@router.post("/meridian/breakthrough")
def breakthrough(req: MeridianBreakthroughRequest, player_id: int = 1, db: Session = Depends(get_db)):
    """打通穴位"""
    result = MeridianService(db).breakthrough(player_id, req.meridian_id)
    return {"code": 0, "data": result, "message": "打通成功"}
