"""装备数据访问"""
from src.models.equipment import PlayerEquipment, EquipmentDefinition


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
