"""WebSocket 聊天连接管理"""
import logging

logger = logging.getLogger(__name__)


class ChatWebSocketManager:
    """维护在线连接并按频道广播"""

    def __init__(self):
        self._connections = {}
        self._guild_ids = {}

    async def connect(self, websocket, player_id: int, guild_id: int = None):
        await websocket.accept()
        self._connections[player_id] = websocket
        self._guild_ids[player_id] = guild_id

    async def disconnect(self, player_id: int):
        self._connections.pop(player_id, None)
        self._guild_ids.pop(player_id, None)

    async def broadcast(self, channel: int, sender_id: int,
                        guild_id: int, message: dict):
        payload = {"type": "chat", "channel": channel, "data": message}
        receiver_id = message.get("receiver_id") if channel == 3 else None
        for player_id, ws in list(self._connections.items()):
            if channel == 2 and self._guild_ids.get(player_id) != guild_id:
                continue
            if channel == 3 and player_id not in (sender_id, receiver_id):
                continue
            try:
                await ws.send_json(payload)
            except Exception:
                await self.disconnect(player_id)
                logger.warning("聊天推送失败，已断开连接: player_id=%s", player_id)


ws_manager = ChatWebSocketManager()
