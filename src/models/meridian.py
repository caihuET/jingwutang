"""经脉模型"""
from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
from src.models.database import Base


class MeridianDefinition(Base):
    """经脉定义"""
    __tablename__ = "meridian_definitions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(16), nullable=False)
    acupoint_count = Column(Integer, default=10)
    bonus_hp = Column(Integer, default=0)
    bonus_attack = Column(Integer, default=0)
    bonus_defense = Column(Integer, default=0)


class MeridianAcupoint(Base):
    """穴位定义"""
    __tablename__ = "meridian_acupoints"
    id = Column(Integer, primary_key=True, autoincrement=True)
    meridian_id = Column(Integer, ForeignKey("meridian_definitions.id"), nullable=False)
    position = Column(Integer, nullable=False)
    name = Column(String(16), nullable=False)
    reputation_cost = Column(Integer, nullable=False)
    bonus_hp = Column(Integer, default=0)
    bonus_attack = Column(Integer, default=0)
    bonus_defense = Column(Integer, default=0)
    bonus_speed = Column(Integer, default=0)


class PlayerMeridian(Base):
    """角色经脉进度"""
    __tablename__ = "player_meridians"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    player_id = Column(BigInteger, ForeignKey("players.id"), nullable=False, index=True)
    meridian_id = Column(Integer, ForeignKey("meridian_definitions.id"), nullable=False)
    current_acupoint = Column(Integer, default=0)
