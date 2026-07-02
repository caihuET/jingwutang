"""角色服务"""
from src.utils.validators import validate_nickname, check_sensitive_words
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.utils.constants import SchoolType, EXP_TABLE
from src.repository.player_repo import PlayerRepository
from datetime import datetime


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
        existing = self.repo.get_by_user_id(user_id)
        if existing:
            return {"player_id": existing.id}
        player = self.repo.create(user_id, name, gender, school_id)
        return {"player_id": player.id}

    def get_info(self, player_id: int) -> dict:
        """获取角色信息"""
        player = self.repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        self._apply_stamina_recovery(player)
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
            "school_name": SchoolType.NAMES.get(player.school_id, "未知"),
            "exp_needed": EXP_TABLE[player.level] if player.level < 100 else 0,
            "exp_progress": round(player.exp / EXP_TABLE[player.level] * 100, 1) if player.level < 100 and EXP_TABLE[player.level] > 0 else 0,
            "max_stamina": self._get_max_stamina(player.level),
        }

    def _get_max_stamina(self, level: int) -> int:
        return min(150, 100 + (level // 10) * 5)

    def _apply_stamina_recovery(self, player):
        """离线体力恢复 (每 5 分钟 1 点)"""
        now = datetime.utcnow()
        elapsed = max(0, int((now - player.updated_at).total_seconds()))
        recovered = int(elapsed / 300)
        if recovered > 0:
            max_sta = self._get_max_stamina(player.level)
            player.stamina = min(max_sta, player.stamina + recovered)
            self.repo.db.commit()

    def buy_stamina(self, player_id: int) -> dict:
        """购买体力"""
        player = self.repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        if player.daily_stamina_bought >= 3:
            raise GameException(ErrorCode.DAILY_LIMIT, "今日购买次数已用完")
        prices = [50, 100, 150]
        cost = prices[player.daily_stamina_bought]
        if player.ingot < cost:
            raise GameException(ErrorCode.INGOT_NOT_ENOUGH, "元宝不足")
        player.ingot -= cost
        player.stamina = min(self._get_max_stamina(player.level), player.stamina + 60)
        player.daily_stamina_bought += 1
        self.repo.db.commit()
        return {
            "stamina": player.stamina,
            "max_stamina": self._get_max_stamina(player.level),
            "ingot": player.ingot,
            "bought_today": player.daily_stamina_bought,
            "cost": cost,
        }
