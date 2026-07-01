"""角色属性模型"""
from sqlalchemy import Column, BigInteger, Integer, DECIMAL, ForeignKey
from src.models.database import Base


class PlayerAttribute(Base):
    __tablename__ = "player_attributes"

    player_id = Column(BigInteger, ForeignKey("players.id"), primary_key=True)
    strength = Column(Integer, default=10)
    agility = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    spirit = Column(Integer, default=10)
    extra_attack = Column(Integer, default=0)
    extra_defense = Column(Integer, default=0)
    extra_magic_attack = Column(Integer, default=0)
    extra_magic_defense = Column(Integer, default=0)
    extra_hp = Column(Integer, default=0)
    extra_mp = Column(Integer, default=0)
    extra_speed = Column(Integer, default=0)
    extra_crit_rate = Column(DECIMAL(5, 2), default=0)
    extra_dodge_rate = Column(DECIMAL(5, 2), default=0)
