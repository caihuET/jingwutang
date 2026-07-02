"""战斗 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.battle_service import BattleService

router = APIRouter()


class BattleRequest(BaseModel):
    map_id: int
    player_id: int = 1


@router.post("/battle/pve")
def pve_battle(req: BattleRequest, db: Session = Depends(get_db)):
    result = BattleService(db).pve_battle(req.player_id, req.map_id)
    return {"code": 0, "data": result, "message": "ok"}
