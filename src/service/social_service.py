"""社交服务（好友 + 聊天）"""
import random
from datetime import datetime
from src.repository.social_repo import SocialRepository
from src.repository.player_repo import PlayerRepository
from src.repository.guild_repo import GuildRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.utils.constants import FriendStatus
from src.utils.validators import check_sensitive_words
from src.utils.redis_client import (
    clear_unread, get_online_ids, get_read_cursor, incr_unread,
    set_read_cursor, check_rate_limit,
)
from src.models.social import FriendRelation, ChatMessage


class SocialService:
    def __init__(self, db):
        self.repo = SocialRepository(db)
        self.player_repo = PlayerRepository(db)
        self.guild_repo = GuildRepository(db)

    def get_friends(self, player_id: int) -> dict:
        relations = self.repo.get_relations(player_id, status=FriendStatus.ACCEPTED)
        friends = []
        seen = set()
        for rel in relations:
            other_id = rel.friend_id if rel.player_id == player_id else rel.player_id
            if other_id in seen:
                continue
            seen.add(other_id)
            friend = self.player_repo.get_by_id(other_id)
            if friend:
                friends.append(self._player_brief(friend))
        return {"friends": friends}

    def get_requests(self, player_id: int) -> dict:
        relations = self.repo.get_relations(player_id, status=FriendStatus.PENDING)
        requests = []
        for rel in relations:
            if rel.friend_id != player_id:
                continue
            applicant = self.player_repo.get_by_id(rel.player_id)
            if applicant:
                requests.append(self._player_brief(applicant))
        return {"requests": requests}

    def add_friend(self, player_id: int, player_name: str) -> dict:
        target = self.player_repo.get_by_name(player_name)
        if not target or target.id == player_id:
            raise GameException(ErrorCode.PARAM_INVALID, "玩家不存在")
        if self._active_relation(player_id, target.id):
            raise GameException(ErrorCode.ALREADY_FRIENDS, "已存在好友关系")
        rel = self.repo.get_relation(player_id, target.id)
        if rel and rel.status in (FriendStatus.REJECTED, FriendStatus.REMOVED):
            rel.status = FriendStatus.PENDING
        else:
            self.repo.db.add(FriendRelation(
                player_id=player_id, friend_id=target.id,
                status=FriendStatus.PENDING,
            ))
        self.repo.db.commit()
        applicant = self.player_repo.get_by_id(player_id)
        return {
            "target_id": target.id,
            "name": applicant.name if applicant else "",
        }

    def respond_friend(self, player_id: int, applicant_id: int, accept: bool) -> dict:
        rel = self.repo.get_relation(applicant_id, player_id)
        if not rel or rel.status != FriendStatus.PENDING:
            raise GameException(ErrorCode.PARAM_INVALID, "申请不存在")
        if accept:
            rel.status = FriendStatus.ACCEPTED
            reverse = self.repo.get_relation(player_id, applicant_id)
            if reverse:
                reverse.status = FriendStatus.ACCEPTED
            else:
                self.repo.db.add(FriendRelation(
                    player_id=player_id, friend_id=applicant_id,
                    status=FriendStatus.ACCEPTED,
                ))
        else:
            rel.status = FriendStatus.REJECTED
        self.repo.db.commit()
        responder = self.player_repo.get_by_id(player_id)
        return {
            "name": responder.name if responder else "",
        }

    def remove_friend(self, player_id: int, friend_id: int) -> bool:
        rel_a = self.repo.get_relation(player_id, friend_id)
        rel_b = self.repo.get_relation(friend_id, player_id)
        if rel_a:
            rel_a.status = FriendStatus.REMOVED
        if rel_b:
            self.repo.db.delete(rel_b)
        self.repo.db.commit()
        return True

    def get_request_history(self, player_id: int) -> dict:
        """获取我发出的好友申请历史"""
        result = []
        for rel in self.repo.get_sent_requests(player_id):
            target = self.player_repo.get_by_id(rel.friend_id)
            result.append({
                "player_id": rel.friend_id,
                "name": target.name if target else "未知",
                "level": target.level if target else 0,
                "status": rel.status,
                "status_name": FriendStatus.NAMES.get(rel.status, "未知"),
            })
        return {"requests": result}

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
                  content: str, receiver_id: int = None,
                  receiver_name: str = None) -> dict:
        if not content or len(content) > 200:
            raise GameException(ErrorCode.PARAM_INVALID, "消息内容不合法")
        if not check_sensitive_words(content):
            raise GameException(ErrorCode.PARAM_INVALID, "消息包含敏感词")
        if not check_rate_limit(player_id):
            raise GameException(ErrorCode.RATE_LIMITED, "发言太快，请稍后再试")
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        guild_id = None
        if channel == 2:
            guild_id = player.guild_id
            if not guild_id:
                raise GameException(ErrorCode.PARAM_INVALID, "请先加入帮派")
        if channel == 3:
            if not receiver_id and receiver_name:
                target = self.player_repo.get_by_name(receiver_name.strip())
                receiver_id = target.id if target else None
            if not receiver_id:
                raise GameException(ErrorCode.PARAM_INVALID, "未找到好友")
            if not self._is_friend(player_id, receiver_id):
                raise GameException(ErrorCode.PARAM_INVALID, "只能给好友发送私聊")
        msg = ChatMessage(
            channel=channel, sender_id=player_id,
            receiver_id=receiver_id, content=content, guild_id=guild_id,
        )
        self.repo.db.add(msg)
        self.repo.db.commit()
        self.repo.db.refresh(msg)
        self._increase_unread(player_id, channel, guild_id, receiver_id)
        receiver = self.player_repo.get_by_id(receiver_id) if receiver_id else None
        return {
            "id": msg.id,
            "channel": msg.channel,
            "sender_id": msg.sender_id,
            "sender_name": player.name,
            "receiver_id": receiver_id,
            "receiver_name": receiver.name if receiver else "",
            "content": msg.content,
            "guild_id": guild_id,
            "created_at": msg.created_at.strftime("%m-%d %H:%M") if msg.created_at else "",
            "read": False,
        }

    def get_messages(self, player_id: int, channel: int,
                     receiver_id: int = None, before_id: int = None,
                     limit: int = 20) -> dict:
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        rows = self.repo.get_messages(
            channel, guild_id=player.guild_id if channel == 2 else None,
            receiver_id=receiver_id, player_id=player_id,
            before_id=before_id, limit=limit + 1,
        )
        has_more = len(rows) > limit
        rows = rows[:limit]
        self._mark_read(player_id, channel, receiver_id, rows)
        result = []
        for msg in reversed(rows):
            sender = self.player_repo.get_by_id(msg.sender_id)
            receiver = self.player_repo.get_by_id(msg.receiver_id) if msg.receiver_id else None
            result.append({
                "id": msg.id,
                "channel": msg.channel,
                "sender_id": msg.sender_id,
                "sender_name": sender.name if sender else "系统",
                "receiver_id": msg.receiver_id,
                "receiver_name": receiver.name if receiver else "",
                "content": msg.content,
                "created_at": msg.created_at.strftime("%m-%d %H:%M") if msg.created_at else "",
                "read": self._is_read(player_id, channel, msg),
            })
        return {"messages": result, "has_more": has_more}

    def _is_friend(self, player_id: int, friend_id: int) -> bool:
        """判断两人是否为好友"""
        rel_a = self.repo.get_relation(player_id, friend_id)
        rel_b = self.repo.get_relation(friend_id, player_id)
        return (rel_a is not None and rel_a.status == FriendStatus.ACCEPTED) or \
               (rel_b is not None and rel_b.status == FriendStatus.ACCEPTED)

    def _increase_unread(self, sender_id: int, channel: int,
                         guild_id: int, receiver_id: int = None):
        """发送后按频道累计未读"""
        if channel == 3 and receiver_id:
            incr_unread(receiver_id, "p:{}".format(sender_id))
            return
        if channel == 1:
            for player_id in get_online_ids():
                if player_id != sender_id:
                    incr_unread(player_id, "1")
            return
        if channel == 2 and guild_id:
            for member in self.guild_repo.get_guild_members(guild_id):
                if member.player_id != sender_id:
                    incr_unread(member.player_id, "2")

    def _mark_read(self, player_id: int, channel: int,
                   receiver_id: int, rows: list):
        """读取消息后清除未读并推进已读游标"""
        if channel == 1:
            clear_unread(player_id, "1")
            return
        if channel == 2:
            clear_unread(player_id, "2")
            return
        if channel != 3:
            return
        if receiver_id:
            clear_unread(player_id, "p:{}".format(receiver_id))
            last_id = max((m.id for m in rows if m.sender_id == receiver_id), default=0)
            if last_id:
                set_read_cursor(player_id, receiver_id, last_id)
            return
        clear_unread(player_id)
        for msg in rows:
            if msg.sender_id != player_id:
                set_read_cursor(player_id, msg.sender_id, msg.id)

    def _is_read(self, player_id: int, channel: int, msg) -> bool:
        """私聊中自己发送的消息是否已被对方阅读"""
        if channel != 3 or msg.sender_id != player_id or not msg.receiver_id:
            return False
        cursor = get_read_cursor(msg.receiver_id, player_id)
        return msg.id <= cursor

    def _active_relation(self, player_id: int, other_id: int) -> bool:
        rel_a = self.repo.get_relation(player_id, other_id)
        rel_b = self.repo.get_relation(other_id, player_id)
        active = (FriendStatus.PENDING, FriendStatus.ACCEPTED)
        return (rel_a is not None and rel_a.status in active) or \
               (rel_b is not None and rel_b.status in active)

    def _player_brief(self, player) -> dict:
        return {
            "player_id": player.id,
            "name": player.name,
            "level": player.level,
            "school_id": player.school_id,
            "combat_power": player.combat_power,
        }
