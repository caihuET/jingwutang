"""Redis 工具：聊天未读、在线状态、已读回执与限流"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_redis = None
_redis_failed = False


def get_redis():
    """懒加载 Redis 客户端，不可用时返回 None"""
    global _redis, _redis_failed
    if _redis is None and not _redis_failed:
        try:
            import redis
            from config import config
            _redis = redis.Redis.from_url(
                config.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            _redis.ping()
            _redis_failed = False
        except Exception as exc:
            logger.warning("Redis 不可用，聊天扩展能力降级: %s", exc)
            _redis = None
            _redis_failed = True
    return _redis


def incr_unread(player_id: int, field: str, delta: int = 1) -> None:
    """增加玩家未读数"""
    client = get_redis()
    if client is None:
        return
    try:
        client.hincrby("chat:unread:{}".format(player_id), field, delta)
    except Exception as exc:
        logger.warning("未读数增加失败: %s", exc)


def clear_unread(player_id: int, field: Optional[str] = None) -> None:
    """清除玩家未读，field 为空时清除全部"""
    client = get_redis()
    if client is None:
        return
    try:
        key = "chat:unread:{}".format(player_id)
        if field:
            client.hdel(key, field)
        else:
            client.delete(key)
    except Exception as exc:
        logger.warning("未读清除失败: %s", exc)


def get_unread(player_id: int) -> Dict[str, object]:
    """获取玩家未读数，世界/帮派不再累计，仅返回私聊"""
    result = {"world": 0, "guild": 0, "private_total": 0, "private": {}}
    client = get_redis()
    if client is None:
        return result
    try:
        raw = client.hgetall("chat:unread:{}".format(player_id))
        private_total = 0
        for key, value in raw.items():
            if key.startswith("p:"):
                friend_id = int(key[2:])
                count = int(value or 0)
                result["private"][friend_id] = count
                private_total += count
        result["private_total"] = private_total
    except Exception as exc:
        logger.warning("未读读取失败: %s", exc)
    return result


def mark_online(player_id: int, conn_id: str) -> None:
    """标记玩家在线，并记录连接 token"""
    client = get_redis()
    if client is None:
        return
    try:
        conn_key = "chat:conn:{}".format(player_id)
        pipe = client.pipeline()
        pipe.sadd(conn_key, conn_id)
        pipe.expire(conn_key, 300)
        pipe.set("chat:online:{}".format(player_id), "1", ex=90)
        pipe.sadd("chat:online_ids", player_id)
        pipe.execute()
    except Exception as exc:
        logger.warning("在线状态写入失败: %s", exc)


def mark_offline(player_id: int, conn_id: str) -> None:
    """移除连接 token，无剩余连接时清除在线状态"""
    client = get_redis()
    if client is None:
        return
    try:
        conn_key = "chat:conn:{}".format(player_id)
        client.srem(conn_key, conn_id)
        if client.scard(conn_key) == 0:
            pipe = client.pipeline()
            pipe.delete(conn_key)
            pipe.delete("chat:online:{}".format(player_id))
            pipe.srem("chat:online_ids", player_id)
            pipe.execute()
    except Exception as exc:
        logger.warning("在线状态清除失败: %s", exc)


def get_online_ids() -> List[int]:
    """获取在线玩家 ID 列表"""
    client = get_redis()
    if client is None:
        return []
    try:
        values = client.smembers("chat:online_ids")
        return [int(value) for value in values]
    except Exception as exc:
        logger.warning("在线列表读取失败: %s", exc)
        return []


def get_online(player_ids: List[int]) -> Dict[int, bool]:
    """批量查询玩家是否在线"""
    result = {player_id: False for player_id in player_ids}
    if not player_ids:
        return result
    client = get_redis()
    if client is None:
        return result
    try:
        keys = ["chat:online:{}".format(player_id) for player_id in player_ids]
        values = client.mget(keys)
        for player_id, value in zip(player_ids, values):
            result[player_id] = bool(value)
    except Exception as exc:
        logger.warning("在线状态查询失败: %s", exc)
    return result


def set_read_cursor(player_id: int, friend_id: int, msg_id: int) -> None:
    """记录玩家已读到的好友消息 ID"""
    client = get_redis()
    if client is None:
        return
    try:
        key = "chat:read:{}:{}".format(player_id, friend_id)
        current = client.get(key)
        if current is None or int(current) < msg_id:
            client.set(key, msg_id)
    except Exception as exc:
        logger.warning("已读游标写入失败: %s", exc)


def get_read_cursor(player_id: int, friend_id: int) -> int:
    """获取玩家已读到的好友消息 ID"""
    client = get_redis()
    if client is None:
        return 0
    try:
        value = client.get("chat:read:{}:{}".format(player_id, friend_id))
        return int(value) if value else 0
    except Exception as exc:
        logger.warning("已读游标读取失败: %s", exc)
        return 0


def check_rate_limit(player_id: int, limit: int = 20,
                     window: int = 60) -> bool:
    """按时间窗口限制发言频率，Redis 不可用时放行"""
    client = get_redis()
    if client is None:
        return True
    try:
        key = "chat:rate:{}".format(player_id)
        count = client.incr(key)
        if count == 1:
            client.expire(key, window)
        return count <= limit
    except Exception as exc:
        logger.warning("限流检查失败: %s", exc)
        return True


def set_session(user_id: int, token: str) -> None:
    """记录用户当前登录 token，用于单点登录"""
    client = get_redis()
    if client is None:
        return
    try:
        from config import config
        client.set(
            "session:{}".format(user_id), token,
            ex=config.JWT_EXPIRE_HOURS * 3600,
        )
    except Exception as exc:
        logger.warning("登录会话写入失败: %s", exc)


def is_session_valid(user_id: int, token: str) -> bool:
    """判断 token 是否仍是该用户当前有效会话"""
    client = get_redis()
    if client is None:
        return True
    try:
        current = client.get("session:{}".format(user_id))
        return bool(current) and current == token
    except Exception as exc:
        logger.warning("登录会话校验失败: %s", exc)
        return True
