"""商城与物品数据访问"""
from src.models.shop import ShopItem, PlayerItem, PurchaseLog


class ShopRepository:
    def __init__(self, db):
        self.db = db

    def get_all_items(self):
        return self.db.query(ShopItem).order_by(
            ShopItem.category, ShopItem.sort_order
        ).all()

    def get_item(self, item_id: int):
        return self.db.query(ShopItem).filter(ShopItem.id == item_id).first()

    def get_player_item(self, player_id: int, item_id: int):
        return self.db.query(PlayerItem).filter(
            PlayerItem.player_id == player_id,
            PlayerItem.item_id == item_id,
        ).first()

    def get_player_items(self, player_id: int):
        return self.db.query(PlayerItem).filter(
            PlayerItem.player_id == player_id
        ).all()

    def get_today_purchase(self, player_id: int, item_id: int, start_at):
        return self.db.query(PurchaseLog).filter(
            PurchaseLog.player_id == player_id,
            PurchaseLog.item_id == item_id,
            PurchaseLog.created_at >= start_at,
        ).all()
