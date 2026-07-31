"""社交 API（好友 + 聊天）"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.social_service import SocialService

router = APIRouter()


@router.get("/friend/list")
def friend_list(player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": SocialService(db).get_friends(player_id), "message": "ok"}


@router.get("/friend/requests")
def friend_requests(player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": SocialService(db).get_requests(player_id), "message": "ok"}


class FriendName(BaseModel):
    player_name: str


@router.post("/friend/add")
def friend_add(req: FriendName, player_id: int = 1, db: Session = Depends(get_db)):
    SocialService(db).add_friend(player_id, req.player_name)
    return {"code": 0, "data": None, "message": "好友申请已发送"}


class FriendRespond(BaseModel):
    player_id: int
    accept: bool = True


@router.post("/friend/respond")
def friend_respond(req: FriendRespond, player_id: int = 1, db: Session = Depends(get_db)):
    SocialService(db).respond_friend(player_id, req.player_id, req.accept)
    return {"code": 0, "data": None, "message": "操作成功"}


class FriendId(BaseModel):
    player_id: int


@router.post("/friend/remove")
def friend_remove(req: FriendId, player_id: int = 1, db: Session = Depends(get_db)):
    SocialService(db).remove_friend(player_id, req.player_id)
    return {"code": 0, "data": None, "message": "已删除好友"}


@router.post("/friend/gift-stamina")
def friend_gift(req: FriendId, player_id: int = 1, db: Session = Depends(get_db)):
    result = SocialService(db).gift_stamina(player_id, req.player_id)
    return {"code": 0, "data": result, "message": "赠送成功"}


@router.post("/friend/spar")
def friend_spar(req: FriendId, player_id: int = 1, db: Session = Depends(get_db)):
    result = SocialService(db).spar(player_id, req.player_id)
    return {"code": 0, "data": result, "message": "切磋完成"}


@router.get("/chat/messages")
def chat_messages(channel: int = 1, receiver_id: int = None,
                  player_id: int = 1, db: Session = Depends(get_db)):
    data = SocialService(db).get_messages(player_id, channel, receiver_id)
    return {"code": 0, "data": data, "message": "ok"}


class ChatSend(BaseModel):
    channel: int
    content: str
    receiver_id: int = None


@router.post("/chat/send")
def chat_send(req: ChatSend, player_id: int = 1, db: Session = Depends(get_db)):
    SocialService(db).send_chat(player_id, req.channel, req.content, req.receiver_id)
    return {"code": 0, "data": None, "message": "发送成功"}
