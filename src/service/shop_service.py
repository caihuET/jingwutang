"""商城与物品服务"""
import random
from datetime import datetime, timedelta
from src.repository.shop_repo import ShopRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.service.title_service import TitleService
from src.models.shop import PlayerItem, PurchaseLog


class ShopService:
    def __init__(self, db):
        self.repo = ShopRepository(db)

    def get_shop(self, category: int = 0) -> list:
        items = self.repo.get_all_items()
        result = []
        for item in items:
            if category and item.category != category:
                continue
            result.append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "category_name": self._category_name(item.category),
                "item_type": item.item_type,
                "effect_value": item.effect_value,
                "price_type": item.price_type,
                "price_type_name": self._price_name(item.price_type),
                "price": item.price,
                "daily_limit": item.daily_limit,
                "description": item.description,
            })
        return result

    def buy(self, player_id: int, item_id: int, quantity: int = 1) -> dict:
        item = self.repo.get_item(item_id)
        if not item:
            raise GameException(ErrorCode.ITEM_NOT_FOUND, "商品不存在")
        if quantity <= 0 or quantity > 99:
            raise GameException(ErrorCode.PARAM_INVALID, "购买数量不合法")
        self._check_daily_limit(player_id, item, quantity)
        player = self._get_player(player_id)
        cost = item.price * quantity
        self._pay(player, item.price_type, cost)
        self._grant_item(player_id, item.id, quantity)
        self.repo.db.add(PurchaseLog(
            player_id=player_id, item_id=item.id, quantity=quantity,
        ))
        self.repo.db.commit()
        return {"item_id": item.id, "name": item.name,
                "quantity": quantity, "cost": cost}

    def get_inventory(self, player_id: int) -> list:
        rows = self.repo.get_player_items(player_id)
        result = []
        for row in rows:
            item = self.repo.get_item(row.item_id)
            result.append({
                "item_id": row.item_id,
                "name": item.name if item else "未知物品",
                "item_type": item.item_type if item else 0,
                "effect_value": item.effect_value if item else 0,
                "quantity": row.quantity,
                "description": item.description if item else "",
            })
        return result

    def use_item(self, player_id: int, item_id: int, quantity: int = 1) -> dict:
        item = self.repo.get_item(item_id)
        if not item:
            raise GameException(ErrorCode.ITEM_NOT_FOUND, "物品不存在")
        row = self.repo.get_player_item(player_id, item_id)
        if not row or row.quantity < quantity:
            raise GameException(ErrorCode.ITEM_NOT_FOUND, "物品数量不足")
        player = self._get_player(player_id)
        if item.item_type == 1:
            self._use_stamina(player, item.effect_value * quantity)
        elif item.item_type == 2:
            self._use_exp(player, item.effect_value * quantity)
        elif item.item_type == 3:
            raise GameException(ErrorCode.PARAM_INVALID, "强化石用于装备强化，无需使用")
        elif item.item_type == 4:
            granted = TitleService(self.repo.db).grant_shop_title(player_id, item.id)
            if not granted:
                player.title = item.name.replace("称号·", "") if item.name.startswith("称号·") else item.name
        elif item.item_type in (5, 6):
            days = item.effect_value or 30
            player.vip_until = datetime.utcnow() + timedelta(days=days)
        row.quantity -= quantity
        self.repo.db.commit()
        return {"item_id": item.id, "name": item.name,
                "quantity_left": row.quantity}

    def _check_daily_limit(self, player_id: int, item, quantity: int):
        if not item.daily_limit:
            return
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        logs = self.repo.get_today_purchase(player_id, item.id, today)
        bought = sum(log.quantity for log in logs)
        if bought + quantity > item.daily_limit:
            raise GameException(ErrorCode.DAILY_LIMIT, "已达今日购买上限")

    def _pay(self, player, price_type: int, cost: int):
        if price_type == 1:
            if player.gold < cost:
                raise GameException(ErrorCode.GOLD_NOT_ENOUGH, "金币不足")
            player.gold -= cost
        elif price_type == 2:
            if player.ingot < cost:
                raise GameException(ErrorCode.INGOT_NOT_ENOUGH, "元宝不足")
            player.ingot -= cost
        elif price_type == 3:
            if player.reputation < cost:
                raise GameException(ErrorCode.REPUTATION_NOT_ENOUGH, "修为不足")
            player.reputation -= cost
        else:
            raise GameException(ErrorCode.PARAM_INVALID, "不支持的价格类型")

    def _grant_item(self, player_id: int, item_id: int, quantity: int):
        row = self.repo.get_player_item(player_id, item_id)
        if row:
            row.quantity += quantity
        else:
            self.repo.db.add(PlayerItem(
                player_id=player_id, item_id=item_id, quantity=quantity,
            ))

    def _get_player(self, player_id: int):
        from src.models.player import Player
        player = self.repo.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        return player

    def _use_stamina(self, player, amount: int):
        max_stamina = min(150, 100 + (player.level // 10) * 5)
        player.stamina = min(max_stamina, player.stamina + amount)

    def _use_exp(self, player, amount: int):
        from src.utils.constants import EXP_TABLE
        player.exp += amount
        while player.level < 100 and player.exp >= EXP_TABLE[player.level]:
            player.exp -= EXP_TABLE[player.level]
            player.level += 1
            player.free_points += 5
            player.max_hp += 20
            player.max_mp += 10

    def _category_name(self, category: int) -> str:
        return {1: "消耗品", 2: "强化材料", 3: "外观", 4: "VIP"}.get(category, "其他")

    def _price_name(self, price_type: int) -> str:
        return {1: "金币", 2: "元宝", 3: "修为", 4: "帮贡"}.get(price_type, "金币")
