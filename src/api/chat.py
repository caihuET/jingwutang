"""聊天 WebSocket 接口"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.models.player import Player
from src.service.social_service import SocialService
from src.service.chat_ws import ws_manager

router = APIRouter()


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket, player_id: int = 1,
                  db: Session = Depends(get_db)):
    """WebSocket 实时聊天，支持世界/帮派频道"""
    player = db.query(Player).filter(Player.id == player_id).first()
    guild_id = player.guild_id if player else None
    await ws_manager.connect(websocket, player_id, guild_id)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") != "send":
                continue
            channel = int(data.get("channel", 1))
            content = str(data.get("content", "")).strip()
            if not content:
                continue
            msg = SocialService(db).send_chat(
                player_id, channel, content, data.get("receiver_id")
            )
            await ws_manager.broadcast(channel, player_id, msg.get("guild_id"), msg)
    except WebSocketDisconnect:
        await ws_manager.disconnect(player_id)
    except Exception:
        await ws_manager.disconnect(player_id)
