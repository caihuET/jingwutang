"""技能模型"""
from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
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
