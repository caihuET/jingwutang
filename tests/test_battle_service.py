"""历练战斗服务回归测试"""
import unittest
from types import SimpleNamespace

from src.service.battle_service import BattleService


class _FakeQuery:
    """模拟 SQLAlchemy Query 链式调用"""

    def join(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return []


class _FakeDB:
    """仅用于触发被动技能查询的 SQL 条件求值"""

    def query(self, *args, **kwargs):
        return _FakeQuery()


class TestBattleServicePassiveSkills(unittest.TestCase):
    """被动技能加成查询不应因 SkillType 未导入而报错"""

    def test_get_passive_bonuses_does_not_raise(self):
        service = BattleService.__new__(BattleService)
        service.db = _FakeDB()
        player = SimpleNamespace(id=1)
        self.assertEqual(service._get_passive_bonuses(player), {})


if __name__ == "__main__":
    unittest.main()
