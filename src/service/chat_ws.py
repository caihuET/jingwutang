"""WebSocket 聊天连接管理（支持跨 worker 推送）"""
import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

REDIS_CHAT_CHANNEL = "jingwutang:chat:events"
MAX_DEDUPE_EVENTS = 200


class ChatWebSocketManager:
    """维护在线连接，并通过 Redis 实现跨 worker 广播"""

    def __init__(self):
        self._connections: Dict[int, object] = {}
        self._guild_ids: Dict[int, Optional[int]] = {}
        self._redis = None
        self._pubsub = None
        self._listener_task = None
        self._delivered_event_ids: Dict[int, List[str]] = {}

    async def connect(self, websocket, player_id: int, guild_id: int = None):
        await websocket.accept()
        self._connections[player_id] = websocket
        self._guild_ids[player_id] = guild_id

    async def disconnect(self, player_id: int):
        self._connections.pop(player_id, None)
        self._guild_ids.pop(player_id, None)
        self._delivered_event_ids.pop(player_id, None)

    async def start_listener(self):
        """启动 Redis 订阅监听，失败时降级为本地推送"""
        if self._listener_task is not None and not self._listener_task.done():
            return
        self._listener_task = asyncio.create_task(self._consume())

    async def _connect_redis(self) -> bool:
        """建立 Redis 订阅连接，失败时返回 False"""
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
            return True
        except Exception as exc:
            self._redis = None
            self._pubsub = None
            logger.warning("Redis 聊天订阅不可用，降级为本地推送: %s", exc)
            return False

    async def _cleanup_redis(self) -> None:
        """关闭订阅连接，避免断线后残留句柄"""
        if self._pubsub is not None:
            try:
                await self._pubsub.aclose()
            except Exception:
                pass
        if self._redis is not None:
            try:
                await self._redis.aclose()
            except Exception:
                pass
        self._pubsub = None
        self._redis = None

    async def _consume(self):
        retry_seconds = 1
        while True:
            if not await self._connect_redis():
                await asyncio.sleep(min(30, retry_seconds))
                retry_seconds = min(30, retry_seconds * 2)
                continue
            retry_seconds = 1
            try:
                await self._listen_once()
                return
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("Redis 聊天订阅中断: %s", exc)
            await self._cleanup_redis()
            await asyncio.sleep(min(30, retry_seconds))
            retry_seconds = min(30, retry_seconds * 2)

    async def _listen_once(self) -> None:
        async for message in self._pubsub.listen():
            if message.get("type") != "message":
                continue
            await self._deliver_event(json.loads(message.get("data") or "{}"))

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
        event = {
            "kind": "direct",
            "player_id": player_id,
            "payload": payload,
            "event_id": uuid.uuid4().hex,
        }
        await self._publish(event)
        await self._deliver_event(event)

    async def broadcast(self, channel: int, sender_id: int,
                        guild_id: int, message: dict):
        event = {
            "kind": "chat",
            "channel": channel,
            "sender_id": sender_id,
            "guild_id": guild_id,
            "message": message,
            "event_id": uuid.uuid4().hex,
        }
        await self._publish(event)
        await self._deliver_event(event)

    async def _deliver_event(self, event: dict):
        event_id = event.get("event_id") or ""
        if event.get("kind") == "direct":
            player_id = event.get("player_id")
            if not self._mark_if_new(player_id, event_id):
                return
            await self._send_local(player_id, event.get("payload") or {})
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
            if not self._mark_if_new(player_id, event_id):
                continue
            try:
                await ws.send_json(payload)
            except Exception:
                await self.disconnect(player_id)
                logger.warning("聊天推送失败，已断开连接: player_id=%s", player_id)

    def _mark_if_new(self, player_id: int, event_id: str) -> bool:
        """返回该事件是否首次推送给玩家"""
        if not event_id:
            return True
        ids = self._delivered_event_ids.setdefault(player_id, [])
        if event_id in ids:
            return False
        ids.append(event_id)
        if len(ids) > MAX_DEDUPE_EVENTS:
            del ids[:len(ids) - MAX_DEDUPE_EVENTS]
        return True

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
