"""WebSocket 聊天连接管理（支持跨 worker 推送）"""
import asyncio
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

REDIS_CHAT_CHANNEL = "jingwutang:chat:events"


class ChatWebSocketManager:
    """维护在线连接，并通过 Redis 实现跨 worker 广播"""

    def __init__(self):
        self._connections: Dict[int, object] = {}
        self._guild_ids: Dict[int, Optional[int]] = {}
        self._redis = None
        self._pubsub = None
        self._listener_task = None

    async def connect(self, websocket, player_id: int, guild_id: int = None):
        await websocket.accept()
        self._connections[player_id] = websocket
        self._guild_ids[player_id] = guild_id

    async def disconnect(self, player_id: int):
        self._connections.pop(player_id, None)
        self._guild_ids.pop(player_id, None)

    async def start_listener(self):
        """启动 Redis 订阅监听，失败时降级为本地推送"""
        if self._pubsub is not None:
            return
        try:
            from redis import asyncio as aioredis
            from config import config
            self._redis = aioredis.from_url(
                config.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._pubsub = self._redis.pubsub()
            await self._pubsub.subscribe(REDIS_CHAT_CHANNEL)
            self._listener_task = asyncio.create_task(self._consume())
        except Exception as exc:
            self._redis = None
            self._pubsub = None
            logger.warning("Redis 聊天订阅不可用，降级为本地推送: %s", exc)

    async def _consume(self):
        try:
            async for message in self._pubsub.listen():
                if message.get("type") != "message":
                    continue
                await self._deliver_event(json.loads(message.get("data") or "{}"))
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("Redis 聊天订阅中断: %s", exc)

    async def _publish(self, event: dict) -> bool:
        if self._redis is None:
            return False
        try:
            await self._redis.publish(
                REDIS_CHAT_CHANNEL, json.dumps(event, ensure_ascii=False)
            )
            return True
        except Exception as exc:
            logger.warning("Redis 聊天推送失败，降级为本地推送: %s", exc)
            return False

    async def send_to_player(self, player_id: int, payload: dict):
        event = {"kind": "direct", "player_id": player_id, "payload": payload}
        if not await self._publish(event):
            await self._deliver_event(event)

    async def broadcast(self, channel: int, sender_id: int,
                        guild_id: int, message: dict):
        event = {
            "kind": "chat",
            "channel": channel,
            "sender_id": sender_id,
            "guild_id": guild_id,
            "message": message,
        }
        if not await self._publish(event):
            await self._deliver_event(event)

    async def _deliver_event(self, event: dict):
        if event.get("kind") == "direct":
            await self._send_local(event.get("player_id"), event.get("payload") or {})
            return
        if event.get("kind") != "chat":
            return
        channel = event.get("channel")
        sender_id = event.get("sender_id")
        guild_id = event.get("guild_id")
        message = event.get("message") or {}
        receiver_id = message.get("receiver_id") if channel == 3 else None
        payload = {"type": "chat", "channel": channel, "data": message}
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

    async def _send_local(self, player_id: int, payload: dict):
        ws = self._connections.get(player_id)
        if ws is None:
            return
        try:
            await ws.send_json(payload)
        except Exception:
            await self.disconnect(player_id)
            logger.warning("通知推送失败，已断开连接: player_id=%s", player_id)


ws_manager = ChatWebSocketManager()
