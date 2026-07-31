"""装备 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.equipment_service import EquipmentService

router = APIRouter()


@router.get("/equipment/list")
def get_equipment(player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": EquipmentService(db).get_equipment(player_id), "message": "ok"}


@router.get("/equipment/catalog")
def get_catalog(db: Session = Depends(get_db)):
    """装备图鉴（按品质分组）"""
    return {"code": 0, "data": EquipmentService(db).get_catalog(), "message": "ok"}


class EquipAction(BaseModel):
    equip_id: int


@router.post("/equipment/equip")
def equip_item(req: EquipAction, player_id: int = 1, db: Session = Depends(get_db)):
    EquipmentService(db).equip(player_id, req.equip_id)
    return {"code": 0, "data": None, "message": "穿戴成功"}


@router.post("/equipment/unequip")
def unequip_item(req: EquipAction, player_id: int = 1, db: Session = Depends(get_db)):
    EquipmentService(db).unequip(player_id, req.equip_id)
    return {"code": 0, "data": None, "message": "卸下成功"}


@router.post("/equipment/enhance")
def enhance_item(req: EquipAction, player_id: int = 1, db: Session = Depends(get_db)):
    result = EquipmentService(db).enhance(player_id, req.equip_id)
    return {"code": 0, "data": result, "message": "强化完成"}

@router.post("/equipment/sell")
def sell_item(req: EquipAction, player_id: int = 1, db: Session = Depends(get_db)):
    """出售装备"""
    result = EquipmentService(db).sell(player_id, req.equip_id)
    return {"code": 0, "data": result, "message": "出售成功"}
