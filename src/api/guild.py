"""帮派 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.guild_service import GuildService

router = APIRouter()


@router.get("/guild/list")
def guild_list(db: Session = Depends(get_db)):
    return {"code": 0, "data": GuildService(db).list_guilds(), "message": "ok"}


@router.get("/guild/info")
def guild_info(player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": GuildService(db).get_info(player_id), "message": "ok"}


class GuildCreate(BaseModel):
    name: str
    announcement: str = ""


@router.post("/guild/create")
def guild_create(req: GuildCreate, player_id: int = 1, db: Session = Depends(get_db)):
    result = GuildService(db).create(player_id, req.name, req.announcement)
    return {"code": 0, "data": result, "message": "创建成功"}


class GuildJoin(BaseModel):
    guild_id: int


@router.post("/guild/join")
def guild_join(req: GuildJoin, player_id: int = 1, db: Session = Depends(get_db)):
    GuildService(db).join(player_id, req.guild_id)
    return {"code": 0, "data": None, "message": "加入成功"}


@router.post("/guild/leave")
def guild_leave(player_id: int = 1, db: Session = Depends(get_db)):
    GuildService(db).leave(player_id)
    return {"code": 0, "data": None, "message": "已退出帮派"}


class GuildAnnouncement(BaseModel):
    content: str


@router.post("/guild/announcement")
def guild_announcement(req: GuildAnnouncement, player_id: int = 1,
                       db: Session = Depends(get_db)):
    GuildService(db).update_announcement(player_id, req.content)
    return {"code": 0, "data": None, "message": "公告已更新"}
