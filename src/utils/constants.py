"""游戏常量定义"""


class SchoolType:
    """门派类型"""
    SHAOLIN = 1
    WUDANG = 2
    EMEI = 3
    TANGMEN = 4
    GAIBANG = 5
    MINGJIAO = 6

    NAMES = {
        1: "少林", 2: "武当", 3: "峨眉",
        4: "唐门", 5: "丐帮", 6: "明教",
    }


class EquipSlot:
    """装备部位"""
    WEAPON = 1
    HELMET = 2
    ARMOR = 3
    BELT = 4
    BOOTS = 5
    NECKLACE = 6

    NAMES = {
        WEAPON: "武器",
        HELMET: "头盔",
        ARMOR: "衣甲",
        BELT: "腰带",
        BOOTS: "靴子",
        NECKLACE: "项链",
    }


class EquipQuality:
    """装备品质"""
    GRAY = 1
    GREEN = 2
    BLUE = 3
    PURPLE = 4
    ORANGE = 5
    RED = 6

    NAMES = {
        1: "普通", 2: "优秀", 3: "精良",
        4: "史诗", 5: "传说", 6: "红装",
    }

    COLORS = {
        1: "gray", 2: "green", 3: "blue",
        4: "purple", 5: "orange", 6: "red",
    }


class TaskType:
    """任务类型"""
    MAIN = 1
    DAILY = 2
    SCHOOL = 3
    ACHIEVEMENT = 4


class BattleType:
    """战斗类型"""
    PVE = 1
    ARENA = 2
    SPAR = 3


class SkillType:
    """技能类型"""
    NORMAL_ATTACK = 1
    PHYSICAL = 2
    MAGIC = 3
    SUPPORT = 4
    PASSIVE = 5


class ChatChannel:
    """聊天频道"""
    WORLD = 1
    GUILD = 2
    PRIVATE = 3


class FriendStatus:
    """好友申请状态"""
    PENDING = 0
    ACCEPTED = 1
    REJECTED = 2
    REMOVED = 3

    NAMES = {
        PENDING: "等待回应",
        ACCEPTED: "对方已同意",
        REJECTED: "对方已拒绝",
        REMOVED: "已解除",
    }


class GuildApplicationStatus:
    """帮派申请状态"""
    PENDING = 0
    ACCEPTED = 1
    REJECTED = 2

    NAMES = {
        PENDING: "等待审核",
        ACCEPTED: "已通过",
        REJECTED: "已拒绝",
    }


class ErrorCode:
    """错误码"""
    SUCCESS = 0
    USERNAME_EXISTS = 1001
    PASSWORD_FORMAT = 1002
    NICKNAME_EXISTS = 1003
    NICKNAME_SENSITIVE = 1004
    STAMINA_NOT_ENOUGH = 1005
    GOLD_NOT_ENOUGH = 1006
    INGOT_NOT_ENOUGH = 1007
    LEVEL_NOT_ENOUGH = 1008
    REPUTATION_NOT_ENOUGH = 1009
    EQUIP_NOT_FOUND = 1010
    EQUIP_MAX_LEVEL = 1011
    SKILL_NOT_SLOTTED = 1012
    TARGET_OFFLINE = 1013
    ALREADY_FRIENDS = 1014
    GUILD_FULL = 1015
    DAILY_LIMIT = 1016
    ARENA_COOLDOWN = 1017
    ITEM_NOT_FOUND = 1018
    TOKEN_INVALID = 2001
    ACCOUNT_DISABLED = 2002
    PARAM_INVALID = 2003
    RATE_LIMITED = 2004
    SERVER_ERROR = 5000

    MESSAGES = {
        1001: "用户名已存在",
        1002: "密码格式不正确",
        1005: "体力不足",
        1006: "金币不足",
        2001: "Token 无效或已过期",
        2003: "请求参数校验失败",
        5000: "服务器内部错误",
    }


# 经验曲线: EXP_TABLE[level] = 升级到下一级所需经验
EXP_TABLE = [0]
for level in range(1, 101):
    if level <= 10:
        exp = 100 * level
    elif level <= 30:
        exp = level * level * 10
    elif level <= 60:
        exp = level * level * 20
    else:
        exp = level * level * 40
    EXP_TABLE.append(exp)


# 强化成功率
ENHANCE_RATES = {
    0: 1.0, 1: 1.0, 2: 0.95, 3: 0.85,
    4: 0.75, 5: 0.65, 6: 0.55, 7: 0.45,
    8: 0.35, 9: 0.30, 10: 0.25, 11: 0.20,
    12: 0.15, 13: 0.12, 14: 0.10,
    15: 0.08, 16: 0.06, 17: 0.05, 18: 0.04, 19: 0.03,
}

# 各品质装备的强化上限
ENHANCE_MAX_BY_QUALITY = {
    1: 5, 2: 8, 3: 12, 4: 15, 5: 18, 6: 20,
}

# 门派技能解锁等级（索引对应门派技能顺序）
SKILL_UNLOCK_LEVELS = {0: 1, 1: 1, 2: 5, 3: 10, 4: 15, 5: 25, 6: 40, 7: 60}


# 被动技能解锁等级
PASSIVE_SKILL_UNLOCK_LEVEL = 20


# 各门派标准被动技能名（兼容历史乱码数据）
PASSIVE_NAMES_BY_SCHOOL = {
    1: "金刚不坏体",
    2: "太极心法",
    3: "慈航心经",
    4: "百毒不侵",
    5: "打狗心法",
    6: "圣火护体",
}


def get_passive_name(school_id: int, fallback: str) -> str:
    """按门派返回标准被动技能名"""
    return PASSIVE_NAMES_BY_SCHOOL.get(school_id, fallback)


# 被动技能效果（数值随技能等级线性提升）
PASSIVE_SKILL_EFFECTS = {
    "金刚不坏体": {"defense": 2, "max_hp": 30},
    "太极心法": {"magic_attack": 3, "max_mp": 10},
    "慈航心经": {"heal_per_round": 5},
    "百毒不侵": {"crit_rate": 0.01, "dodge_rate": 0.01},
    "打狗心法": {"attack": 3, "lifesteal": 0.02},
    "圣火护体": {"reflect_rate": 0.10},
}
