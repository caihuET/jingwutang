"""帮派数据访问"""
from src.models.social import Guild, GuildMember, GuildApplication


class GuildRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, guild_id: int):
        return self.db.query(Guild).filter(Guild.id == guild_id).first()

    def get_by_name(self, name: str):
        return self.db.query(Guild).filter(Guild.name == name).first()

    def get_all_guilds(self):
        return self.db.query(Guild).order_by(Guild.id).all()

    def get_member(self, guild_id: int, player_id: int):
        return self.db.query(GuildMember).filter(
            GuildMember.guild_id == guild_id,
            GuildMember.player_id == player_id,
        ).first()

    def get_player_member(self, player_id: int):
        return self.db.query(GuildMember).filter(
            GuildMember.player_id == player_id
        ).first()

    def get_guild_members(self, guild_id: int):
        return self.db.query(GuildMember).filter(
            GuildMember.guild_id == guild_id
        ).all()

    def get_applications(self, guild_id: int, status: int = None):
        query = self.db.query(GuildApplication).filter(
            GuildApplication.guild_id == guild_id
        )
        if status is not None:
            query = query.filter(GuildApplication.status == status)
        return query.order_by(GuildApplication.id.desc()).all()

    def get_application(self, application_id: int):
        return self.db.query(GuildApplication).filter(
            GuildApplication.id == application_id
        ).first()

    def get_pending_application(self, guild_id: int, player_id: int):
        return self.db.query(GuildApplication).filter(
            GuildApplication.guild_id == guild_id,
            GuildApplication.player_id == player_id,
            GuildApplication.status == 0,
        ).first()
