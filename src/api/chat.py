"""聊天 WebSocket 接口"""
import asyncio
import logging
import uuid
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.models.player import Player
from src.repository.player_repo import PlayerRepository
from src.service.social_service import SocialService
from src.service.chat_ws import ws_manager
from src.utils.errors import GameException
from src.utils.security import verify_token
from src.utils.redis_client import mark_offline, mark_online

logger = logging.getLogger(__name__)
router = APIRouter()


def _auth_player(token: str, db: Session) -> int:
    """校验 JWT 并返回玩家 ID，失败返回 None"""
    try:
        payload = verify_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            return None
        player = PlayerRepository(db).get_by_user_id(user_id)
        return player.id if player else None
    except Exception:
        return None


async def _handle_send(websocket: WebSocket, db: Session,
                       player_id: int, data: dict):
    """处理聊天发送，并把业务错误回传给客户端"""
    channel = int(data.get("channel", 1))
    content = str(data.get("content", "")).strip()
    receiver_id = data.get("receiver_id")
    receiver_name = data.get("receiver_name")
    if not content:
        return
    try:
        msg = SocialService(db).send_chat(
            player_id, channel, content, receiver_id, receiver_name
        )
        await ws_manager.broadcast(
            channel, player_id, msg.get("guild_id"), msg
        )
    except GameException as exc:
        await websocket.send_json({"type": "error", "message": exc.message})
    except Exception:
        logger.exception("聊天发送失败: player_id=%s", player_id)
        await websocket.send_json({"type": "error", "message": "发送失败"})


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket, token: str = "",
                  db: Session = Depends(get_db)):
    """WebSocket 实时聊天，握手时校验 JWT，并支持心跳"""
    player_id = _auth_player(token, db)
    if player_id is None:
        await websocket.close(code=4401)
        return
    player = db.query(Player).filter(Player.id == player_id).first()
    guild_id = player.guild_id if player else None
    await ws_manager.connect(websocket, player_id, guild_id)
    conn_id = uuid.uuid4().hex
    mark_online(player_id, conn_id)
    try:
        while True:
            data = await asyncio.wait_for(websocket.receive_json(), timeout=90)
            action = data.get("action")
            if action == "ping":
                mark_online(player_id, conn_id)
                await websocket.send_json({"type": "pong"})
                continue
            if action == "send":
                await _handle_send(websocket, db, player_id, data)
    except WebSocketDisconnect:
        await ws_manager.disconnect(player_id)
    except asyncio.TimeoutError:
        await ws_manager.disconnect(player_id)
    except Exception:
        logger.exception("聊天连接异常断开: player_id=%s", player_id)
        await ws_manager.disconnect(player_id)
    finally:
        mark_offline(player_id, conn_id)
