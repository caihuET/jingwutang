"""认证服务"""
from src.utils.security import hash_password, verify_password, create_token
from src.utils.validators import validate_username, validate_password
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.repository.user_repo import UserRepository


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
        return {"token": token, "user_id": user.id}
