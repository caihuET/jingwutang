"""角色模型"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Date, func, ForeignKey
from src.models.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(32), unique=True, nullable=False, index=True)
    gender = Column(Integer, nullable=False)
    school_id = Column(Integer, nullable=False)
    guild_id = Column(Integer, nullable=True)
    level = Column(Integer, default=1)
    exp = Column(BigInteger, default=0)
    hp = Column(Integer, default=100)
    max_hp = Column(Integer, default=100)
    mp = Column(Integer, default=50)
    max_mp = Column(Integer, default=50)
    stamina = Column(Integer, default=100)
    gold = Column(BigInteger, default=0)
    ingot = Column(Integer, default=0)
    reputation = Column(Integer, default=0)
    combat_power = Column(Integer, default=0)
    title = Column(String(64), nullable=True)
    free_points = Column(Integer, default=0)
    vip_until = Column(DateTime(6), nullable=True)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)
    updated_at = Column(DateTime(6), default=func.now(), onupdate=func.now(), nullable=False)
