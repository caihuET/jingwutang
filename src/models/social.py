"""社交与帮派模型"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func
from src.models.database import Base


class FriendRelation(Base):
    """好友关系"""
    __tablename__ = "friend_relationships"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    player_id = Column(BigInteger, nullable=False, index=True)
    friend_id = Column(BigInteger, nullable=False, index=True)
    status = Column(Integer, default=0)
    last_gift_at = Column(DateTime(6), nullable=True)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)


class ChatMessage(Base):
    """聊天消息"""
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    channel = Column(Integer, nullable=False)
    sender_id = Column(BigInteger, nullable=False)
    receiver_id = Column(BigInteger, nullable=True)
    guild_id = Column(Integer, nullable=True)
    content = Column(String(256), nullable=False)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)


class Guild(Base):
    """帮派"""
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)
    leader_id = Column(BigInteger, nullable=False)
    level = Column(Integer, default=1)
    exp = Column(BigInteger, default=0)
    announcement = Column(String(256), default="")
    created_at = Column(DateTime(6), default=func.now(), nullable=False)


class GuildMember(Base):
    """帮派成员"""
    __tablename__ = "guild_members"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(Integer, nullable=False, index=True)
    player_id = Column(BigInteger, nullable=False, index=True)
    role = Column(Integer, default=5)
    contribution = Column(Integer, default=0)
    joined_at = Column(DateTime(6), default=func.now(), nullable=False)


class GuildApplication(Base):
    """帮派入帮申请"""
    __tablename__ = "guild_applications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(Integer, nullable=False, index=True)
    player_id = Column(BigInteger, nullable=False, index=True)
    status = Column(Integer, default=0)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)
