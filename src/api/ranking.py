"""排行 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.ranking_service import RankingService

router = APIRouter()


@router.get("/ranking/level")
def ranking_level(player_id: int = 1, page: int = 1, size: int = 20,
                  db: Session = Depends(get_db)):
    size = min(max(1, size), 100)
    data = RankingService(db).get_ranking("level", player_id, page, size)
    return {"code": 0, "data": data, "message": "ok"}


@router.get("/ranking/combat")
def ranking_combat(player_id: int = 1, page: int = 1, size: int = 20,
                   db: Session = Depends(get_db)):
    size = min(max(1, size), 100)
    data = RankingService(db).get_ranking("combat", player_id, page, size)
    return {"code": 0, "data": data, "message": "ok"}


@router.get("/ranking/marquee")
def ranking_marquee(db: Session = Depends(get_db)):
    return {"code": 0, "data": RankingService(db).get_marquee(), "message": "ok"}
