"""装备属性核心逻辑单元测试"""
import random
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.constants import (
    AFFIX_COUNT_BY_QUALITY,
    AFFIX_VALUE_RANGE,
    BASE_STAT_KEYS,
    calc_enhance_stats,
    calc_equip_power,
    generate_affixes,
    get_base_max_stamina,
    get_enhance_band,
)


class TestEnhanceStats(unittest.TestCase):
    """强化成长公式测试（穿戴等级带 + 品质）"""

    def test_tian_gang_sword_level_10(self):
        stats = calc_enhance_stats({"attack": 100}, 40, 5, 10)
        self.assertEqual(stats["attack"], 120)

    def test_tian_gang_sword_level_18(self):
        stats = calc_enhance_stats({"attack": 100}, 40, 5, 18)
        self.assertEqual(stats["attack"], 216)

    def test_jing_gang_sword_level_3(self):
        stats = calc_enhance_stats({"attack": 35, "magic_attack": 14}, 15, 3, 3)
        self.assertEqual(stats["attack"], 9)
        self.assertEqual(stats["magic_attack"], 4)

    def test_zero_enhance_level(self):
        stats = calc_enhance_stats({"attack": 100}, 60, 6, 0)
        self.assertEqual(stats["attack"], 0)

    def test_band_boundary(self):
        self.assertEqual(get_enhance_band(1), 1)
        self.assertEqual(get_enhance_band(4), 1)
        self.assertEqual(get_enhance_band(5), 5)
        self.assertEqual(get_enhance_band(14), 5)
        self.assertEqual(get_enhance_band(15), 15)
        self.assertEqual(get_enhance_band(39), 25)
        self.assertEqual(get_enhance_band(40), 40)
        self.assertEqual(get_enhance_band(60), 60)
        self.assertEqual(get_enhance_band(80), 60)

    def test_all_keys_present(self):
        stats = calc_enhance_stats({"attack": 10, "hp": 100}, 25, 4, 5)
        for key in BASE_STAT_KEYS:
            self.assertIn(key, stats)


class TestAffixGeneration(unittest.TestCase):
    """附加属性生成测试"""

    def test_count_by_quality(self):
        for quality in range(1, 7):
            affixes = generate_affixes(quality, 1, random.Random(quality))
            self.assertEqual(len(affixes), AFFIX_COUNT_BY_QUALITY[quality])

    def test_no_duplicate_type(self):
        for quality in range(1, 7):
            for slot in range(1, 7):
                affixes = generate_affixes(quality, slot, random.Random(quality * 10 + slot))
                types = [a["affix_type"] for a in affixes]
                self.assertEqual(len(types), len(set(types)), f"q{quality} slot{slot}")

    def test_value_in_range(self):
        for quality in range(1, 7):
            for _ in range(20):
                affixes = generate_affixes(quality, 1, random.Random())
                for affix in affixes:
                    vmin, vmax = AFFIX_VALUE_RANGE[quality][affix["affix_type"]]
                    self.assertGreaterEqual(affix["value"], vmin)
                    self.assertLessEqual(affix["value"], vmax)

    def test_sort_order_sequential(self):
        affixes = generate_affixes(6, 6, random.Random(1))
        self.assertEqual([a["sort_order"] for a in affixes], list(range(1, len(affixes) + 1)))

    def test_deterministic_with_seed(self):
        first = generate_affixes(5, 5, random.Random(42))
        second = generate_affixes(5, 5, random.Random(42))
        self.assertEqual(first, second)


class TestEquipPowerAndStamina(unittest.TestCase):
    """战力与体力上限计算测试"""

    def test_calc_equip_power(self):
        bonuses = {
            "attack": 100,
            "magic_attack": 40,
            "defense": 10,
            "magic_defense": 5,
            "hp": 200,
            "mp": 50,
            "speed": 15,
            "stamina": 8,
        }
        self.assertEqual(calc_equip_power(bonuses), 314)

    def test_max_stamina_by_level(self):
        self.assertEqual(get_base_max_stamina(1), 100)
        self.assertEqual(get_base_max_stamina(60), 130)
        self.assertEqual(get_base_max_stamina(100), 150)


if __name__ == "__main__":
    unittest.main()
