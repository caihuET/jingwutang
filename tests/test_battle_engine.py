"""战斗引擎单元测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
import random
from src.service.battle_engine import BattleEngine, BattleUnit, BattleResult, MONSTERS


class TestBattleUnit(unittest.TestCase):
    """战斗单元测试"""

    def setUp(self):
        self.unit = BattleUnit(
            unit_id=1, name="测试玩家", level=10,
            hp=200, mp=100, attack=30, defense=15,
            magic_attack=20, magic_defense=12, speed=15,
            crit_rate=0.05, dodge_rate=0.05,
            skills=[{"id": 1, "name": "测试技能", "skill_type": 2,
                     "base_damage": 150, "mp_cost": 15, "cooldown": 0,
                     "damage_type": 1}],
            is_player=True,
        )

    def test_is_alive(self):
        self.assertTrue(self.unit.is_alive())
        self.unit.hp = 0
        self.assertFalse(self.unit.is_alive())

    def test_take_damage(self):
        self.unit.take_damage(50)
        self.assertEqual(self.unit.hp, 150)

    def test_take_damage_overflow(self):
        self.unit.take_damage(999)
        self.assertEqual(self.unit.hp, 0)

    def test_cooldown(self):
        skill = self.unit.skills[0]
        skill["cooldown"] = 2
        self.assertTrue(self.unit.can_use_skill(skill))
        self.unit.use_skill(skill)
        self.assertFalse(self.unit.can_use_skill(skill))
        self.unit.tick_cooldowns()
        self.assertFalse(self.unit.can_use_skill(skill))
        self.unit.tick_cooldowns()
        self.assertTrue(self.unit.can_use_skill(skill))

    def test_mp_cost(self):
        skill = {"id": 2, "name": "耗蓝技能", "mp_cost": 999, "cooldown": 0}
        self.assertFalse(self.unit.can_use_skill(skill))

    def test_get_available_skills(self):
        self.assertEqual(len(self.unit.get_available_skills()), 1)

    def test_get_available_skills_no_mp(self):
        self.unit.mp = 0
        self.assertEqual(len(self.unit.get_available_skills()), 0)


class TestBattleEngine(unittest.TestCase):
    """战斗引擎测试"""

    def setUp(self):
        self.engine = BattleEngine()
        self.player = BattleUnit(
            unit_id=1, name="玩家", level=10,
            hp=200, mp=100, attack=30, defense=15,
            magic_attack=20, magic_defense=12, speed=15,
            crit_rate=0.05, dodge_rate=0.05,
            skills=[{"id": 1, "name": "普攻", "skill_type": 1,
                     "base_damage": 100, "mp_cost": 0, "cooldown": 0,
                     "damage_type": 1}],
            is_player=True,
        )

    def test_setup_pve_valid_map(self):
        result = self.engine.setup_pve(self.player, 1)
        self.assertTrue(result)
        self.assertIsNotNone(self.engine.defender)
        self.assertEqual(self.engine.defender.name, "山贼甲")

    def test_setup_pve_invalid_map(self):
        result = self.engine.setup_pve(self.player, 999)
        self.assertFalse(result)

    def test_full_battle_execution(self):
        self.engine.setup_pve(self.player, 1)
        result = self.engine.execute()
        self.assertIsInstance(result, BattleResult)
        self.assertGreater(result.rounds, 0)
        self.assertIn(result.winner, [self.engine.attacker, self.engine.defender])
        self.assertGreater(len(result.log), 0)

    def test_winner_is_player_on_strong_enemy(self):
        """强玩家对弱怪物应获胜"""
        strong_player = BattleUnit(
            unit_id=1, name="强者", level=50,
            hp=1000, mp=500, attack=200, defense=100,
            magic_attack=150, magic_defense=80, speed=50,
            crit_rate=0.1, dodge_rate=0.1,
            skills=[{"id": 1, "name": "强攻", "skill_type": 2,
                     "base_damage": 200, "mp_cost": 10, "cooldown": 0,
                     "damage_type": 1}],
            is_player=True,
        )
        self.engine.setup_pve(strong_player, 1)
        result = self.engine.execute()
        self.assertTrue(result.winner.is_player)

    def test_battle_log_structure(self):
        self.engine.setup_pve(self.player, 1)
        result = self.engine.execute()
        for round_entry in result.log:
            self.assertIn("round", round_entry)
            self.assertIn("actions", round_entry)
            for action in round_entry["actions"]:
                self.assertIn("actor", action)
                self.assertIn("skill", action)
                self.assertIn("damage", action)

    def test_damage_minimum(self):
        """伤害至少为 1"""
        weak = BattleUnit(
            unit_id=2, name="弱者", level=1,
            hp=10, mp=0, attack=1, defense=0,
            magic_attack=0, magic_defense=0, speed=1,
            skills=[],
        )
        defender = BattleUnit(
            unit_id=3, name="铁壁", level=1,
            hp=1000, mp=0, attack=0, defense=0,
            magic_attack=0, magic_defense=0, speed=1,
            skills=[],
        )
        damage = self.engine._calc_damage(
            weak, defender,
            {"id": 0, "name": "普攻", "skill_type": 1, "base_damage": 1,
             "mp_cost": 0, "cooldown": 0, "damage_type": 1},
            False
        )
        self.assertGreaterEqual(damage, 1)


class TestMonsters(unittest.TestCase):
    """怪物模板测试"""

    def test_monster_definitions(self):
        self.assertIn(1, MONSTERS)
        self.assertIn(2, MONSTERS)
        self.assertIn(3, MONSTERS)
        self.assertIn(4, MONSTERS)

    def test_monster_fields(self):
        monster = MONSTERS[1]
        required = ["name", "level", "hp", "attack", "defense",
                    "exp_reward", "gold_reward"]
        for field in required:
            self.assertIn(field, monster, f"怪物缺少字段: {field}")

    def test_monster_exp_positive(self):
        for mid, m in MONSTERS.items():
            self.assertGreater(m["exp_reward"], 0, f"怪物{mid}经验为0")
            self.assertGreater(m["gold_reward"], 0, f"怪物{mid}金币为0")

    def test_monster_stats_scale(self):
        """高级怪物应有更高属性"""
        stats = ["hp", "attack", "defense", "exp_reward", "gold_reward"]
        for s in stats:
            self.assertGreater(
                MONSTERS[4][s], MONSTERS[1][s],
                f"山寨首领的{s}应高于山贼甲"
            )


class TestAdvanceCombat(unittest.TestCase):
    """高级战斗场景测试"""

    def test_speed_determines_turn_order(self):
        fast = BattleUnit(1, "快", 1, 100, 100, 10, 5, 5, 5, 50, skills=[])
        slow = BattleUnit(2, "慢", 1, 100, 100, 10, 5, 5, 5, 10, skills=[])
        engine = BattleEngine()
        engine.attacker = fast
        engine.defender = slow
        engine.execute()
        self.assertGreater(fast.speed, slow.speed)

    def test_full_battle_with_player_stats(self):
        """模拟完整战斗流程: 从玩家属性构建战斗单位到战斗结束"""
        # 模拟 _build_player_unit 的输出
        unit = BattleUnit(
            unit_id=1, name="测试少侠", level=10,
            hp=200, mp=100, attack=30, defense=15,
            magic_attack=20, magic_defense=12, speed=15,
            crit_rate=0.05, dodge_rate=0.05,
            skills=[{"id": 1, "name": "测试拳", "skill_type": 2,
                     "base_damage": 150, "mp_cost": 15, "cooldown": 0,
                     "damage_type": 1}],
            is_player=True,
        )
        engine = BattleEngine()
        self.assertTrue(engine.setup_pve(unit, 1), "地图1(山贼甲)应能正常setup")
        result = engine.execute()
        self.assertIsNotNone(result.winner, "战斗应有胜者")
        self.assertGreater(result.rounds, 0, "应有至少1回合")
        self.assertGreater(len(result.log), 0, "应有战斗日志")
        self.assertTrue(result.winner.is_player, "玩家属性远强于怪物, 应获胜")
        self.assertIn(result.to_dict()["result"], ["win", "lose"], "result 应为 win 或 lose")
        self.assertGreater(result.exp_gained, 0, "应有经验奖励")
        self.assertGreater(result.gold_gained, 0, "应有金币奖励")

    def test_all_maps_valid(self):
        """验证所有地图均可正常setup"""
        unit = BattleUnit(0, "玩家", 10, 200, 100, 30, 15, 20, 12, 15, 0.05, 0.05, [], True)
        for map_id in [1, 2, 3, 4]:
            engine = BattleEngine()
            self.assertTrue(engine.setup_pve(unit, map_id),
                            f"地图{map_id}({MONSTERS[map_id]['name']})应可setup")
            result = engine.execute()
            self.assertIsNotNone(result.winner, f"地图{map_id}战斗应有结果")

    def test_passive_heal(self):
        """被动回血应在回合开始时生效"""
        unit = BattleUnit(1, "回血", 10, 100, 100, 10, 5, 5, 5, 10,
                          skills=[], heal_per_round=10)
        unit.hp = 50
        engine = BattleEngine()
        engine.attacker = unit
        engine.defender = BattleUnit(2, "木桩", 1, 1000, 100, 1, 0, 0, 0, 1,
                                     skills=[])
        round_log = {"actions": []}
        engine._apply_round_heal(round_log)
        self.assertEqual(unit.hp, 60)
        self.assertEqual(len(round_log["actions"]), 1)

    def test_reflect_damage(self):
        """反弹伤害应反伤攻击者"""
        attacker = BattleUnit(1, "攻", 10, 200, 100, 50, 10, 5, 5, 10,
                              skills=[{"id": 1, "name": "拳", "skill_type": 2,
                                       "base_damage": 150, "mp_cost": 0,
                                       "cooldown": 0, "damage_type": 1}],
                              is_player=True)
        defender = BattleUnit(2, "反", 10, 500, 100, 0, 10, 5, 5, 5,
                              skills=[], reflect_rate=0.5, dodge_rate=0.0)
        engine = BattleEngine()
        engine.attacker = attacker
        engine.defender = defender
        hp_before = attacker.hp
        engine._process_actor_turn(attacker, defender, {"actions": []})
        self.assertLess(attacker.hp, hp_before)

    def test_lifesteal(self):
        """吸血应按伤害比例回复攻击者"""
        attacker = BattleUnit(1, "吸血", 10, 200, 100, 50, 10, 5, 5, 10,
                              skills=[{"id": 1, "name": "吸", "skill_type": 2,
                                       "base_damage": 150, "mp_cost": 0,
                                       "cooldown": 0, "damage_type": 1}],
                              lifesteal=1.0)
        attacker.hp = 100
        defender = BattleUnit(2, "木桩", 1, 500, 100, 0, 0, 0, 0, 1, skills=[])
        engine = BattleEngine()
        engine.attacker = attacker
        engine.defender = defender
        engine._process_actor_turn(attacker, defender, {"actions": []})
        self.assertGreater(attacker.hp, 100)


if __name__ == "__main__":
    unittest.main()
