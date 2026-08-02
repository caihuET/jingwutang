"""认证服务"""
import secrets
from datetime import datetime

from src.utils.security import hash_password, verify_password, create_token
from src.utils.validators import validate_username, validate_password
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.repository.user_repo import UserRepository
from src.utils.redis_client import set_session


class AuthService:
    """用户认证业务"""

    def __init__(self, db):
        self.repo = UserRepository(db)

    def register(self, username: str, password: str) -> dict:
        """用户注册"""
        if not validate_username(username):
            raise GameException(ErrorCode.PARAM_INVALID, "用户名格式不正确")
        if not validate_password(password):
            raise GameException(ErrorCode.PASSWORD_FORMAT, "密码格式不正确")
        if self.repo.get_by_username(username):
            raise GameException(ErrorCode.USERNAME_EXISTS, "用户名已存在")
        user = self.repo.create(username, hash_password(password), "0.0.0.0")
        return {"user_id": user.id}

    def login(self, username: str, password: str) -> dict:
        """用户登录"""
        user = self.repo.get_by_username(username)
        if not user:
            raise GameException(ErrorCode.PARAM_INVALID, "用户名或密码错误")
        if not verify_password(password, user.password_hash):
            raise GameException(ErrorCode.PARAM_INVALID, "用户名或密码错误")
        if user.status != 1:
            raise GameException(ErrorCode.ACCOUNT_DISABLED, "账号已被禁用")
        token = create_token(user.id)
        set_session(user.id, token)
        return {"token": token, "user_id": user.id}

    def oauth_login(self, provider: str, oauth_id: str,
                    oauth_name: str = "", email: str = "",
                    oauth_avatar: str = "") -> dict:
        """第三方登录：已注册直接登录，未注册自动创建账号"""
        user = self.repo.get_by_oauth(provider, oauth_id)
        created = False
        if not user:
            username = self._unique_username(self._oauth_username(provider, oauth_id))
            user = self.repo.create_oauth(
                username,
                hash_password(secrets.token_urlsafe(24)),
                "0.0.0.0",
                provider,
                oauth_id,
                oauth_name,
                oauth_avatar,
                email,
            )
            created = True
        if user.status != 1:
            raise GameException(ErrorCode.ACCOUNT_DISABLED, "账号已被禁用")
        user.last_login_at = datetime.utcnow()
        self.repo.db.commit()
        token = create_token(user.id)
        set_session(user.id, token)
        return {"token": token, "user_id": user.id, "created": created}

    def _oauth_username(self, provider: str, oauth_id: str) -> str:
        """生成第三方账号默认用户名"""
        prefix = "wx" if provider == "wechat" else "gg"
        suffix = oauth_id[-12:] if len(oauth_id) > 12 else oauth_id
        return "{}_{}".format(prefix, suffix)

    def _unique_username(self, base: str) -> str:
        """确保第三方用户名不冲突"""
        candidate = base[:24]
        while self.repo.get_by_username(candidate):
            candidate = "{} {}".format(base[:20], secrets.token_hex(2))
        return candidate
