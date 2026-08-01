"""技能系统新规则单测：杀伤距离、单群攻、熟练加成、状态效果"""
import sys
import os
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.constants import (
    RANGE_DODGE_MODIFIER,
    SKILL_AOE_DAMAGE_MULTIPLIER,
    SkillRange,
    SkillTarget,
    calc_skill_power,
    get_proficiency_bonus,
    get_skill_cooldown,
    get_standard_monster_defense,
)
from src.service.battle_engine import BattleEngine, BattleUnit


class TestSkillRules(unittest.TestCase):
    """技能数值规则测试"""

    def test_skill_power(self):
        self.assertEqual(calc_skill_power(130, 12, 1), 130)
        self.assertEqual(calc_skill_power(130, 12, 5), 178)
        self.assertEqual(calc_skill_power(130, 12, 0), 130)

    def test_aoe_cooldown(self):
        self.assertEqual(get_skill_cooldown(0, SkillTarget.SINGLE), 0)
        self.assertEqual(get_skill_cooldown(0, SkillTarget.AOE), 2)
        self.assertEqual(get_skill_cooldown(2, SkillTarget.AOE), 3)

    def test_aoe_damage_multiplier(self):
        self.assertEqual(SKILL_AOE_DAMAGE_MULTIPLIER, 0.7)

    def test_proficiency_bonus(self):
        self.assertEqual(get_proficiency_bonus(0), 0)
        self.assertEqual(get_proficiency_bonus(49), 0)
        self.assertEqual(get_proficiency_bonus(50), 1)
        self.assertEqual(get_proficiency_bonus(499), 9)
        self.assertEqual(get_proficiency_bonus(500), 10)
        self.assertEqual(get_proficiency_bonus(800), 10)

    def test_range_dodge_modifier(self):
        self.assertEqual(RANGE_DODGE_MODIFIER[SkillRange.NEAR], 1.2)
        self.assertEqual(RANGE_DODGE_MODIFIER[SkillRange.MID], 1.0)
        self.assertEqual(RANGE_DODGE_MODIFIER[SkillRange.FAR], 0.8)

    def test_standard_monster_defense(self):
        self.assertEqual(get_standard_monster_defense(1), 9)
        self.assertEqual(get_standard_monster_defense(10), 23)


class TestBattleSkillEffects(unittest.TestCase):
    """战斗引擎技能效果测试"""

    def make_engine(self, actor, target):
        engine = BattleEngine()
        engine.attacker = actor
        engine.defender = target
        return engine

    def heal_skill(self):
        return {
            "id": 1, "name": "回春术", "skill_type": 4,
            "base_damage": 0, "mp_cost": 10, "cooldown": 2,
            "damage_type": 0, "target_type": SkillTarget.SINGLE,
            "attack_range": SkillRange.MID, "proficiency": 0, "level": 1,
            "effects": [{
                "effect_type": "heal", "base_value": 50,
                "value_per_level": 0, "duration": 0, "target_type": 2,
            }],
        }

    def test_heal_skill(self):
        actor = BattleUnit(1, "玩家", 10, 200, 100, 30, 15, 100, 15, 15,
                           skills=[self.heal_skill()], is_player=True)
        actor.hp = 50
        target = BattleUnit(2, "木桩", 1, 1000, 100, 1, 0, 0, 0, 1, skills=[])
        engine = self.make_engine(actor, target)
        round_log = {"actions": []}
        engine._process_actor_turn(actor, target, round_log)
        self.assertEqual(actor.hp, 100)
        self.assertEqual(actor.mp, 90)
        self.assertTrue(any(a.get("support") for a in round_log["actions"]))

    def test_burn_dot(self):
        actor = BattleUnit(1, "玩家", 10, 200, 100, 30, 15, 100, 15, 15,
                           skills=[], is_player=True)
        target = BattleUnit(2, "木桩", 1, 1000, 100, 1, 0, 0, 0, 1, skills=[])
        engine = self.make_engine(actor, target)
        skill = {
            "id": 2, "name": "圣火令", "skill_type": 3,
            "base_damage": 175, "mp_cost": 20, "cooldown": 1,
            "damage_type": 2, "target_type": SkillTarget.SINGLE,
            "attack_range": SkillRange.MID, "proficiency": 0, "level": 1,
            "effects": [{
                "effect_type": "burn", "base_value": 10,
                "value_per_level": 0, "duration": 2, "target_type": 1,
            }],
        }
        engine._apply_skill_effects(actor, target, skill, {"actions": []})
        self.assertEqual(target.statuses["burn"]["damage"], 10)
        self.assertEqual(target.statuses["burn"]["duration"], 2)
        hp_before = target.hp
        engine._apply_round_heal({"actions": []})
        self.assertEqual(target.hp, hp_before - 10)

    def test_aoe_and_proficiency_damage(self):
        actor = BattleUnit(1, "玩家", 10, 500, 500, 1000, 100, 1000, 100, 20,
                           skills=[], is_player=True)
        target = BattleUnit(2, "木桩", 1, 9999, 100, 1, 0, 0, 0, 1, skills=[])
        engine = self.make_engine(actor, target)
        single = {
            "id": 1, "name": "单体", "skill_type": 2, "base_damage": 100,
            "mp_cost": 0, "cooldown": 0, "damage_type": 1,
            "target_type": SkillTarget.SINGLE, "attack_range": SkillRange.MID,
            "proficiency": 0, "effects": [],
        }
        aoe = dict(single)
        aoe["target_type"] = SkillTarget.AOE
        prof = dict(single)
        prof["proficiency"] = 500
        with mock.patch("random.uniform", return_value=0.0):
            single_damage = engine._calc_damage(actor, target, single, False)
            aoe_damage = engine._calc_damage(actor, target, aoe, False)
            prof_damage = engine._calc_damage(actor, target, prof, False)
        self.assertEqual(aoe_damage, int(single_damage * 0.7))
        self.assertEqual(prof_damage, int(single_damage * 1.1))


if __name__ == "__main__":
    unittest.main()
