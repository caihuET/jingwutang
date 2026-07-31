"""装备服务"""
import random
import math
from src.repository.equipment_repo import EquipmentRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.utils.constants import ENHANCE_RATES, ENHANCE_MAX_BY_QUALITY, EquipQuality, EquipSlot
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

        "quality_name": EquipQuality.NAMES.get(eq.quality, "未知"),

        "enhance_max": ENHANCE_MAX_BY_QUALITY.get(eq.quality, 15),

        "level_required": defn.level_required if defn else 1,
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
        max_level = ENHANCE_MAX_BY_QUALITY.get(eq.quality, 15)
        if eq.enhance_level >= max_level:
            raise GameException(ErrorCode.EQUIP_MAX_LEVEL, "已达该品质最高强化等级")

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

    def get_catalog(self) -> dict:
        """获取装备图鉴（按品质分组，含各品质强化上限）"""
        defs = self.repo.get_all_definitions()
        groups = []
        for quality in range(1, 7):
            items = []
            for d in defs:
                if d.quality != quality:
                    continue
                items.append({
                    "name": d.name,
                    "slot": d.slot,
                    "level_required": d.level_required,
                    "base_attack": d.base_attack,
                    "base_defense": d.base_defense,
                    "base_magic_attack": d.base_magic_attack,
                    "base_magic_defense": d.base_magic_defense,
                    "base_hp": d.base_hp,
                    "base_speed": d.base_speed,
                })
            groups.append({
                "quality": quality,
                "quality_name": EquipQuality.NAMES.get(quality, "未知"),
                "enhance_max": ENHANCE_MAX_BY_QUALITY.get(quality, 15),
                "items": items,
            })
        return {"groups": groups}
