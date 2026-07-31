"""称号数据访问"""
from src.models.title import PlayerTitle, TitleDefinition


class TitleRepository:
    """称号表操作"""

    def __init__(self, db):
        self.db = db

    def get_player_titles(self, player_id: int) -> list:
        return self.db.query(PlayerTitle).filter(
            PlayerTitle.player_id == player_id
        ).all()

    def get_player_title(self, player_id: int, title_id: int) -> PlayerTitle:
        return self.db.query(PlayerTitle).filter(
            PlayerTitle.player_id == player_id,
            PlayerTitle.title_id == title_id,
        ).first()

    def get_title(self, title_id: int) -> TitleDefinition:
        return self.db.query(TitleDefinition).filter(
            TitleDefinition.id == title_id
        ).first()

    def get_title_by_source(self, source_type: int, source_id: int) -> TitleDefinition:
        return self.db.query(TitleDefinition).filter(
            TitleDefinition.source_type == source_type,
            TitleDefinition.source_id == source_id,
        ).first()
