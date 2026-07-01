"""核心战斗引擎 - 回合制战斗逻辑"""
import random
import math
from src.utils.constants import SkillType


# 怪物模板
MONSTERS = {
    1: {"name": "山贼甲", "level": 3, "hp": 60, "mp": 20,
        "attack": 15, "defense": 8, "magic_attack": 5, "magic_defense": 5,
        "speed": 10, "crit_rate": 0.03, "dodge_rate": 0.03,
        "exp_reward": 30, "gold_reward": 15},
    2: {"name": "山贼头目", "level": 5, "hp": 100, "mp": 30,
        "attack": 25, "defense": 12, "magic_attack": 8, "magic_defense": 8,
        "speed": 12, "crit_rate": 0.05, "dodge_rate": 0.04,
        "exp_reward": 60, "gold_reward": 30},
    3: {"name": "青云山贼", "level": 8, "hp": 150, "mp": 40,
        "attack": 35, "defense": 18, "magic_attack": 12, "magic_defense": 10,
        "speed": 15, "crit_rate": 0.05, "dodge_rate": 0.05,
        "exp_reward": 100, "gold_reward": 45},
    4: {"name": "山寨首领", "level": 12, "hp": 250, "mp": 60,
        "attack": 50, "defense": 25, "magic_attack": 20, "magic_defense": 18,
        "speed": 18, "crit_rate": 0.08, "dodge_rate": 0.06,
        "exp_reward": 180, "gold_reward": 80},
}


class BattleUnit:
    """战斗单元 (玩家或怪物)"""

    def __init__(self, unit_id: int, name: str, level: int,
                 hp: int, mp: int, attack: int, defense: int,
                 magic_attack: int, magic_defense: int, speed: int,
                 crit_rate: float = 0.05, dodge_rate: float = 0.05,
                 skills: list = None, is_player: bool = False):
        self.id = unit_id
        self.name = name
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.max_mp = mp
        self.mp = mp
        self.attack = attack
        self.defense = defense
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense
        self.speed = speed
        self.crit_rate = crit_rate
        self.dodge_rate = dodge_rate
        self.skills = skills or []
        self.is_player = is_player
        self.cooldowns = {}  # skill_id -> remaining rounds

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, damage: int):
        self.hp = max(0, self.hp - damage)

    def can_use_skill(self, skill: dict) -> bool:
        """检查是否可以使用技能"""
        skill_id = skill.get("id", 0)
        if skill_id in self.cooldowns and self.cooldowns[skill_id] > 0:
            return False
        if self.mp < skill.get("mp_cost", 0):
            return False
        return True

    def use_skill(self, skill: dict):
        """使用技能, 消耗内力"""
        self.mp -= skill.get("mp_cost", 0)
        cd = skill.get("cooldown", 0)
        if cd > 0:
            self.cooldowns[skill.get("id", 0)] = cd

    def tick_cooldowns(self):
        """减少冷却计数"""
        for skill_id in list(self.cooldowns.keys()):
            self.cooldowns[skill_id] -= 1
            if self.cooldowns[skill_id] <= 0:
                del self.cooldowns[skill_id]

    def get_available_skills(self) -> list:
        """获取可用的技能列表"""
        return [s for s in self.skills if self.can_use_skill(s)]


class BattleResult:
    """战斗结果"""

    def __init__(self):
        self.winner = None
        self.loser = None
        self.rounds = 0
        self.log = []
        self.exp_gained = 0
        self.gold_gained = 0
        self.leveled_up = False

    def to_dict(self) -> dict:
        return {
            "result": "win" if self.winner and self.winner.is_player else "lose",
            "rounds": self.rounds,
            "log": self.log,
            "exp_gained": self.exp_gained,
            "gold_gained": self.gold_gained,
        }


