"""社交数据访问"""
from src.models.social import FriendRelation, ChatMessage


class SocialRepository:
    def __init__(self, db):
        self.db = db

    def get_relation(self, player_id: int, friend_id: int):
        return self.db.query(FriendRelation).filter(
            FriendRelation.player_id == player_id,
            FriendRelation.friend_id == friend_id,
        ).first()

    def get_relations(self, player_id: int, status: int = None):
        query = self.db.query(FriendRelation).filter(
            (FriendRelation.player_id == player_id) |
            (FriendRelation.friend_id == player_id)
        )
        if status is not None:
            query = query.filter(FriendRelation.status == status)
        return query.all()

    def get_sent_requests(self, player_id: int) -> list:
        return self.db.query(FriendRelation).filter(
            FriendRelation.player_id == player_id
        ).order_by(FriendRelation.id.desc()).all()

    def get_messages(self, channel: int, guild_id: int = None,
                     receiver_id: int = None, player_id: int = None,
                     before_id: int = None, limit: int = 20):
        query = self.db.query(ChatMessage).filter(
            ChatMessage.channel == channel
        )
        if channel == 2 and guild_id is not None:
            query = query.filter(ChatMessage.guild_id == guild_id)
        if channel == 3 and player_id is not None:
            if receiver_id is not None:
                query = query.filter(
                    ((ChatMessage.sender_id == player_id) &
                     (ChatMessage.receiver_id == receiver_id)) |
                    ((ChatMessage.sender_id == receiver_id) &
                     (ChatMessage.receiver_id == player_id))
                )
            else:
                query = query.filter(
                    (ChatMessage.sender_id == player_id) |
                    (ChatMessage.receiver_id == player_id)
                )
        if before_id is not None:
            query = query.filter(ChatMessage.id < before_id)
        return query.order_by(ChatMessage.id.desc()).limit(limit).all()
