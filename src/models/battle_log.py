"""战斗日志模型"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, JSON, func, ForeignKey
from src.models.database import Base


class BattleLog(Base):
    """战斗记录"""
    __tablename__ = "battle_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    attacker_id = Column(BigInteger, ForeignKey("players.id"), nullable=False)
    defender_id = Column(BigInteger, nullable=True)
    battle_type = Column(Integer, nullable=False)
    result = Column(Integer, nullable=False)
    rounds = Column(Integer, nullable=False)
    log_detail = Column(JSON, nullable=True)
    drop_exp = Column(Integer, default=0)
    drop_gold = Column(Integer, default=0)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)
