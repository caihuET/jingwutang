"""技能服务"""
from src.repository.skill_repo import SkillRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode


class SkillService:
    def __init__(self, db):
        self.repo = SkillRepository(db)

    def get_skills(self, player_id: int) -> list:
        from src.models.skill import SkillDefinition
        skills = self.repo.get_player_skills(player_id)
        skill_ids = [s.skill_id for s in skills]
        defs = {}
        if skill_ids:
            for d in self.repo.db.query(SkillDefinition).filter(SkillDefinition.id.in_(skill_ids)).all():
                defs[d.id] = d.name
        return [{
            "id": s.id,
            "skill_id": s.skill_id,
            "name": defs.get(s.skill_id, f"技能{s.skill_id}"),
            "level": s.level,
            "proficiency": s.proficiency,
            "slot_position": s.slot_position,
            "is_learned": s.is_learned,
        } for s in skills]

    def set_slots(self, player_id: int, skill_ids: list) -> bool:
        """设置出战技能栏 (最多 4 个)"""
        if len(skill_ids) > 4:
            raise GameException(ErrorCode.PARAM_INVALID, "最多 4 个出战技能")
        skills = self.repo.get_player_skills(player_id)
        skill_map = {s.id: s for s in skills}

        # 全部清除
        for s in skills:
            s.slot_position = None

        # 设置出战
        for i, sid in enumerate(skill_ids):
            if sid in skill_map:
                skill_map[sid].slot_position = i + 1

        self.repo.db.commit()
        return True

    def add_proficiency(self, player_skill_id: int, amount: int = 1):
        """增加技能熟练度"""
        self.repo.add_proficiency(player_skill_id, amount)
