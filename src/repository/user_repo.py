"""用户数据访问"""
from src.models.user import User


class UserRepository:
    """用户表操作"""

    def __init__(self, db):
        self.db = db

    def get_by_username(self, username: str) -> User:
        """根据用户名查询"""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> User:
        """根据 ID 查询"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_oauth(self, provider: str, oauth_id: str) -> User:
        """根据第三方登录标识查询"""
        return self.db.query(User).filter(
            User.oauth_provider == provider,
            User.oauth_id == oauth_id,
        ).first()

    def create_oauth(self, username: str, password_hash: str,
                     register_ip: str, provider: str, oauth_id: str,
                     oauth_name: str = "", oauth_avatar: str = "",
                     email: str = "") -> User:
        """创建第三方登录用户"""
        user = User(
            username=username,
            password_hash=password_hash,
            register_ip=register_ip,
            oauth_provider=provider,
            oauth_id=oauth_id,
            oauth_name=oauth_name or None,
            oauth_avatar=oauth_avatar or None,
            email=email or None,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create(self, username: str, password_hash: str, register_ip: str) -> User:
        """创建用户"""
        user = User(username=username, password_hash=password_hash, register_ip=register_ip)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
