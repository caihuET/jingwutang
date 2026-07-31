"""商城与物品模型"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func
from src.models.database import Base


class ShopItem(Base):
    """商城商品定义"""
    __tablename__ = "shop_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    category = Column(Integer, nullable=False)
    item_type = Column(Integer, nullable=False)
    effect_value = Column(Integer, default=0)
    price_type = Column(Integer, default=1)
    price = Column(Integer, default=0)
    daily_limit = Column(Integer, default=0)
    description = Column(String(128), default="")
    sort_order = Column(Integer, default=0)


class PlayerItem(Base):
    """玩家背包物品"""
    __tablename__ = "player_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    player_id = Column(BigInteger, nullable=False, index=True)
    item_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=0)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)


class PurchaseLog(Base):
    """商城购买记录（用于每日限购校验）"""
    __tablename__ = "shop_purchase_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    player_id = Column(BigInteger, nullable=False, index=True)
    item_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)
