"""帮派服务"""
from src.repository.guild_repo import GuildRepository
from src.repository.player_repo import PlayerRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.models.social import Guild, GuildMember


class GuildService:
    def __init__(self, db):
        self.repo = GuildRepository(db)
        self.player_repo = PlayerRepository(db)

    def list_guilds(self) -> list:
        guilds = self.repo.get_all_guilds()
        result = []
        for guild in guilds:
            members = self.repo.get_guild_members(guild.id)
            result.append({
                "guild_id": guild.id,
                "name": guild.name,
                "level": guild.level,
                "member_count": len(members),
                "announcement": guild.announcement,
            })
        return result

    def get_info(self, player_id: int) -> dict:
        player = self.player_repo.get_by_id(player_id)
        if not player or not player.guild_id:
            raise GameException(ErrorCode.PARAM_INVALID, "尚未加入帮派")
        guild = self.repo.get_by_id(player.guild_id)
        if not guild:
            raise GameException(ErrorCode.PARAM_INVALID, "帮派不存在")
        members = []
        for m in self.repo.get_guild_members(guild.id):
            p = self.player_repo.get_by_id(m.player_id)
            members.append({
                "player_id": m.player_id,
                "name": p.name if p else "未知",
                "level": p.level if p else 0,
                "role": m.role,
                "contribution": m.contribution,
            })
        return {
            "guild_id": guild.id,
            "name": guild.name,
            "level": guild.level,
            "announcement": guild.announcement,
            "leader_id": guild.leader_id,
            "members": members,
        }

    def create(self, player_id: int, name: str, announcement: str = "") -> dict:
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        if player.guild_id:
            raise GameException(ErrorCode.PARAM_INVALID, "已加入帮派")
        if not name or len(name) > 16:
            raise GameException(ErrorCode.PARAM_INVALID, "帮派名称不合法")
        if self.repo.get_by_name(name):
            raise GameException(ErrorCode.PARAM_INVALID, "帮派名称已存在")
        if player.gold < 5000:
            raise GameException(ErrorCode.GOLD_NOT_ENOUGH, "创建帮派需要 5000 金币")
        player.gold -= 5000
        guild = Guild(name=name, leader_id=player_id, announcement=announcement or "欢迎加入本帮")
        self.repo.db.add(guild)
        self.repo.db.flush()
        self.repo.db.add(GuildMember(
            guild_id=guild.id, player_id=player_id, role=1,
        ))
        player.guild_id = guild.id
        self.repo.db.commit()
        return {"guild_id": guild.id, "name": guild.name}

    def join(self, player_id: int, guild_id: int) -> bool:
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        if player.guild_id:
            raise GameException(ErrorCode.PARAM_INVALID, "已加入帮派")
        guild = self.repo.get_by_id(guild_id)
        if not guild:
            raise GameException(ErrorCode.PARAM_INVALID, "帮派不存在")
        self.repo.db.add(GuildMember(
            guild_id=guild_id, player_id=player_id, role=5,
        ))
        player.guild_id = guild_id
        self.repo.db.commit()
        return True

    def leave(self, player_id: int) -> bool:
        player = self.player_repo.get_by_id(player_id)
        if not player or not player.guild_id:
            raise GameException(ErrorCode.PARAM_INVALID, "尚未加入帮派")
        member = self.repo.get_player_member(player_id)
        if member and member.role == 1:
            self._disband(player.guild_id)
        else:
            if member:
                self.repo.db.delete(member)
        player.guild_id = None
        self.repo.db.commit()
        return True

    def update_announcement(self, player_id: int, content: str) -> bool:
        player = self.player_repo.get_by_id(player_id)
        if not player or not player.guild_id:
            raise GameException(ErrorCode.PARAM_INVALID, "尚未加入帮派")
        member = self.repo.get_player_member(player_id)
        if not member or member.role != 1:
            raise GameException(ErrorCode.PARAM_INVALID, "只有帮主可以修改公告")
        guild = self.repo.get_by_id(player.guild_id)
        guild.announcement = content[:256]
        self.repo.db.commit()
        return True

    def _disband(self, guild_id: int):
        for member in self.repo.get_guild_members(guild_id):
            p = self.player_repo.get_by_id(member.player_id)
            if p:
                p.guild_id = None
            self.repo.db.delete(member)
        guild = self.repo.get_by_id(guild_id)
        if guild:
            self.repo.db.delete(guild)
