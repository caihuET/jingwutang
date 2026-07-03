"""装备服务"""
import random
import math
from src.repository.equipment_repo import EquipmentRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.utils.constants import ENHANCE_RATES, EquipSlot
from src.service.task_service import TaskService
from src.models.equipment import PlayerEquipment


class EquipmentService:
    def __init__(self, db):
        self.repo = EquipmentRepository(db)

    def get_equipment(self, player_id: int) -> list:
        items = self.repo.get_player_equipment(player_id)
        result = []
        for eq in items:
            defn = self.repo.get_definition(eq.equip_def_id)
            result.append({
                "id": eq.id,
                "name": defn.name if defn else "未知",
                "slot": eq.slot,
                "quality": eq.quality,
                "is_equipped": eq.is_equipped,
                "enhance_level": eq.enhance_level,
                "stats": {
                    "attack": (defn.base_attack if defn else 0) + (eq.enhance_attack or 0),
                    "defense": (defn.base_defense if defn else 0) + (eq.enhance_defense or 0),
                    "hp": (defn.base_hp if defn else 0) + (eq.enhance_hp or 0),
                }
            })
        return result

    def equip(self, player_id: int, equip_id: int) -> bool:
        eq = self.repo.get_by_id(equip_id)
        if not eq or eq.player_id != player_id:
            raise GameException(ErrorCode.EQUIP_NOT_FOUND)
        # 先卸下同槽位的已装备物品
        old_equipped = self.repo.db.query(PlayerEquipment).filter(
            PlayerEquipment.player_id == player_id,
            PlayerEquipment.slot == eq.slot,
            PlayerEquipment.is_equipped == 1,
            PlayerEquipment.id != equip_id,
        ).all()
        for old in old_equipped:
            old.is_equipped = 0
        eq.is_equipped = 1
        self.repo.db.commit()
        TaskService(self.repo.db).check_progress(player_id, "equip_item", 1)
        return True

    def unequip(self, player_id: int, equip_id: int) -> bool:
        eq = self.repo.get_by_id(equip_id)
        if not eq or eq.player_id != player_id:
            raise GameException(ErrorCode.EQUIP_NOT_FOUND)
        eq.is_equipped = 0
        self.repo.db.commit()
        return True

    def enhance(self, player_id: int, equip_id: int) -> dict:
        """装备强化"""
        eq = self.repo.get_by_id(equip_id)
        if not eq or eq.player_id != player_id:
            raise GameException(ErrorCode.EQUIP_NOT_FOUND)
        if eq.enhance_level >= 15:
            raise GameException(ErrorCode.EQUIP_MAX_LEVEL, "已达最高强化等级")

        rate = ENHANCE_RATES.get(eq.enhance_level, 0.5)
        success = random.random() < rate

        if success:
            eq.enhance_level += 1
            eq.enhance_attack = (eq.enhance_attack or 0) + 5
            eq.enhance_defense = (eq.enhance_defense or 0) + 3
            eq.enhance_hp = (eq.enhance_hp or 0) + 10
        else:
            if eq.enhance_level >= 3:
                eq.enhance_level = max(0, eq.enhance_level - 1)

        self.repo.db.commit()
        if success:
            TaskService(self.repo.db).check_progress(player_id, "enhance_equip", 1)
        return {"success": success, "new_level": eq.enhance_level}

    def sell(self, player_id: int, equip_id: int) -> dict:
        """出售装备（获得金币）"""
        from src.models.player import Player
        eq = self.repo.get_by_id(equip_id)
        if not eq or eq.player_id != player_id:
            raise GameException(ErrorCode.EQUIP_NOT_FOUND)
        if eq.is_equipped:
            raise GameException(ErrorCode.PARAM_INVALID, "请先卸下装备再出售")
        player = self.repo.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        # 根据品质和强化等级计算售价
        price = 10 + max(0, eq.quality - 1) * 20 + eq.enhance_level * 50
        player.gold += price
        self.repo.db.delete(eq)
        self.repo.db.commit()
        return {"gold_gained": price, "total_gold": player.gold}
