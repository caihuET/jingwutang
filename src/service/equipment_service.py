"""装备服务"""
import random

from src.models.equipment import PlayerEquipment
from src.models.player import Player
from src.repository.equipment_repo import EquipmentRepository
from src.service.task_service import TaskService
from src.utils.constants import (
    AFFIX_COUNT_BY_QUALITY,
    AFFIX_STAT_KEYS,
    AFFIX_TYPES,
    AFFIX_VALUE_RANGE,
    BASE_STAT_KEYS,
    ENHANCE_MAX_BY_QUALITY,
    ENHANCE_RATES,
    EquipQuality,
    calc_enhance_stats,
    generate_affixes,
    get_base_max_stamina,
)
from src.utils.errors import GameException
from src.utils.constants import ErrorCode


class EquipmentService:
    """装备业务"""

    def __init__(self, db):
        self.repo = EquipmentRepository(db)

    def get_equipment(self, player_id: int) -> list:
        """获取角色全部装备（含基础属性、强化属性、附加属性）"""
        items = self.repo.get_player_equipment(player_id)
        affix_map = self.repo.get_affixes_by_equip_ids([eq.id for eq in items])
        result = []
        for eq in items:
            defn = self.repo.get_definition(eq.equip_def_id)
            affixes = affix_map.get(eq.id, [])
            result.append(self._build_equip_item(eq, defn, affixes))
        return result

    def _build_equip_item(self, eq, defn, affixes) -> dict:
        """组装单件装备返回结构"""
        base_stats = self._base_stats(eq, defn)
        enhance_stats = self._enhance_stats(eq, defn)
        stats = {key: base_stats[key] + enhance_stats[key] for key in BASE_STAT_KEYS}
        max_level = ENHANCE_MAX_BY_QUALITY.get(eq.quality, 15)
        enhance_preview = None
        enhance_rate = None
        if eq.enhance_level < max_level:
            enhance_preview = self._calc_stats_at_level(eq, defn, eq.enhance_level + 1)
            enhance_rate = ENHANCE_RATES.get(eq.enhance_level, 0.5)
        return {
            "id": eq.id,
            "name": defn.name if defn else "未知",
            "slot": eq.slot,
            "quality": eq.quality,
            "quality_name": EquipQuality.NAMES.get(eq.quality, "未知"),
            "enhance_max": max_level,
            "level_required": defn.level_required if defn else 1,
            "sell_price": self._calc_sell_price(eq, defn),
            "is_equipped": eq.is_equipped,
            "enhance_level": eq.enhance_level,
            "base_stats": base_stats,
            "enhance_stats": enhance_stats,
            "stats": stats,
            "enhance_preview": enhance_preview,
            "enhance_rate": enhance_rate,
            "affixes": [self._format_affix(a) for a in affixes],
        }

    def _base_stats(self, eq, defn) -> dict:
        """读取装备基础属性"""
        if not defn:
            return {key: 0 for key in BASE_STAT_KEYS}
        return {
            "attack": defn.base_attack or 0,
            "defense": defn.base_defense or 0,
            "magic_attack": defn.base_magic_attack or 0,
            "magic_defense": defn.base_magic_defense or 0,
            "hp": defn.base_hp or 0,
            "mp": defn.base_mp or 0,
            "speed": defn.base_speed or 0,
        }

    def _enhance_stats(self, eq, defn) -> dict:
        """读取装备强化累计属性"""
        return {
            "attack": eq.enhance_attack or 0,
            "defense": eq.enhance_defense or 0,
            "magic_attack": eq.enhance_magic_attack or 0,
            "magic_defense": eq.enhance_magic_defense or 0,
            "hp": eq.enhance_hp or 0,
            "mp": eq.enhance_mp or 0,
            "speed": eq.enhance_speed or 0,
        }

    def _calc_stats_at_level(self, eq, defn, level: int) -> dict:
        """按强化等级计算强化后的总属性"""
        base = self._base_stats(eq, defn)
        level_required = defn.level_required if defn else 1
        enhance = calc_enhance_stats(base, level_required, eq.quality, level)
        return {key: base[key] + enhance[key] for key in BASE_STAT_KEYS}

    def _format_affix(self, affix) -> dict:
        """格式化附加属性"""
        return {
            "type": affix.affix_type,
            "name": AFFIX_TYPES.get(affix.affix_type, "未知"),
            "value": affix.value,
            "sort_order": affix.sort_order,
        }

    def equip(self, player_id: int, equip_id: int) -> bool:
        """穿戴装备，同部位自动卸下"""
        eq = self.repo.get_by_id(equip_id)
        if not eq or eq.player_id != player_id:
            raise GameException(ErrorCode.EQUIP_NOT_FOUND)
        old_equipped = self.repo.db.query(PlayerEquipment).filter(
            PlayerEquipment.player_id == player_id,
            PlayerEquipment.slot == eq.slot,
            PlayerEquipment.is_equipped == 1,
            PlayerEquipment.id != equip_id,
        ).all()
        for old in old_equipped:
            old.is_equipped = 0
        eq.is_equipped = 1
        self._clamp_stamina(player_id)
        self.repo.db.commit()
        TaskService(self.repo.db).check_progress(player_id, "equip_item", 1)
        return True

    def unequip(self, player_id: int, equip_id: int) -> bool:
        """卸下装备，并钳制当前体力不超过新上限"""
        eq = self.repo.get_by_id(equip_id)
        if not eq or eq.player_id != player_id:
            raise GameException(ErrorCode.EQUIP_NOT_FOUND)
        eq.is_equipped = 0
        self._clamp_stamina(player_id)
        self.repo.db.commit()
        return True

    def _clamp_stamina(self, player_id: int) -> None:
        """体力上限变化后钳制当前体力"""
        player = self.repo.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return
        max_stamina = self.get_equipped_stamina_max(player)
        if player.stamina > max_stamina:
            player.stamina = max_stamina

    def enhance(self, player_id: int, equip_id: int) -> dict:
        """装备强化：成功 +1，+3 后失败 -1"""
        eq = self.repo.get_by_id(equip_id)
        if not eq or eq.player_id != player_id:
            raise GameException(ErrorCode.EQUIP_NOT_FOUND)
        max_level = ENHANCE_MAX_BY_QUALITY.get(eq.quality, 15)
        if eq.enhance_level >= max_level:
            raise GameException(ErrorCode.EQUIP_MAX_LEVEL, "已达该品质最高强化等级")
        self._consume_stone(player_id)
        rate = ENHANCE_RATES.get(eq.enhance_level, 0.5)
        success = random.random() < rate
        if success:
            eq.enhance_level += 1
        elif eq.enhance_level >= 3:
            eq.enhance_level = max(0, eq.enhance_level - 1)
        defn = self.repo.get_definition(eq.equip_def_id)
        self._recalc_enhance(eq, defn)
        self.repo.db.commit()
        if success:
            TaskService(self.repo.db).check_progress(player_id, "enhance_equip", 1)
        return {"success": success, "new_level": eq.enhance_level}

    def _consume_stone(self, player_id: int) -> None:
        """消耗 1 个强化石"""
        from src.models.shop import PlayerItem
        stone = self.repo.db.query(PlayerItem).filter(
            PlayerItem.player_id == player_id,
            PlayerItem.item_id == 4,
        ).first()
        if not stone or stone.quantity < 1:
            raise GameException(ErrorCode.ITEM_NOT_FOUND, "强化石不足，请到商城购买")
        stone.quantity -= 1

    def _recalc_enhance(self, eq, defn) -> None:
        """按穿戴等级带与品质重算全部强化属性"""
        base = self._base_stats(eq, defn)
        level_required = defn.level_required if defn else 1
        enhance = calc_enhance_stats(base, level_required, eq.quality, eq.enhance_level)
        eq.enhance_attack = enhance["attack"]
        eq.enhance_defense = enhance["defense"]
        eq.enhance_magic_attack = enhance["magic_attack"]
        eq.enhance_magic_defense = enhance["magic_defense"]
        eq.enhance_hp = enhance["hp"]
        eq.enhance_mp = enhance["mp"]
        eq.enhance_speed = enhance["speed"]

    def sell(self, player_id: int, equip_id: int) -> dict:
        """出售装备（获得金币）"""
        eq = self.repo.get_by_id(equip_id)
        if not eq or eq.player_id != player_id:
            raise GameException(ErrorCode.EQUIP_NOT_FOUND)
        if eq.is_equipped:
            raise GameException(ErrorCode.PARAM_INVALID, "请先卸下装备再出售")
        player = self.repo.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        defn = self.repo.get_definition(eq.equip_def_id)
        price = self._calc_sell_price(eq, defn)
        player.gold += price
        self.repo.db.delete(eq)
        self.repo.db.commit()
        return {"gold_gained": price, "total_gold": player.gold}

    def _calc_sell_price(self, eq, defn) -> int:
        """按装备等级、品质和强化等级计算出售价"""
        base = defn.sell_price if defn and defn.sell_price > 0 else (
            (defn.level_required if defn else 1) * 10
        )
        quality_bonus = max(0, eq.quality - 1) * 20
        enhance_bonus = eq.enhance_level * 50
        return base + quality_bonus + enhance_bonus

    def get_catalog(self) -> dict:
        """获取装备图鉴（含基础属性与附加属性值域）"""
        defs = self.repo.get_all_definitions()
        groups = []
        for quality in range(1, 7):
            items = []
            for d in defs:
                if d.quality != quality:
                    continue
                items.append(self._catalog_item(d))
            groups.append({
                "quality": quality,
                "quality_name": EquipQuality.NAMES.get(quality, "未知"),
                "enhance_max": ENHANCE_MAX_BY_QUALITY.get(quality, 15),
                "affix_count": AFFIX_COUNT_BY_QUALITY.get(quality, 1),
                "affix_ranges": self._format_affix_ranges(quality),
                "items": items,
            })
        return {"groups": groups}

    def _catalog_item(self, d) -> dict:
        """组装图鉴装备项"""
        base_stats = {
            "attack": d.base_attack or 0,
            "defense": d.base_defense or 0,
            "magic_attack": d.base_magic_attack or 0,
            "magic_defense": d.base_magic_defense or 0,
            "hp": d.base_hp or 0,
            "mp": d.base_mp or 0,
            "speed": d.base_speed or 0,
        }
        return {
            "name": d.name,
            "slot": d.slot,
            "level_required": d.level_required,
            "base_stats": base_stats,
            "base_attack": base_stats["attack"],
            "base_defense": base_stats["defense"],
            "base_magic_attack": base_stats["magic_attack"],
            "base_magic_defense": base_stats["magic_defense"],
            "base_hp": base_stats["hp"],
            "base_mp": base_stats["mp"],
            "base_speed": base_stats["speed"],
        }

    def _format_affix_ranges(self, quality: int) -> list:
        """格式化附加属性值域"""
        ranges = AFFIX_VALUE_RANGE.get(quality, {})
        return [
            {
                "type": affix_type,
                "name": AFFIX_TYPES.get(affix_type, "未知"),
                "min_value": vmin,
                "max_value": vmax,
            }
            for affix_type, (vmin, vmax) in sorted(ranges.items())
        ]

    def get_equipped_bonuses(self, player_id: int) -> dict:
        """汇总已穿戴装备的基础+强化+附加属性加成"""
        equipped = self.repo.get_equipped(player_id)
        affix_map = self.repo.get_affixes_by_equip_ids([eq.id for eq in equipped])
        totals = {key: 0 for key in BASE_STAT_KEYS}
        totals["stamina"] = 0
        for eq in equipped:
            defn = self.repo.get_definition(eq.equip_def_id)
            base = self._base_stats(eq, defn)
            enhance = self._enhance_stats(eq, defn)
            for key in BASE_STAT_KEYS:
                totals[key] += base[key] + enhance[key]
            for affix in affix_map.get(eq.id, []):
                stat_key = AFFIX_STAT_KEYS.get(affix.affix_type)
                if stat_key:
                    totals[stat_key] += affix.value
        return totals

    def get_equipped_stamina_max(self, player) -> int:
        """计算角色当前体力上限（等级基础 + 已穿戴体力附加）"""
        bonuses = self.get_equipped_bonuses(player.id)
        return get_base_max_stamina(player.level) + bonuses.get("stamina", 0)

    def generate_affixes_for_equipment(self, eq) -> None:
        """为装备实例生成附加属性（已存在则跳过）"""
        if self.repo.has_affixes(eq.id):
            return
        affixes = generate_affixes(eq.quality, eq.slot)
        self.repo.add_affixes(eq.id, affixes)
        self.repo.db.commit()
