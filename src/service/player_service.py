"""角色服务"""
from src.utils.validators import validate_nickname, check_sensitive_words
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.repository.player_repo import PlayerRepository


class PlayerService:
    """角色业务"""

    def __init__(self, db):
        self.repo = PlayerRepository(db)

    def get_by_user(self, user_id: int) -> dict:
        """按 user_id 查询角色"""
        player = self.repo.get_by_user_id(user_id)
        if not player:
            return None
        return {"player_id": player.id, "name": player.name, "level": player.level}

    def create(self, user_id: int, name: str, gender: int, school_id: int) -> dict:
        """创建角色"""
        if not validate_nickname(name):
            raise GameException(ErrorCode.PARAM_INVALID, "昵称格式不正确")
        if not check_sensitive_words(name):
            raise GameException(ErrorCode.NICKNAME_SENSITIVE, "昵称包含敏感词")
        if self.repo.get_by_name(name):
            raise GameException(ErrorCode.NICKNAME_EXISTS, "昵称已存在")
        player = self.repo.create(user_id, name, gender, school_id)
        return {"player_id": player.id}

    def get_info(self, player_id: int) -> dict:
        """获取角色信息"""
        player = self.repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        return {
            "name": player.name,
            "level": player.level,
            "exp": player.exp,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "mp": player.mp,
            "max_mp": player.max_mp,
            "stamina": player.stamina,
            "gold": player.gold,
            "ingot": player.ingot,
            "reputation": player.reputation,
            "combat_power": player.combat_power,
        }
