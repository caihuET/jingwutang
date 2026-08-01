"""帮派服务"""
from src.repository.guild_repo import GuildRepository
from src.repository.player_repo import PlayerRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.utils.constants import GuildApplicationStatus
from src.models.social import Guild, GuildMember, GuildApplication


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

    def join(self, player_id: int, guild_id: int) -> dict:
        """申请加入帮派，等待帮主审核"""
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        if player.guild_id:
            raise GameException(ErrorCode.PARAM_INVALID, "已加入帮派")
        guild = self.repo.get_by_id(guild_id)
        if not guild:
            raise GameException(ErrorCode.PARAM_INVALID, "帮派不存在")
        if self.repo.get_pending_application(guild_id, player_id):
            raise GameException(ErrorCode.PARAM_INVALID, "已提交申请，等待审核")
        application = GuildApplication(
            guild_id=guild_id, player_id=player_id,
            status=GuildApplicationStatus.PENDING,
        )
        self.repo.db.add(application)
        self.repo.db.commit()
        self.repo.db.refresh(application)
        return {"application_id": application.id}

    def list_applications(self, player_id: int) -> dict:
        """帮主查看待审核的入帮申请"""
        player = self.player_repo.get_by_id(player_id)
        if not player or not player.guild_id:
            raise GameException(ErrorCode.PARAM_INVALID, "尚未加入帮派")
        member = self.repo.get_player_member(player_id)
        if not member or member.role != 1:
            raise GameException(ErrorCode.PARAM_INVALID, "只有帮主可以审核")
        applications = self.repo.get_applications(
            player.guild_id, GuildApplicationStatus.PENDING
        )
        result = []
        for app in applications:
            applicant = self.player_repo.get_by_id(app.player_id)
            result.append({
                "application_id": app.id,
                "player_id": app.player_id,
                "name": applicant.name if applicant else "未知",
                "level": applicant.level if applicant else 0,
                "combat_power": applicant.combat_power if applicant else 0,
                "created_at": app.created_at.strftime("%m-%d %H:%M") if app.created_at else "",
            })
        return {"applications": result}

    def review_application(self, player_id: int,
                           application_id: int, accept: bool) -> bool:
        """帮主同意或拒绝入帮申请"""
        player = self.player_repo.get_by_id(player_id)
        if not player or not player.guild_id:
            raise GameException(ErrorCode.PARAM_INVALID, "尚未加入帮派")
        member = self.repo.get_player_member(player_id)
        if not member or member.role != 1:
            raise GameException(ErrorCode.PARAM_INVALID, "只有帮主可以审核")
        application = self.repo.get_application(application_id)
        if not application or application.guild_id != player.guild_id:
            raise GameException(ErrorCode.PARAM_INVALID, "申请不存在")
        if application.status != GuildApplicationStatus.PENDING:
            raise GameException(ErrorCode.PARAM_INVALID, "该申请已处理")
        if accept:
            applicant = self.player_repo.get_by_id(application.player_id)
            if not applicant:
                raise GameException(ErrorCode.PARAM_INVALID, "申请人不存在")
            if applicant.guild_id:
                application.status = GuildApplicationStatus.REJECTED
            else:
                self.repo.db.add(GuildMember(
                    guild_id=application.guild_id,
                    player_id=application.player_id, role=5,
                ))
                applicant.guild_id = application.guild_id
                application.status = GuildApplicationStatus.ACCEPTED
        else:
            application.status = GuildApplicationStatus.REJECTED
        self.repo.db.commit()
        if accept:
            from src.service.task_service import TaskService
            TaskService(self.repo.db).check_progress(application.player_id, "join_guild", 1)
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
