"""称号服务"""
from src.repository.title_repo import TitleRepository
from src.models.title import PlayerTitle
from src.models.player import Player
from src.utils.errors import GameException
from src.utils.constants import ErrorCode


class TitleService:
    """称号业务"""

    def __init__(self, db):
        self.db = db
        self.repo = TitleRepository(db)

    def get_titles(self, player_id: int) -> list:
        """获取角色已获得称号"""
        result = []
        for pt in self.repo.get_player_titles(player_id):
            td = self.repo.get_title(pt.title_id)
            result.append({
                "title_id": pt.title_id,
                "name": td.name if td else "未知称号",
                "title_level": td.title_level if td else 1,
                "display_effect": td.display_effect if td else "none",
                "source_type": td.source_type if td else 0,
                "is_equipped": pt.is_equipped,
                "obtained_at": pt.obtained_at.isoformat() if pt.obtained_at else None,
            })
        return result

    def equip(self, player_id: int, title_id: int) -> dict:
        """佩戴称号"""
        pt = self.repo.get_player_title(player_id, title_id)
        if not pt:
            raise GameException(ErrorCode.PARAM_INVALID, "尚未获得该称号")
        td = self.repo.get_title(title_id)
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        self.db.query(PlayerTitle).filter(
            PlayerTitle.player_id == player_id
        ).update({"is_equipped": 0}, synchronize_session=False)
        pt.is_equipped = 1
        player.equipped_title_id = title_id
        player.title = td.name if td else player.title
        self.db.commit()
        return {"title_id": title_id, "name": td.name if td else "未知称号"}

    def unequip(self, player_id: int, title_id: int) -> dict:
        """卸下称号"""
        pt = self.repo.get_player_title(player_id, title_id)
        if not pt:
            raise GameException(ErrorCode.PARAM_INVALID, "尚未获得该称号")
        if pt.is_equipped:
            player = self.db.query(Player).filter(Player.id == player_id).first()
            if player:
                player.equipped_title_id = None
                player.title = None
        pt.is_equipped = 0
        self.db.commit()
        return {"title_id": title_id}

    def grant_shop_title(self, player_id: int, item_id: int) -> bool:
        """商城称号道具使用后发放并自动佩戴"""
        td = self.repo.get_title_by_source(1, item_id)
        if not td:
            return False
        return self.grant(player_id, td.id, auto_equip=True)

    def grant(self, player_id: int, title_id: int, auto_equip: bool = False) -> bool:
        """发放称号，由调用方统一提交事务"""
        td = self.repo.get_title(title_id)
        if not td:
            return False
        pt = self.repo.get_player_title(player_id, title_id)
        if not pt:
            pt = PlayerTitle(player_id=player_id, title_id=title_id, is_equipped=0)
            self.db.add(pt)
        if auto_equip:
            self._set_equipped(player_id, title_id, td.name)
        return True

    def _set_equipped(self, player_id: int, title_id: int, title_name: str):
        """将指定称号设为当前佩戴，不主动提交"""
        self.db.query(PlayerTitle).filter(
            PlayerTitle.player_id == player_id
        ).update({"is_equipped": 0}, synchronize_session=False)
        pt = self.repo.get_player_title(player_id, title_id)
        if pt:
            pt.is_equipped = 1
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if player:
            player.equipped_title_id = title_id
            player.title = title_name
