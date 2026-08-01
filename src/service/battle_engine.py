"""核心战斗引擎 - 回合制战斗逻辑（含杀伤距离、单群攻、状态效果）"""
import random

from src.utils.constants import (
    RANGE_DODGE_MODIFIER,
    SKILL_AOE_DAMAGE_MULTIPLIER,
    SKILL_EFFECT_NAMES,
    SkillEffectType,
    SkillRange,
    SkillTarget,
    SkillType,
    get_proficiency_bonus,
)


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
    """战斗单元（玩家或怪物）"""

    def __init__(self, unit_id: int, name: str, level: int,
                 hp: int, mp: int, attack: int, defense: int,
                 magic_attack: int, magic_defense: int, speed: int,
                 crit_rate: float = 0.05, dodge_rate: float = 0.05,
                 skills: list = None, is_player: bool = False,
                 heal_per_round: int = 0, lifesteal: float = 0.0,
                 reflect_rate: float = 0.0,
                 statuses: dict = None, shield: int = 0,
                 damage_bonus: int = 0):
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
        self.cooldowns = {}
        self.heal_per_round = heal_per_round
        self.lifesteal = lifesteal
        self.reflect_rate = reflect_rate
        self.statuses = dict(statuses or {})
        self.shield = shield
        self.damage_bonus = damage_bonus

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, damage: int):
        self.hp = max(0, self.hp - damage)

    def can_use_skill(self, skill: dict) -> bool:
        skill_id = skill.get("id", 0)
        if skill_id in self.cooldowns and self.cooldowns[skill_id] > 0:
            return False
        if self.mp < skill.get("mp_cost", 0):
            return False
        return True

    def use_skill(self, skill: dict):
        self.mp -= skill.get("mp_cost", 0)
        cd = skill.get("cooldown", 0)
        if cd > 0:
            self.cooldowns[skill.get("id", 0)] = cd

    def tick_cooldowns(self):
        for skill_id in list(self.cooldowns.keys()):
            self.cooldowns[skill_id] -= 1
            if self.cooldowns[skill_id] <= 0:
                del self.cooldowns[skill_id]

    def get_available_skills(self) -> list:
        return [s for s in self.skills if self.can_use_skill(s)]

    def has_status(self, effect_type: str) -> bool:
        return effect_type in self.statuses

    def status_value(self, effect_type: str) -> int:
        status = self.statuses.get(effect_type)
        return status["value"] if status else 0


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
            skills=[{
                "id": 0, "name": "砍劈", "skill_type": SkillType.PHYSICAL,
                "base_damage": 100, "mp_cost": 0, "cooldown": 0,
                "damage_type": 1, "target_type": SkillTarget.SINGLE,
                "attack_range": SkillRange.MID, "proficiency": 0,
                "effects": [],
            }],
        )
        self.result.exp_gained = monster["exp_reward"]
        self.result.gold_gained = monster["gold_reward"]
        return True

    def execute(self) -> BattleResult:
        if not self.attacker or not self.defender:
            return self.result

        self.result.rounds = 0
        while self.result.rounds < self.MAX_ROUNDS:
            self.result.rounds += 1
            round_log = {"round": self.result.rounds, "actions": []}
            self._apply_round_heal(round_log)

            if self._effective_speed(self.attacker) >= self._effective_speed(self.defender):
                first, second = self.attacker, self.defender
            else:
                first, second = self.defender, self.attacker

            self._process_actor_turn(first, second, round_log)
            if not second.is_alive():
                self.result.winner = first
                self.result.loser = second
                break

            self._process_actor_turn(second, first, round_log)
            if not first.is_alive():
                self.result.winner = second
                self.result.loser = first
                break

            first.tick_cooldowns()
            second.tick_cooldowns()
            self._tick_statuses(first)
            self._tick_statuses(second)

            self.result.log.append(round_log)

        if not self.result.winner:
            attacker_pct = self.attacker.hp / self.attacker.max_hp
            defender_pct = self.defender.hp / self.defender.max_hp
            if attacker_pct > defender_pct:
                self.result.winner = self.attacker
                self.result.loser = self.defender
            else:
                self.result.winner = self.defender
                self.result.loser = self.attacker

        return self.result

    def _process_actor_turn(self, actor: BattleUnit, target: BattleUnit,
                            round_log: dict):
        skill = self._select_skill(actor)
        if skill is None:
            return

        actor.use_skill(skill)
        effects = skill.get("effects") or []

        if skill.get("damage_type", 1) == 0:
            self._apply_skill_effects(actor, target, skill, round_log)
            round_log["actions"].append({
                "actor": actor.name,
                "skill": skill.get("name", "技能"),
                "damage": 0,
                "target": actor.name,
                "dodged": False,
                "critical": False,
                "support": True,
            })
            return

        guaranteed = any(
            e.get("effect_type") == SkillEffectType.GUARANTEED_HIT
            for e in effects
        )
        range_mod = RANGE_DODGE_MODIFIER.get(
            int(skill.get("attack_range", SkillRange.MID)), 1.0
        )
        if not guaranteed and random.random() < self._effective_dodge(target) * range_mod:
            round_log["actions"].append({
                "actor": actor.name,
                "skill": skill.get("name", "普攻"),
                "damage": 0,
                "target": target.name,
                "dodged": True,
                "critical": False,
            })
            return

        crit_bonus = sum(
            e.get("base_value", 0)
            for e in effects
            if e.get("effect_type") == SkillEffectType.CRIT_UP
        ) / 100.0
        is_critical = random.random() < self._effective_crit(actor) + crit_bonus
        damage = self._calc_damage(actor, target, skill, is_critical)
        self._deal_damage(target, damage, round_log)

        lifesteal = actor.lifesteal + sum(
            e.get("base_value", 0)
            for e in effects
            if e.get("effect_type") == SkillEffectType.LIFESTEAL
        ) / 100.0
        if lifesteal > 0 and damage > 0:
            actor.hp = min(actor.max_hp, actor.hp + int(damage * min(1.0, lifesteal)))

        reflect_rate = target.reflect_rate
        if reflect_rate > 0 and damage > 0:
            self._deal_damage(actor, int(damage * reflect_rate), round_log)

        self._apply_skill_effects(actor, target, skill, round_log)
        round_log["actions"].append({
            "actor": actor.name,
            "skill": skill.get("name", "普攻"),
            "damage": damage,
            "target": target.name,
            "dodged": False,
            "critical": is_critical,
        })

    def _apply_round_heal(self, round_log: dict):
        """回合开始处理被动回血与持续状态（中毒/灼烧/持续治疗）"""
        for unit in (self.attacker, self.defender):
            if unit.hp <= 0:
                continue
            if unit.heal_per_round > 0:
                healed = min(unit.max_hp - unit.hp, unit.heal_per_round)
                if healed > 0:
                    unit.hp += healed
                    round_log["actions"].append({
                        "actor": unit.name,
                        "skill": "被动回复",
                        "damage": healed,
                        "target": unit.name,
                        "dodged": False,
                        "critical": False,
                    })
            for etype in (SkillEffectType.POISON, SkillEffectType.BURN):
                status = unit.statuses.get(etype)
                if status and status.get("damage", 0) > 0:
                    self._deal_damage(unit, status["damage"], round_log)
            hot = unit.statuses.get(SkillEffectType.HEAL_OVER_TIME)
            if hot and hot.get("heal_per_round", 0) > 0:
                healed = min(unit.max_hp - unit.hp, hot["heal_per_round"])
                if healed > 0:
                    unit.hp += healed
                    round_log["actions"].append({
                        "actor": unit.name,
                        "skill": "持续治疗",
                        "damage": healed,
                        "target": unit.name,
                        "dodged": False,
                        "critical": False,
                    })

    def _tick_statuses(self, unit: BattleUnit):
        for etype in list(unit.statuses.keys()):
            status = unit.statuses[etype]
            status["duration"] -= 1
            if status["duration"] > 0:
                continue
            if etype == SkillEffectType.MAX_HP_UP and status.get("max_hp_delta", 0) > 0:
                unit.max_hp = max(1, unit.max_hp - status["max_hp_delta"])
                unit.hp = min(unit.hp, unit.max_hp)
            del unit.statuses[etype]

    def _select_skill(self, unit: BattleUnit) -> dict:
        available = unit.get_available_skills()
        if not available:
            return {
                "id": 0, "name": "普攻", "skill_type": SkillType.NORMAL_ATTACK,
                "base_damage": 100, "mp_cost": 0, "cooldown": 0,
                "damage_type": 1, "target_type": SkillTarget.SINGLE,
                "attack_range": SkillRange.MID, "proficiency": 0,
                "effects": [],
            }
        if unit.is_player:
            return available[0]
        return random.choice(available)

    def _calc_damage(self, actor: BattleUnit, target: BattleUnit,
                     skill: dict, is_critical: bool) -> int:
        base_damage = skill.get("base_damage", 100)
        damage_type = skill.get("damage_type", 1)
        skill_coeff = base_damage / 100.0
        aoe_mult = (
            SKILL_AOE_DAMAGE_MULTIPLIER
            if int(skill.get("target_type", SkillTarget.SINGLE)) == SkillTarget.AOE
            else 1.0
        )
        proficiency_mult = 1 + get_proficiency_bonus(
            int(skill.get("proficiency", 0))
        ) / 100.0
        bonus_mult = 1 + (actor.damage_bonus or 0) / 100.0
        armor_pen = sum(
            e.get("base_value", 0)
            for e in (skill.get("effects") or [])
            if e.get("effect_type") == SkillEffectType.ARMOR_PENETRATION
        )
        pen_rate = min(0.9, armor_pen / 100.0)
        if damage_type == 1:
            raw = actor.attack * skill_coeff - self._effective_defense(target) * (1 - pen_rate) * 0.5
        else:
            raw = self._effective_magic_attack(actor) * skill_coeff - target.magic_defense * (1 - pen_rate) * 0.5

        raw *= aoe_mult * proficiency_mult * bonus_mult
        variance = random.uniform(-0.05, 0.05)
        damage = int(raw * (1 + variance))
        if is_critical:
            damage = int(damage * 1.5)
        return max(1, damage)

    def _apply_skill_effects(self, actor: BattleUnit, target: BattleUnit,
                             skill: dict, round_log: dict):
        effects = skill.get("effects") or []
        level = int(skill.get("level", 1))
        for eff in effects:
            etype = eff.get("effect_type")
            value = int(eff.get("base_value", 0)) + int(eff.get("value_per_level", 0)) * (level - 1)
            duration = int(eff.get("duration", 0))
            tgt = target if int(eff.get("target_type", 1)) == 1 else actor
            if etype == SkillEffectType.HEAL:
                heal = max(1, int(actor.magic_attack * value / 100))
                healed = min(tgt.max_hp - tgt.hp, heal)
                tgt.hp += healed
                round_log["actions"].append({
                    "actor": actor.name, "skill": "治疗", "damage": healed,
                    "target": tgt.name, "dodged": False, "critical": False,
                })
            elif etype == SkillEffectType.HEAL_OVER_TIME:
                self._apply_status(tgt, etype, value, duration, {
                    "heal_per_round": max(1, int(actor.magic_attack * value / 100)),
                })
            elif etype in (SkillEffectType.BURN, SkillEffectType.POISON):
                self._apply_status(tgt, etype, value, duration, {
                    "damage": max(1, int(actor.magic_attack * value / 100)),
                })
            elif etype == SkillEffectType.DEFENSE_UP:
                self._apply_status(actor, etype, value, duration)
            elif etype == SkillEffectType.DEFENSE_DOWN:
                self._apply_status(tgt, etype, value, duration)
            elif etype == SkillEffectType.DODGE_UP:
                self._apply_status(actor, etype, value, duration)
            elif etype == SkillEffectType.DODGE_DOWN:
                self._apply_status(tgt, etype, value, duration)
            elif etype == SkillEffectType.SPEED_UP:
                self._apply_status(actor, etype, value, duration)
            elif etype == SkillEffectType.SPEED_DOWN:
                self._apply_status(tgt, etype, value, duration)
            elif etype == SkillEffectType.MAGIC_ATTACK_UP:
                self._apply_status(actor, etype, value, duration)
            elif etype == SkillEffectType.MAX_HP_UP:
                delta = int(actor.max_hp * value / 100)
                actor.max_hp += delta
                actor.hp += delta
                self._apply_status(actor, etype, value, duration, {
                    "max_hp_delta": delta,
                })
            elif etype == SkillEffectType.REFLECT:
                actor.reflect_rate = min(0.8, actor.reflect_rate + value / 100)
            elif etype == SkillEffectType.LIFESTEAL:
                actor.lifesteal = min(1.0, actor.lifesteal + value / 100)
            elif etype == SkillEffectType.SHIELD:
                tgt.shield += max(1, int(actor.magic_attack * value / 100))
            elif etype == SkillEffectType.BACKLASH:
                self._deal_damage(actor, max(1, int(actor.max_hp * value / 100)), round_log)
            elif etype == SkillEffectType.STACK_DAMAGE:
                actor.damage_bonus = min(30, (actor.damage_bonus or 0) + value)
            elif etype == SkillEffectType.UNDYING:
                self._apply_status(actor, etype, 0, duration)

    def _apply_status(self, unit: BattleUnit, effect_type: str,
                      value: int, duration: int, extra: dict = None):
        unit.statuses[effect_type] = {"duration": duration, "value": value}
        if extra:
            unit.statuses[effect_type].update(extra)

    def _deal_damage(self, target: BattleUnit, damage: int, round_log: dict):
        if damage <= 0:
            return
        if target.shield > 0:
            absorbed = min(target.shield, damage)
            target.shield -= absorbed
            damage -= absorbed
            round_log["actions"].append({
                "actor": target.name, "skill": "护盾", "damage": absorbed,
                "target": target.name, "dodged": False, "critical": False,
            })
        if damage <= 0:
            return
        if damage >= target.hp and target.has_status(SkillEffectType.UNDYING):
            del target.statuses[SkillEffectType.UNDYING]
            if target.hp > 1:
                target.hp = 1
                return
        target.take_damage(damage)

    def _effective_speed(self, unit: BattleUnit) -> int:
        bonus = unit.status_value(SkillEffectType.SPEED_UP) - unit.status_value(SkillEffectType.SPEED_DOWN)
        return max(1, int(unit.speed * (1 + bonus / 100)))

    def _effective_defense(self, unit: BattleUnit) -> int:
        bonus = unit.status_value(SkillEffectType.DEFENSE_UP) - unit.status_value(SkillEffectType.DEFENSE_DOWN)
        return max(0, int(unit.defense * (1 + bonus / 100)))

    def _effective_magic_attack(self, unit: BattleUnit) -> int:
        bonus = unit.status_value(SkillEffectType.MAGIC_ATTACK_UP)
        return max(0, int(unit.magic_attack * (1 + bonus / 100)))

    def _effective_dodge(self, unit: BattleUnit) -> float:
        bonus = unit.status_value(SkillEffectType.DODGE_UP) - unit.status_value(SkillEffectType.DODGE_DOWN)
        return max(0.0, unit.dodge_rate * (1 + bonus / 100))

    def _effective_crit(self, unit: BattleUnit) -> float:
        return max(0.0, unit.crit_rate)


__all__ = ["BattleEngine", "BattleUnit", "BattleResult", "MONSTERS"]
