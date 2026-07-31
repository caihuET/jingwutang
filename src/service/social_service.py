"""社交服务（好友 + 聊天）"""
import random
from datetime import datetime
from src.repository.social_repo import SocialRepository
from src.repository.player_repo import PlayerRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.models.social import FriendRelation, ChatMessage


class SocialService:
    def __init__(self, db):
        self.repo = SocialRepository(db)
        self.player_repo = PlayerRepository(db)

    def get_friends(self, player_id: int) -> dict:
        relations = self.repo.get_relations(player_id, status=1)
        friends = []
        for rel in relations:
            other_id = rel.friend_id if rel.player_id == player_id else rel.player_id
            friend = self.player_repo.get_by_id(other_id)
            if friend:
                friends.append(self._player_brief(friend))
        return {"friends": friends}

    def get_requests(self, player_id: int) -> dict:
        relations = self.repo.get_relations(player_id, status=0)
        requests = []
        for rel in relations:
            if rel.friend_id != player_id:
                continue
            applicant = self.player_repo.get_by_id(rel.player_id)
            if applicant:
                requests.append(self._player_brief(applicant))
        return {"requests": requests}

    def add_friend(self, player_id: int, player_name: str) -> bool:
        target = self.player_repo.get_by_name(player_name)
        if not target or target.id == player_id:
            raise GameException(ErrorCode.PARAM_INVALID, "玩家不存在")
        if self._has_relation(player_id, target.id):
            raise GameException(ErrorCode.ALREADY_FRIENDS, "已存在好友关系")
        self.repo.db.add(FriendRelation(
            player_id=player_id, friend_id=target.id, status=0,
        ))
        self.repo.db.add(FriendRelation(
            player_id=target.id, friend_id=player_id, status=0,
        ))
        self.repo.db.commit()
        return True

    def respond_friend(self, player_id: int, applicant_id: int, accept: bool) -> bool:
        rel_a = self.repo.get_relation(applicant_id, player_id)
        rel_b = self.repo.get_relation(player_id, applicant_id)
        if not rel_a or not rel_b or rel_b.status != 0:
            raise GameException(ErrorCode.PARAM_INVALID, "申请不存在")
        if accept:
            rel_a.status = 1
            rel_b.status = 1
        else:
            self.repo.db.delete(rel_a)
            self.repo.db.delete(rel_b)
        self.repo.db.commit()
        return True

    def remove_friend(self, player_id: int, friend_id: int) -> bool:
        rel_a = self.repo.get_relation(player_id, friend_id)
        rel_b = self.repo.get_relation(friend_id, player_id)
        if rel_a:
            self.repo.db.delete(rel_a)
        if rel_b:
            self.repo.db.delete(rel_b)
        self.repo.db.commit()
        return True

    def gift_stamina(self, player_id: int, friend_id: int) -> dict:
        rel = self.repo.get_relation(player_id, friend_id)
        if not rel or rel.status != 1:
            raise GameException(ErrorCode.PARAM_INVALID, "还不是好友")
        today = datetime.utcnow().date()
        if rel.last_gift_at and rel.last_gift_at.date() == today:
            raise GameException(ErrorCode.DAILY_LIMIT, "今日已赠送过体力")
        friend = self.player_repo.get_by_id(friend_id)
        if not friend:
            raise GameException(ErrorCode.PARAM_INVALID, "玩家不存在")
        max_stamina = min(150, 100 + (friend.level // 10) * 5)
        friend.stamina = min(max_stamina, friend.stamina + 10)
        rel.last_gift_at = datetime.utcnow()
        self.repo.db.commit()
        return {"friend_id": friend_id, "gift": 10}

    def spar(self, player_id: int, friend_id: int) -> dict:
        me = self.player_repo.get_by_id(player_id)
        friend = self.player_repo.get_by_id(friend_id)
        if not me or not friend:
            raise GameException(ErrorCode.PARAM_INVALID, "玩家不存在")
        my_power = me.combat_power or me.level * 10
        other_power = friend.combat_power or friend.level * 10
        result = "win" if my_power > other_power else "lose"
        if my_power == other_power:
            result = "win" if random.random() > 0.5 else "lose"
        return {
            "result": result,
            "opponent": friend.name,
            "my_power": my_power,
            "opponent_power": other_power,
        }

    def send_chat(self, player_id: int, channel: int,
                  content: str, receiver_id: int = None) -> dict:
        if not content or len(content) > 200:
            raise GameException(ErrorCode.PARAM_INVALID, "消息内容不合法")
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        guild_id = None
        if channel == 2:
            guild_id = player.guild_id
            if not guild_id:
                raise GameException(ErrorCode.PARAM_INVALID, "请先加入帮派")
        if channel == 3 and not receiver_id:
            raise GameException(ErrorCode.PARAM_INVALID, "私聊需要指定接收人")
        msg = ChatMessage(
            channel=channel, sender_id=player_id,
            receiver_id=receiver_id, content=content, guild_id=guild_id,
        )
        self.repo.db.add(msg)
        self.repo.db.commit()
        self.repo.db.refresh(msg)
        return {
            "id": msg.id,
            "channel": msg.channel,
            "sender_id": msg.sender_id,
            "sender_name": player.name,
            "content": msg.content,
            "receiver_id": receiver_id,
            "guild_id": guild_id,
            "created_at": msg.created_at.strftime("%m-%d %H:%M") if msg.created_at else "",
        }

    def get_messages(self, player_id: int, channel: int,
                     receiver_id: int = None) -> list:
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        rows = self.repo.get_messages(
            channel, guild_id=player.guild_id if channel == 2 else None,
            receiver_id=receiver_id, player_id=player_id,
        )
        result = []
        for msg in reversed(rows):
            sender = self.player_repo.get_by_id(msg.sender_id)
            result.append({
                "id": msg.id,
                "channel": msg.channel,
                "sender_id": msg.sender_id,
                "sender_name": sender.name if sender else "系统",
                "content": msg.content,
                "created_at": msg.created_at.strftime("%m-%d %H:%M") if msg.created_at else "",
            })
        return result

    def _has_relation(self, player_id: int, other_id: int) -> bool:
        rel = self.repo.get_relation(player_id, other_id)
        return rel is not None

    def _player_brief(self, player) -> dict:
        return {
            "player_id": player.id,
            "name": player.name,
            "level": player.level,
            "school_id": player.school_id,
            "combat_power": player.combat_power,
        }
