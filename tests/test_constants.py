"""常量和核心逻辑单元测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from src.utils.constants import (
    ErrorCode, EXP_TABLE, ENHANCE_RATES,
    SchoolType, EquipSlot, EquipQuality, TaskType, BattleType,
    SkillType, PASSIVE_SKILL_UNLOCK_LEVEL, PASSIVE_SKILL_EFFECTS,
)


class TestConstantsValues(unittest.TestCase):
    def test_school_types(self):
        self.assertEqual(SchoolType.SHAOLIN, 1)
        self.assertEqual(SchoolType.WUDANG, 2)
        self.assertEqual(SchoolType.EMEI, 3)
        self.assertEqual(SchoolType.TANGMEN, 4)
        self.assertEqual(SchoolType.GAIBANG, 5)
        self.assertEqual(SchoolType.MINGJIAO, 6)

    def test_school_names(self):
        self.assertEqual(SchoolType.NAMES[1], "少林")
        self.assertEqual(SchoolType.NAMES[6], "明教")

    def test_equip_slots(self):
        self.assertEqual(EquipSlot.WEAPON, 1)
        self.assertEqual(EquipSlot.ARMOR, 2)
        self.assertEqual(EquipSlot.ACCESSORY, 3)
        self.assertEqual(EquipSlot.MOUNT, 4)

    def test_equip_qualities(self):
        self.assertEqual(EquipQuality.GRAY, 1)
        self.assertEqual(EquipQuality.ORANGE, 5)

    def test_task_types(self):
        self.assertEqual(TaskType.MAIN, 1)
        self.assertEqual(TaskType.DAILY, 2)
        self.assertEqual(TaskType.SCHOOL, 3)
        self.assertEqual(TaskType.ACHIEVEMENT, 4)

    def test_battle_types(self):
        self.assertEqual(BattleType.PVE, 1)
        self.assertEqual(BattleType.ARENA, 2)

    def test_error_codes(self):
        self.assertEqual(ErrorCode.SUCCESS, 0)
        self.assertEqual(ErrorCode.USERNAME_EXISTS, 1001)
        self.assertEqual(ErrorCode.TOKEN_INVALID, 2001)
        self.assertEqual(ErrorCode.SERVER_ERROR, 5000)


class TestExpTable(unittest.TestCase):
    def test_exp_table_length(self):
        self.assertEqual(len(EXP_TABLE), 101)

    def test_exp_increasing(self):
        for i in range(1, len(EXP_TABLE)):
            self.assertGreater(EXP_TABLE[i], 0, f"Level {i} exp is 0")

    def test_exp_growth_stages(self):
        # 新手期: 1-10, 线性
        self.assertEqual(EXP_TABLE[1], 100)
        self.assertEqual(EXP_TABLE[10], 1000)
        # 成长期: 11-30, 平方*10
        self.assertEqual(EXP_TABLE[11], 1210)
        # 中期: 31-60, 平方*20
        self.assertEqual(EXP_TABLE[31], 19220)
        # 后期: 61-100, 平方*40
        self.assertEqual(EXP_TABLE[61], 148840)

    def test_exp_monotonic(self):
        for i in range(1, 99):
            self.assertLess(EXP_TABLE[i], EXP_TABLE[i + 1],
                            f"Level {i} exp >= level {i+1}")


class TestEnhanceRates(unittest.TestCase):
    def test_rate_count(self):
        # 强化上限扩展至 20 级（各品质上限见 ENHANCE_MAX_BY_QUALITY）
        self.assertEqual(len(ENHANCE_RATES), 20)

    def test_rate_values(self):
        self.assertEqual(ENHANCE_RATES[0], 1.0)
        self.assertEqual(ENHANCE_RATES[1], 1.0)
        self.assertEqual(ENHANCE_RATES[2], 0.95)
        self.assertEqual(ENHANCE_RATES[5], 0.65)
        self.assertEqual(ENHANCE_RATES[10], 0.25)
        self.assertEqual(ENHANCE_RATES[14], 0.10)
        self.assertEqual(ENHANCE_RATES[19], 0.03)

    def test_rates_decreasing(self):
        for i in range(14):
            self.assertGreaterEqual(ENHANCE_RATES[i], ENHANCE_RATES[i + 1],
                                    f"Rate increased at level {i}")

    def test_rates_in_range(self):
        for rate in ENHANCE_RATES.values():
            self.assertGreaterEqual(rate, 0.0)
            self.assertLessEqual(rate, 1.0)


class TestErrorMessages(unittest.TestCase):
    def test_error_messages_exist(self):
        self.assertIn(1001, ErrorCode.MESSAGES)
        self.assertIn(5000, ErrorCode.MESSAGES)

    def test_chinese_messages(self):
        self.assertEqual(ErrorCode.MESSAGES[1001], "用户名已存在")
        self.assertEqual(ErrorCode.MESSAGES[5000], "服务器内部错误")


class TestPassiveSkills(unittest.TestCase):
    """被动技能常量测试"""

    def test_passive_type(self):
        self.assertEqual(SkillType.PASSIVE, 5)

    def test_passive_unlock_level(self):
        self.assertEqual(PASSIVE_SKILL_UNLOCK_LEVEL, 20)

    def test_passive_effects_cover_six_schools(self):
        self.assertEqual(len(PASSIVE_SKILL_EFFECTS), 6)


if __name__ == "__main__":
    unittest.main()
