"""经脉数据访问"""
from src.models.meridian import MeridianDefinition, MeridianAcupoint, PlayerMeridian


class MeridianRepository:
    def __init__(self, db):
        self.db = db

    def get_all_meridians(self):
        return self.db.query(MeridianDefinition).order_by(MeridianDefinition.id).all()

    def get_acupoints(self, meridian_id: int):
        return self.db.query(MeridianAcupoint).filter(
            MeridianAcupoint.meridian_id == meridian_id
        ).order_by(MeridianAcupoint.position).all()

    def get_player_meridian(self, player_id: int, meridian_id: int):
        return self.db.query(PlayerMeridian).filter(
            PlayerMeridian.player_id == player_id,
            PlayerMeridian.meridian_id == meridian_id
        ).first()

    def get_all_player_meridians(self, player_id: int):
        return self.db.query(PlayerMeridian).filter(
            PlayerMeridian.player_id == player_id
        ).all()

    def get_meridian_def(self, meridian_id: int):
        return self.db.query(MeridianDefinition).filter(
            MeridianDefinition.id == meridian_id
        ).first()

    def ensure_player_meridian(self, player_id: int, meridian_id: int):
        existing = self.get_player_meridian(player_id, meridian_id)
        if not existing:
            pm = PlayerMeridian(player_id=player_id, meridian_id=meridian_id, current_acupoint=0)
            self.db.add(pm)
            self.db.commit()
            return pm
        return existing
