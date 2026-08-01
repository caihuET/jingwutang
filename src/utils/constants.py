"""游戏常量定义"""
import random


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


# 装备基础属性键与展示名
BASE_STAT_KEYS = ("attack", "defense", "magic_attack", "magic_defense", "hp", "mp", "speed")

STAT_NAMES = {
    "attack": "外功攻击",
    "defense": "外功防御",
    "magic_attack": "内功攻击",
    "magic_defense": "内功防御",
    "hp": "生命",
    "mp": "内力",
    "speed": "速度",
}


def get_base_max_stamina(level: int) -> int:
    """等级体力上限：100 + 每 10 级 +5，封顶 150"""
    return min(150, 100 + (level // 10) * 5)


# 强化成长率（按穿戴等级带，非强化等级）
ENHANCE_RATE_BY_BAND = {1: 0.06, 5: 0.07, 15: 0.08, 25: 0.09, 40: 0.10, 60: 0.12}

# 强化成长品质倍率
ENHANCE_QUALITY_MULTIPLIER = {1: 1.00, 2: 1.05, 3: 1.10, 4: 1.15, 5: 1.20, 6: 1.25}


def get_enhance_band(level_required: int) -> int:
    """返回穿戴等级所属强化等级带"""
    for band in (60, 40, 25, 15, 5, 1):
        if level_required >= band:
            return band
    return 1


def calc_enhance_stats(base_stats: dict, level_required: int, quality: int, enhance_level: int) -> dict:
    """按穿戴等级带与品质计算强化累计属性"""
    band = get_enhance_band(level_required)
    rate = ENHANCE_RATE_BY_BAND.get(band, 0.06) * ENHANCE_QUALITY_MULTIPLIER.get(quality, 1.0)
    result = {}
    for key in BASE_STAT_KEYS:
        base = int(base_stats.get(key) or 0)
        result[key] = round(base * rate * enhance_level)
    return result


# 附加属性类型：1=外攻 2=外防 3=内攻 4=内防 5=速度 6=生命 7=内力 8=体力上限
AFFIX_TYPES = {
    1: "外功攻击",
    2: "外功防御",
    3: "内功攻击",
    4: "内功防御",
    5: "速度",
    6: "生命",
    7: "内力",
    8: "体力上限",
}

AFFIX_STAT_KEYS = {
    1: "attack",
    2: "defense",
    3: "magic_attack",
    4: "magic_defense",
    5: "speed",
    6: "hp",
    7: "mp",
    8: "stamina",
}

# 各品质附加属性条数
AFFIX_COUNT_BY_QUALITY = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}

# 附加属性值域：品质 -> 类型 -> (最小值, 最大值)
AFFIX_VALUE_RANGE = {
    1: {1: (2, 4), 2: (1, 3), 3: (2, 4), 4: (1, 3), 5: (1, 1), 6: (5, 10), 7: (3, 6), 8: (1, 2)},
    2: {1: (5, 9), 2: (3, 6), 3: (5, 9), 4: (3, 6), 5: (1, 2), 6: (12, 20), 7: (8, 14), 8: (2, 4)},
    3: {1: (10, 18), 2: (6, 12), 3: (10, 18), 4: (6, 12), 5: (2, 3), 6: (25, 45), 7: (16, 28), 8: (4, 6)},
    4: {1: (20, 32), 2: (12, 20), 3: (20, 32), 4: (12, 20), 5: (3, 5), 6: (50, 80), 7: (30, 50), 8: (6, 8)},
    5: {1: (35, 55), 2: (22, 36), 3: (35, 55), 4: (22, 36), 5: (5, 7), 6: (90, 130), 7: (55, 85), 8: (8, 12)},
    6: {1: (60, 100), 2: (38, 60), 3: (60, 100), 4: (38, 60), 5: (7, 10), 6: (140, 200), 7: (90, 130), 8: (10, 15)},
}

# 部位附加属性权重（值越大越容易随机到）
AFFIX_SLOT_WEIGHTS = {
    1: {1: 30, 3: 30, 5: 12, 7: 10, 6: 8, 2: 5, 4: 5, 8: 4},
    2: {2: 26, 6: 24, 4: 22, 3: 6, 7: 6, 8: 6, 1: 5, 5: 5},
    3: {6: 28, 2: 26, 4: 20, 1: 6, 3: 6, 7: 6, 5: 4, 8: 4},
    4: {8: 24, 7: 22, 6: 18, 2: 16, 4: 10, 5: 8, 1: 2, 3: 2},
    5: {5: 34, 2: 20, 4: 16, 6: 12, 7: 8, 8: 6, 1: 4, 3: 4},
    6: {7: 24, 3: 22, 6: 16, 1: 12, 4: 12, 5: 8, 8: 4, 2: 4},
}


def generate_affixes(quality: int, slot: int, rng: random.Random = None) -> list:
    """按品质和部位随机生成附加属性，同件装备不重复"""
    rng = rng or random
    count = AFFIX_COUNT_BY_QUALITY.get(quality, 1)
    weights = AFFIX_SLOT_WEIGHTS.get(slot, AFFIX_SLOT_WEIGHTS[1])
    pool = [t for t in AFFIX_TYPES if t in weights]
    result = []
    for _ in range(count):
        if not pool:
            break
        total = sum(weights[t] for t in pool)
        pick = rng.randint(1, total)
        cursor = 0
        chosen = pool[0]
        for t in pool:
            cursor += weights[t]
            if pick <= cursor:
                chosen = t
                break
        vmin, vmax = AFFIX_VALUE_RANGE.get(quality, {}).get(chosen, (1, 1))
        result.append({
            "affix_type": chosen,
            "value": rng.randint(vmin, vmax),
            "sort_order": len(result) + 1,
        })
        pool.remove(chosen)
    return result


def calc_equip_power(bonuses: dict) -> int:
    """装备战力：攻击 + 内攻 + (防御+内防)*2 + 生命//2 + 内力//2 + 速度 + 体力//2"""
    attack = bonuses.get("attack", 0)
    magic_attack = bonuses.get("magic_attack", 0)
    defense = bonuses.get("defense", 0)
    magic_defense = bonuses.get("magic_defense", 0)
    hp = bonuses.get("hp", 0)
    mp = bonuses.get("mp", 0)
    speed = bonuses.get("speed", 0)
    stamina = bonuses.get("stamina", 0)
    return int(attack + magic_attack + (defense + magic_defense) * 2 + hp // 2 + mp // 2 + speed + stamina // 2)
