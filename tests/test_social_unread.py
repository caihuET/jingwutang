"""私聊未读策略回归测试"""
import unittest
from unittest.mock import patch

from src.service.social_service import SocialService
from src.utils.redis_client import get_unread


class _FakeRedis:
    """模拟 Redis hgetall 返回旧的世界/帮派未读数据"""

    def hgetall(self, key):
        return {"1": "5", "2": "3", "p:2": "1"}


class TestSocialUnreadPolicy(unittest.TestCase):
    """世界/帮派不再累计未读，仅私聊保留"""

    def setUp(self):
        self.service = SocialService.__new__(SocialService)

    def test_world_and_guild_do_not_increment_unread(self):
        with patch("src.service.social_service.incr_unread") as mock_incr:
            self.service._increase_unread(1, 1, None)
            self.service._increase_unread(1, 2, 10)
            mock_incr.assert_not_called()

    def test_private_increments_only_receiver(self):
        with patch("src.service.social_service.incr_unread") as mock_incr:
            self.service._increase_unread(1, 3, None, 2)
            mock_incr.assert_called_once_with(2, "p:1")

    def test_get_unread_ignores_world_and_guild(self):
        with patch("src.utils.redis_client.get_redis", return_value=_FakeRedis()):
            result = get_unread(1)
        self.assertEqual(result["world"], 0)
        self.assertEqual(result["guild"], 0)
        self.assertEqual(result["private_total"], 1)
        self.assertEqual(result["private"], {2: 1})


if __name__ == "__main__":
    unittest.main()
