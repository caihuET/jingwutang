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
