"""用户账号模型"""
from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Index, func
from src.models.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("uk_oauth", "oauth_provider", "oauth_id", unique=True),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(32), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    register_ip = Column(String(45), nullable=False)
    oauth_provider = Column(String(16), nullable=True)
    oauth_id = Column(String(64), nullable=True)
    oauth_name = Column(String(32), nullable=True)
    oauth_avatar = Column(String(512), nullable=True)
    email = Column(String(128), nullable=True)
    status = Column(Integer, default=1)
    last_login_at = Column(DateTime(6), nullable=True)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)
    updated_at = Column(DateTime(6), default=func.now(), onupdate=func.now(), nullable=False)
