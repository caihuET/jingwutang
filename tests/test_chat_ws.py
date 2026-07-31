"""WebSocket 聊天连接管理测试"""
import asyncio
import unittest
from src.service.chat_ws import ChatWebSocketManager


class FakeWebSocket:
    """模拟 WebSocket，仅记录发送内容"""

    def __init__(self):
        self.sent = []

    async def accept(self):
        return None

    async def send_json(self, payload):
        self.sent.append(payload)


class TestChatWebSocketManager(unittest.TestCase):
    """聊天连接管理单元测试"""

    def test_world_broadcast_to_all(self):
        manager = ChatWebSocketManager()
        a = FakeWebSocket()
        b = FakeWebSocket()

        async def run():
            await manager.connect(a, 1, None)
            await manager.connect(b, 2, None)
            await manager.broadcast(1, 1, None, {"content": "hi"})

        asyncio.run(run())
        self.assertEqual(len(a.sent), 1)
        self.assertEqual(len(b.sent), 1)

    def test_guild_broadcast_only_members(self):
        manager = ChatWebSocketManager()
        a = FakeWebSocket()
        b = FakeWebSocket()
        c = FakeWebSocket()

        async def run():
            await manager.connect(a, 1, 10)
            await manager.connect(b, 2, 10)
            await manager.connect(c, 3, 20)
            await manager.broadcast(2, 1, 10, {"content": "hi"})

        asyncio.run(run())
        self.assertEqual(len(a.sent), 1)
        self.assertEqual(len(b.sent), 1)
        self.assertEqual(len(c.sent), 0)

    def test_private_broadcast_only_two_players(self):
        manager = ChatWebSocketManager()
        me = FakeWebSocket()
        friend = FakeWebSocket()
        other = FakeWebSocket()

        async def run():
            await manager.connect(me, 1, None)
            await manager.connect(friend, 2, None)
            await manager.connect(other, 3, None)
            await manager.broadcast(3, 1, None, {
                "sender_id": 1,
                "receiver_id": 2,
                "content": "hi",
            })

        asyncio.run(run())
        self.assertEqual(len(me.sent), 1)
        self.assertEqual(len(friend.sent), 1)
        self.assertEqual(len(other.sent), 0)

    def test_disconnect_removes_connection(self):
        manager = ChatWebSocketManager()
        a = FakeWebSocket()

        async def run():
            await manager.connect(a, 1, None)
            await manager.disconnect(1)
            await manager.broadcast(1, 1, None, {"content": "hi"})

        asyncio.run(run())
        self.assertEqual(len(a.sent), 0)


if __name__ == "__main__":
    unittest.main()
