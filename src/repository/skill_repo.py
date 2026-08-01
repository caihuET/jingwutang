"""技能数据访问"""
from src.models.skill import PlayerSkill, SkillDefinition, SkillEffect
from sqlalchemy import text


class SkillRepository:
    def __init__(self, db):
        self.db = db

    def get_player_skills(self, player_id: int):
        return self.db.query(PlayerSkill).filter(
            PlayerSkill.player_id == player_id
        ).all()

    def get_slotted_skills(self, player_id: int):
        return self.db.query(PlayerSkill).filter(
            PlayerSkill.player_id == player_id,
            PlayerSkill.slot_position.isnot(None)
        ).order_by(PlayerSkill.slot_position).all()

    def add_proficiency(self, skill_id: int, amount: int = 1):
        sk = self.db.query(PlayerSkill).filter(PlayerSkill.id == skill_id).first()
        if sk:
            sk.proficiency += amount
            self.db.commit()

    def get_definitions_by_ids(self, skill_ids: list) -> dict:
        """按技能定义 ID 批量查询，返回 id -> SkillDefinition"""
        if not skill_ids:
            return {}
        rows = self.db.query(SkillDefinition).filter(
            SkillDefinition.id.in_(skill_ids)
        ).all()
        return {d.id: d for d in rows}

    def get_effects_by_skill_ids(self, skill_ids: list) -> dict:
        """按技能定义 ID 批量查询附加效果，返回 skill_id -> [SkillEffect]"""
        if not skill_ids:
            return {}
        rows = self.db.query(SkillEffect).filter(
            SkillEffect.skill_id.in_(skill_ids)
        ).order_by(SkillEffect.skill_id, SkillEffect.sort_order).all()
        result = {}
        for row in rows:
            result.setdefault(row.skill_id, []).append(row)
        return result
