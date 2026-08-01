"""技能服务"""
from src.repository.skill_repo import SkillRepository
from src.utils.errors import GameException
from src.utils.constants import (
    ErrorCode,
    SKILL_AOE_DAMAGE_MULTIPLIER,
    SKILL_EFFECT_NAMES,
    SkillEffectType,
    SkillRange,
    SkillTarget,
    SkillType,
    calc_skill_power,
    get_proficiency_bonus,
    get_skill_cooldown,
    get_standard_monster_defense,
)
from src.utils.constants import get_passive_name
from src.service.battle_service import BattleService


class SkillService:
    def __init__(self, db):
        self.repo = SkillRepository(db)

    def get_skills(self, player_id: int) -> list:
        skills = self.repo.get_player_skills(player_id)
        skill_ids = [s.skill_id for s in skills]
        defs = self.repo.get_definitions_by_ids(skill_ids)
        effects_map = self.repo.get_effects_by_skill_ids(skill_ids)
        stats = BattleService(self.repo.db).get_combat_stats(player_id)
        result = []
        for s in skills:
            d = defs.get(s.skill_id)
            name = f"技能{s.skill_id}"
            if d:
                name = d.name
                if d.skill_type == SkillType.PASSIVE:
                    name = get_passive_name(d.school_id or 0, d.name)
            result.append({
                "id": s.id,
                "skill_id": s.skill_id,
                "name": name,
                "skill_type": d.skill_type if d else 0,
                "description": d.description if d else "",
                "level": s.level,
                "proficiency": s.proficiency,
                "slot_position": s.slot_position,
                "is_learned": s.is_learned,
                "proficiency_bonus": get_proficiency_bonus(s.proficiency),
            })
            if d:
                result[-1].update(
                    self._skill_meta(d, s, effects_map.get(s.skill_id, []), stats)
                )
        return result

    def _skill_meta(self, d, s, effects, stats) -> dict:
        """组装技能战斗属性（距离/目标/威力/冷却/效果/预估伤害）"""
        cooldown = get_skill_cooldown(d.cooldown, d.target_type)
        power = calc_skill_power(d.base_damage, d.damage_per_level, s.level)
        attack_range = d.attack_range or SkillRange.MID
        target_type = d.target_type or SkillTarget.SINGLE
        meta = {
            "attack_range": attack_range,
            "attack_range_name": SkillRange.NAMES.get(attack_range, "未知"),
            "target_type": target_type,
            "target_name": SkillTarget.NAMES.get(target_type, "未知"),
            "aoe_targets": d.aoe_targets or 1,
            "base_damage": d.base_damage,
            "damage_per_level": d.damage_per_level,
            "mp_cost": d.mp_cost,
            "mp_cost_per_level": d.mp_cost_per_level,
            "cooldown": cooldown,
            "power": power,
            "power_text": f"{power}%" if d.damage_type in (1, 2) else "-",
            "effects": [self._format_effect(e, s.level) for e in effects],
        }
        if d.damage_type in (1, 2):
            meta["damage_estimate"] = self._estimate_damage(stats, d, s, effects)
        else:
            meta["damage_estimate"] = None
        return meta

    def _format_effect(self, eff, level: int) -> dict:
        """格式化技能附加效果并生成展示文案"""
        value = eff.base_value + eff.value_per_level * max(0, level - 1)
        return {
            "effect_type": eff.effect_type,
            "name": SKILL_EFFECT_NAMES.get(eff.effect_type, eff.effect_type),
            "value": value,
            "duration": eff.duration,
            "target_type": eff.target_type,
            "text": self._effect_text(eff.effect_type, value, eff.duration),
        }

    def _effect_text(self, effect_type: str, value: int, duration: int) -> str:
        """生成技能效果展示文本"""
        if effect_type == SkillEffectType.HEAL:
            return f"恢复内功攻击×{value}% 生命"
        if effect_type == SkillEffectType.HEAL_OVER_TIME:
            return f"每回合恢复内功攻击×{value}% 生命，持续{duration}回合"
        if effect_type == SkillEffectType.BURN:
            return f"每回合灼烧内功攻击×{value}%，持续{duration}回合"
        if effect_type == SkillEffectType.POISON:
            return f"每回合中毒内功攻击×{value}%，持续{duration}回合"
        if effect_type == SkillEffectType.DEFENSE_UP:
            return f"防御+{value}%，持续{duration}回合"
        if effect_type == SkillEffectType.DEFENSE_DOWN:
            return f"目标防御-{value}%，持续{duration}回合"
        if effect_type == SkillEffectType.DODGE_UP:
            return f"闪避+{value}%，持续{duration}回合"
        if effect_type == SkillEffectType.DODGE_DOWN:
            return f"目标闪避-{value}%，持续{duration}回合"
        if effect_type == SkillEffectType.SPEED_UP:
            return f"速度+{value}%，持续{duration}回合"
        if effect_type == SkillEffectType.SPEED_DOWN:
            return f"目标速度-{value}%，持续{duration}回合"
        if effect_type == SkillEffectType.CRIT_UP:
            return f"本次攻击暴击率+{value}%"
        if effect_type == SkillEffectType.MAX_HP_UP:
            return f"生命上限+{value}%，持续{duration}回合"
        if effect_type == SkillEffectType.MAGIC_ATTACK_UP:
            return f"内功攻击+{value}%，持续{duration}回合"
        if effect_type == SkillEffectType.REFLECT:
            return f"反弹{value}%伤害，持续{duration}回合"
        if effect_type == SkillEffectType.SHIELD:
            return f"获得内功攻击×{value}% 护盾"
        if effect_type == SkillEffectType.LIFESTEAL:
            return f"吸血{value}%"
        if effect_type == SkillEffectType.ARMOR_PENETRATION:
            return f"无视目标{value}%防御"
        if effect_type == SkillEffectType.GUARANTEED_HIT:
            return "必中"
        if effect_type == SkillEffectType.BACKLASH:
            return f"自身受最大生命{value}%反噬"
        if effect_type == SkillEffectType.STACK_DAMAGE:
            return f"每次使用伤害+{value}%（最多3层）"
        if effect_type == SkillEffectType.UNDYING:
            return f"致命伤害保留1点生命，持续{duration}回合"
        return ""

    def _estimate_damage(self, stats: dict, d, s, effects) -> dict:
        """按角色面板对同等级标准怪估算伤害区间"""
        if not stats:
            return {"min": 1, "max": 1}
        power = calc_skill_power(d.base_damage, d.damage_per_level, s.level)
        attack = stats["attack"] if d.damage_type == 1 else stats["magic_attack"]
        defense = get_standard_monster_defense(stats["level"])
        armor_pen = sum(
            e.base_value for e in effects
            if e.effect_type == SkillEffectType.ARMOR_PENETRATION
        )
        defense = defense * (1 - min(0.9, armor_pen / 100))
        aoe_mult = (
            SKILL_AOE_DAMAGE_MULTIPLIER
            if d.target_type == SkillTarget.AOE
            else 1.0
        )
        proficiency_mult = 1 + get_proficiency_bonus(s.proficiency) / 100
        raw = max(1, attack * power / 100 - defense * 0.5)
        raw *= aoe_mult * proficiency_mult
        return {
            "min": max(1, int(raw * 0.95)),
            "max": max(1, int(raw * 1.05)),
        }

    def set_slots(self, player_id: int, skill_ids: list) -> bool:
        """设置出战技能栏 (最多 4 个)"""
        if len(skill_ids) > 4:
            raise GameException(ErrorCode.PARAM_INVALID, "最多 4 个出战技能")
        skills = self.repo.get_player_skills(player_id)
        skill_map = {s.id: s for s in skills}
        from src.models.skill import SkillDefinition
        if skills:
            skill_ids_all = [s.skill_id for s in skills]
            defs = {d.id: d for d in self.repo.db.query(SkillDefinition).filter(
                SkillDefinition.id.in_(skill_ids_all)
            ).all()}
            for sid in skill_ids:
                ps = skill_map.get(sid)
                if ps and defs.get(ps.skill_id) and defs[ps.skill_id].skill_type == SkillType.PASSIVE:
                    raise GameException(ErrorCode.PARAM_INVALID, "被动技能不能设置到出战栏")

        # 全部清除
        for s in skills:
            s.slot_position = None

        # 设置出战
        for i, sid in enumerate(skill_ids):
            if sid in skill_map:
                skill_map[sid].slot_position = i + 1

        self.repo.db.commit()
        from src.service.task_service import TaskService
        TaskService(self.repo.db).check_progress(player_id, "skill_level", len(skill_ids))
        return True

    def add_proficiency(self, player_skill_id: int, amount: int = 1):
        """增加技能熟练度"""
        self.repo.add_proficiency(player_skill_id, amount)
