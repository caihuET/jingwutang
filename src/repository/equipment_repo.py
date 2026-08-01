"""装备数据访问"""
from src.models.equipment import PlayerEquipment, EquipmentDefinition, PlayerEquipmentAffix


class EquipmentRepository:
    def __init__(self, db):
        self.db = db

    def get_player_equipment(self, player_id: int):
        return self.db.query(PlayerEquipment).filter(
            PlayerEquipment.player_id == player_id
        ).all()

    def get_equipped(self, player_id: int):
        return self.db.query(PlayerEquipment).filter(
            PlayerEquipment.player_id == player_id,
            PlayerEquipment.is_equipped == 1
        ).all()

    def get_by_id(self, equip_id: int):
        return self.db.query(PlayerEquipment).filter(
            PlayerEquipment.id == equip_id
        ).first()

    def get_definition(self, def_id: int):
        return self.db.query(EquipmentDefinition).filter(
            EquipmentDefinition.id == def_id
        ).first()

    def get_all_definitions(self):
        return self.db.query(EquipmentDefinition).order_by(
            EquipmentDefinition.quality, EquipmentDefinition.level_required
        ).all()

    def get_affixes(self, equip_id: int) -> list:
        """查询单件装备的附加属性"""
        return self.db.query(PlayerEquipmentAffix).filter(
            PlayerEquipmentAffix.equip_id == equip_id
        ).order_by(PlayerEquipmentAffix.sort_order).all()

    def get_affixes_by_equip_ids(self, equip_ids: list) -> dict:
        """按装备 ID 批量查询附加属性"""
        if not equip_ids:
            return {}
        rows = self.db.query(PlayerEquipmentAffix).filter(
            PlayerEquipmentAffix.equip_id.in_(equip_ids)
        ).order_by(PlayerEquipmentAffix.sort_order).all()
        result = {}
        for row in rows:
            result.setdefault(row.equip_id, []).append(row)
        return result

    def has_affixes(self, equip_id: int) -> bool:
        """判断装备是否已有附加属性"""
        return self.db.query(PlayerEquipmentAffix.id).filter(
            PlayerEquipmentAffix.equip_id == equip_id
        ).first() is not None

    def add_affixes(self, equip_id: int, affixes: list) -> None:
        """批量写入附加属性"""
        for affix in affixes:
            self.db.add(PlayerEquipmentAffix(
                equip_id=equip_id,
                affix_type=affix["affix_type"],
                value=affix["value"],
                sort_order=affix["sort_order"],
            ))
