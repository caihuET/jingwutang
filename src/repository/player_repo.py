"""角色数据访问"""
from src.models.player import Player


class PlayerRepository:
    """角色表操作"""

    def __init__(self, db):
        self.db = db

    def get_by_id(self, player_id: int) -> Player:
        return self.db.query(Player).filter(Player.id == player_id).first()

    def get_by_name(self, name: str) -> Player:
        return self.db.query(Player).filter(Player.name == name).first()

    def get_by_user_id(self, user_id: int) -> Player:
        return self.db.query(Player).filter(Player.user_id == user_id).first()

    def create(self, user_id: int, name: str, gender: int, school_id: int) -> Player:
        player = Player(
            user_id=user_id, name=name, gender=gender, school_id=school_id,
            hp=100, max_hp=100, mp=50, max_mp=50, stamina=100,
        )
        self.db.add(player)
        self.db.commit()
        self.db.refresh(player)
        return player
