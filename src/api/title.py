"""称号 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.title_service import TitleService

router = APIRouter()


@router.get("/title/list")
def title_list(player_id: int = 1, db: Session = Depends(get_db)):
    """获取已获得称号列表"""
    return {"code": 0, "data": TitleService(db).get_titles(player_id), "message": "ok"}


class TitleIdRequest(BaseModel):
    title_id: int


@router.post("/title/equip")
def title_equip(req: TitleIdRequest, player_id: int = 1, db: Session = Depends(get_db)):
    """佩戴称号"""
    result = TitleService(db).equip(player_id, req.title_id)
    return {"code": 0, "data": result, "message": "佩戴成功"}


@router.post("/title/unequip")
def title_unequip(req: TitleIdRequest, player_id: int = 1, db: Session = Depends(get_db)):
    """卸下称号"""
    result = TitleService(db).unequip(player_id, req.title_id)
    return {"code": 0, "data": result, "message": "卸下成功"}
