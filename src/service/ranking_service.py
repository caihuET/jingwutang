"""排行服务"""
from src.models.player import Player
from src.service.player_service import PlayerService
from src.utils.constants import SchoolType


class RankingService:
    """等级与战力排行"""

    def __init__(self, db):
        self.db = db
        self.player_service = PlayerService(db)

    def get_ranking(self, kind: str, player_id: int,
                    page: int = 1, size: int = 20) -> dict:
        """获取指定类型排行，kind 支持 level / combat"""
        players = self._load_players(kind)
        total = len(players)
        start = (page - 1) * size
        end = start + size
        result = []
        for rank, player in enumerate(players[start:end], start=start + 1):
            result.append(self._brief(player, rank))
        my_rank = next(
            (rank for rank, player in enumerate(players, 1)
             if player.id == player_id), 0
        )
        return {"list": result, "total": total, "my_rank": my_rank}

    def get_marquee(self) -> dict:
        """获取等级排行 Top10 跑马灯数据"""
        players = self._load_players("level")[:10]
        return {
            "list": [
                self._brief(player, rank)
                for rank, player in enumerate(players, 1)
            ]
        }

    def _load_players(self, kind: str):
        players = self.db.query(Player).all()
        power_map = {
            player.id: self.player_service.get_combat_power(player)
            for player in players
        }
        if kind == "combat":
            players = sorted(
                players,
                key=lambda p: (power_map[p.id], p.level),
                reverse=True,
            )
        else:
            players = sorted(
                players,
                key=lambda p: (p.level, power_map[p.id]),
                reverse=True,
            )
        return players

    def _brief(self, player, rank: int) -> dict:
        combat_power = self.player_service.get_combat_power(player)
        return {
            "rank": rank,
            "player_id": player.id,
            "name": player.name,
            "level": player.level,
            "school": SchoolType.NAMES.get(player.school_id, "未知"),
            "combat_power": combat_power,
        }
