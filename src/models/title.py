"""称号模型"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func
from src.models.database import Base


class TitleDefinition(Base):
    """称号定义"""
    __tablename__ = "title_definitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    title_level = Column(Integer, default=1)
    source_type = Column(Integer, nullable=False)
    source_id = Column(Integer, nullable=True)
    display_effect = Column(String(32), default="none")
    description = Column(String(128), default="")
    sort_order = Column(Integer, default=0)
    is_active = Column(Integer, default=1)


class PlayerTitle(Base):
    """角色已获得称号"""
    __tablename__ = "player_titles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    player_id = Column(BigInteger, nullable=False, index=True)
    title_id = Column(Integer, nullable=False)
    obtained_at = Column(DateTime(6), default=func.now(), nullable=False)
    is_equipped = Column(Integer, default=0)