class BattleEngine:
    """回合制战斗引擎"""

    MAX_ROUNDS = 50

    def __init__(self):
        self.attacker = None
        self.defender = None
        self.result = BattleResult()

    def setup_pve(self, player_unit: BattleUnit, map_id: int) -> bool:
        """设置 PvE 战斗"""
        monster = MONSTERS.get(map_id)
        if not monster:
            return False
        self.attacker = player_unit
        self.defender = BattleUnit(
            unit_id=-map_id,
            name=monster["name"],
            level=monster["level"],
            hp=monster["hp"],
            mp=monster["mp"],
            attack=monster["attack"],
            defense=monster["defense"],
            magic_attack=monster["magic_attack"],
            magic_defense=monster["magic_defense"],
            speed=monster["speed"],
            crit_rate=monster["crit_rate"],
            dodge_rate=monster["dodge_rate"],
            skills=[{"id": 0, "name": "砍劈", "skill_type": SkillType.PHYSICAL,
                     "base_damage": 100, "mp_cost": 0, "cooldown": 0,
                     "damage_type": 1}],
        )
        self.result.exp_gained = monster["exp_reward"]
        self.result.gold_gained = monster["gold_reward"]
        return True

    def execute(self) -> BattleResult:
        """执行完整战斗"""
        if not self.attacker or not self.defender:
            return self.result

        self.result.rounds = 0
        while self.result.rounds < self.MAX_ROUNDS:
            self.result.rounds += 1
            round_log = {"round": self.result.rounds, "actions": []}

            # 按速度判定先后手
            if self.attacker.speed >= self.defender.speed:
                first, second = self.attacker, self.defender
                first_is_attacker = True
            else:
                first, second = self.defender, self.attacker
                first_is_attacker = False

            # 先手行动
            self._process_actor_turn(first, second, round_log)
            if not second.is_alive():
                self.result.winner = first
                self.result.loser = second
                break

            # 后手行动
            self._process_actor_turn(second, first, round_log)
            if not first.is_alive():
                self.result.winner = second
                self.result.loser = first
                break

            # 减少冷却
            first.tick_cooldowns()
            second.tick_cooldowns()

            self.result.log.append(round_log)

        if not self.result.winner:
            # 50 回合上限, 按剩余 HP 百分比判定
            attacker_pct = self.attacker.hp / self.attacker.max_hp
            defender_pct = self.defender.hp / self.defender.max_hp
            if attacker_pct > defender_pct:
                self.result.winner = self.attacker
                self.result.loser = self.defender
            else:
                self.result.winner = self.defender
                self.result.loser = self.attacker

        return self.result

    def _process_actor_turn(self, actor: BattleUnit, target: BattleUnit, round_log: dict):
        """处理一个行动者的回合"""
        # 选择技能
        skill = self._select_skill(actor)
        if skill is None:
            return

        actor.use_skill(skill)

        # 闪避判定
        if random.random() < target.dodge_rate:
            round_log["actions"].append({
                "actor": actor.name,
                "skill": skill.get("name", "普攻"),
                "damage": 0,
                "target": target.name,
                "dodged": True,
                "critical": False,
            })
            return

        # 暴击判定
        is_critical = random.random() < actor.crit_rate

        # 计算伤害
        damage = self._calc_damage(actor, target, skill, is_critical)
        target.take_damage(damage)

        round_log["actions"].append({
            "actor": actor.name,
            "skill": skill.get("name", "普攻"),
            "damage": damage,
            "target": target.name,
            "dodged": False,
            "critical": is_critical,
        })

    def _select_skill(self, unit: BattleUnit) -> dict:
        """为行动者选择技能"""
        available = unit.get_available_skills()
        if not available:
            # 使用普攻
            return {"id": 0, "name": "普攻", "skill_type": SkillType.NORMAL_ATTACK,
                    "base_damage": 100, "mp_cost": 0, "cooldown": 0,
                    "damage_type": 1}

        if unit.is_player:
            # 玩家: 优先使用出战技能 (如果有可用技能则用第一个)
            return available[0]
        else:
            # 怪物: 随机选择
            return random.choice(available)

    def _calc_damage(self, actor: BattleUnit, target: BattleUnit,
                     skill: dict, is_critical: bool) -> int:
        """计算伤害"""
        skill_type = skill.get("skill_type", SkillType.NORMAL_ATTACK)
        base_damage = skill.get("base_damage", 100)
        damage_type = skill.get("damage_type", 1)
        skill_coeff = base_damage / 100.0

        if damage_type == 1:  # 物理伤害
            raw = actor.attack * skill_coeff - target.defense * 0.5
        else:  # 魔法伤害
            raw = actor.magic_attack * skill_coeff - target.magic_defense * 0.5

        # 浮动 (-5% ~ +5%)
        variance = random.uniform(-0.05, 0.05)
        damage = int(raw * (1 + variance))

        # 暴击
        if is_critical:
            damage = int(damage * 1.5)

        return max(1, damage)
