"""技能 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.skill_service import SkillService

router = APIRouter()


class SlotRequest(BaseModel):
    skill_ids: list


@router.get("/skill/list")
def get_skills(player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": SkillService(db).get_skills(player_id), "message": "ok"}


@router.post("/skill/slot")
def set_slots(req: SlotRequest, player_id: int = 1, db: Session = Depends(get_db)):
    SkillService(db).set_slots(player_id, req.skill_ids)
    return {"code": 0, "data": None, "message": "设置成功"}
