"""技能数据访问"""
from src.models.skill import PlayerSkill
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
