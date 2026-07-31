"""技能模型"""
from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, SmallInteger
from src.models.database import Base


class PlayerSkill(Base):
    """角色技能"""
    __tablename__ = "player_skills"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    player_id = Column(BigInteger, ForeignKey("players.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skill_definitions.id"), nullable=False)
    level = Column(Integer, default=1)
    proficiency = Column(Integer, default=0)
    slot_position = Column(Integer, nullable=True)
    is_learned = Column(Integer, default=1)


class SkillDefinition(Base):
    """技能定义表"""
    __tablename__ = "skill_definitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    school_id = Column(Integer, nullable=True)
    skill_type = Column(SmallInteger, nullable=False)
    damage_type = Column(SmallInteger, nullable=False)
    base_damage = Column(Integer, default=0)
    damage_per_level = Column(Integer, default=0)
    mp_cost = Column(Integer, default=0)
    mp_cost_per_level = Column(Integer, default=0)
    cooldown = Column(Integer, default=0)
    target_type = Column(SmallInteger, default=1)
    max_level = Column(Integer, default=10)
    unlock_level = Column(Integer, default=0)
    description = Column(String(256), nullable=False)
