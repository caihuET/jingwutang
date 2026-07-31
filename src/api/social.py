"""社交 API（好友 + 聊天）"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.social_service import SocialService
from src.service.chat_ws import ws_manager
from src.utils.redis_client import clear_unread, get_online, get_unread

router = APIRouter()


@router.get("/friend/list")
def friend_list(player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": SocialService(db).get_friends(player_id), "message": "ok"}


@router.get("/friend/requests")
def friend_requests(player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": SocialService(db).get_requests(player_id), "message": "ok"}


@router.get("/friend/request-history")
def friend_request_history(player_id: int = 1, db: Session = Depends(get_db)):
    """我发出的好友申请历史（等待/已同意/已拒绝/已解除）"""
    return {"code": 0, "data": SocialService(db).get_request_history(player_id), "message": "ok"}


class FriendName(BaseModel):
    player_name: str


@router.post("/friend/add")
async def friend_add(req: FriendName, player_id: int = 1, db: Session = Depends(get_db)):
    result = SocialService(db).add_friend(player_id, req.player_name)
    await ws_manager.send_to_player(
        result.get("target_id"),
        {"type": "friend_request", "name": result.get("name") or ""},
    )
    return {"code": 0, "data": None, "message": "好友申请已发送"}


class FriendRespond(BaseModel):
    player_id: int
    accept: bool = True


@router.post("/friend/respond")
async def friend_respond(req: FriendRespond, player_id: int = 1, db: Session = Depends(get_db)):
    result = SocialService(db).respond_friend(player_id, req.player_id, req.accept)
    if req.accept:
        await ws_manager.send_to_player(
            req.player_id,
            {"type": "friend_accepted", "name": result.get("name") or ""},
        )
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
                  player_id: int = 1, before_id: int = None,
                  limit: int = 20, db: Session = Depends(get_db)):
    limit = min(max(1, limit), 50)
    data = SocialService(db).get_messages(
        player_id, channel, receiver_id, before_id, limit,
    )
    return {"code": 0, "data": data, "message": "ok"}


class ChatSend(BaseModel):
    channel: int
    content: str
    receiver_id: int = None
    receiver_name: str = None


@router.post("/chat/send")
async def chat_send(req: ChatSend, player_id: int = 1, db: Session = Depends(get_db)):
    msg = SocialService(db).send_chat(
        player_id, req.channel, req.content, req.receiver_id, req.receiver_name
    )
    await ws_manager.broadcast(msg["channel"], msg["sender_id"], msg.get("guild_id"), msg)
    return {"code": 0, "data": None, "message": "发送成功"}


class ChatRead(BaseModel):
    channel: int
    friend_id: int = None


@router.get("/chat/unread")
def chat_unread(player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": get_unread(player_id), "message": "ok"}


@router.post("/chat/read")
def chat_read(req: ChatRead, player_id: int = 1,
              db: Session = Depends(get_db)):
    if req.channel == 3:
        field = "p:{}".format(req.friend_id) if req.friend_id else None
        clear_unread(player_id, field)
    else:
        clear_unread(player_id, str(req.channel))
    return {"code": 0, "data": None, "message": "ok"}


@router.get("/chat/online")
def chat_online(player_ids: str = "", db: Session = Depends(get_db)):
    ids = [int(item) for item in player_ids.split(",") if item.strip().isdigit()]
    return {"code": 0, "data": get_online(ids), "message": "ok"}
