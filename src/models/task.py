"""任务模型"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Text, func, ForeignKey
from src.models.database import Base


class TaskDefinition(Base):
    """任务定义"""
    __tablename__ = "task_definitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    task_type = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    requirement_type = Column(String(32), nullable=False)
    requirement_value = Column(Integer, nullable=False)
    reward_exp = Column(Integer, default=0)
    reward_gold = Column(Integer, default=0)
    reward_reputation = Column(Integer, default=0)
    reward_item_id = Column(Integer, nullable=True)
    reward_title_id = Column(Integer, nullable=True)
    daily_refresh = Column(Integer, default=0)
    min_level = Column(Integer, default=1)
    max_level = Column(Integer, nullable=True)
    sort_order = Column(Integer, default=0)


class PlayerTask(Base):
    """角色任务进度"""
    __tablename__ = "player_tasks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    player_id = Column(BigInteger, ForeignKey("players.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("task_definitions.id"), nullable=False)
    progress = Column(Integer, default=0)
    target = Column(Integer, nullable=False)
    status = Column(Integer, default=0)
    completed_at = Column(DateTime(6), nullable=True)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)
