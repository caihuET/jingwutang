"""输入校验"""
import re


def validate_username(username: str) -> bool:
    """校验用户名: 4-16 位字母/数字/下划线"""
    if not username:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_]{4,16}$", username))


def validate_password(password: str) -> bool:
    """校验密码: 8-20 位, 必须含字母和数字"""
    if not password or len(password) < 8 or len(password) > 20:
        return False
    if not re.search(r"[a-zA-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


def validate_nickname(nickname: str) -> bool:
    """校验昵称: 2-8 中文或 4-16 英文"""
    if not nickname:
        return False
    if re.match(r"^[a-zA-Z]{4,16}$", nickname):
        return True
    cn_count = sum(1 for c in nickname if ord(c) > 0x4E00)
    en_count = sum(1 for c in nickname if c.isascii() and c.isalpha())
    total = cn_count + en_count * 0.5
    return 2 <= total <= 8


def check_sensitive_words(text: str) -> bool:
    """检查敏感词"""
    if not text:
        return True
    sensitive = ["管理员", "系统", "admin", "root", "test"]
    for word in sensitive:
        if word in text.lower():
            return False
    return True
