"""装备模型"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func, ForeignKey
from src.models.database import Base


class EquipmentDefinition(Base):
    """装备模板"""
    __tablename__ = "equipment_definitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    slot = Column(Integer, nullable=False)
    quality = Column(Integer, nullable=False)
    level_required = Column(Integer, default=1)
    base_attack = Column(Integer, default=0)
    base_defense = Column(Integer, default=0)
    base_magic_attack = Column(Integer, default=0)
    base_magic_defense = Column(Integer, default=0)
    base_hp = Column(Integer, default=0)
    base_speed = Column(Integer, default=0)
    max_gem_slots = Column(Integer, default=0)
    is_sellable = Column(Integer, default=1)
    sell_price = Column(Integer, default=0)


class PlayerEquipment(Base):
    """角色装备实例"""
    __tablename__ = "player_equipment"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    player_id = Column(BigInteger, ForeignKey("players.id"), nullable=False)
    equip_def_id = Column(Integer, ForeignKey("equipment_definitions.id"), nullable=False)
    slot = Column(Integer, nullable=False)
    quality = Column(Integer, nullable=False)
    is_equipped = Column(Integer, default=0)
    enhance_level = Column(Integer, default=0)
    enhance_attack = Column(Integer, default=0)
    enhance_defense = Column(Integer, default=0)
    enhance_hp = Column(Integer, default=0)
    durability = Column(Integer, default=100)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)
