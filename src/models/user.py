"""用户账号模型"""
from sqlalchemy import Column, BigInteger, String, DateTime, Integer, func
from src.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(32), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    register_ip = Column(String(45), nullable=False)
    status = Column(Integer, default=1)
    last_login_at = Column(DateTime(6), nullable=True)
    created_at = Column(DateTime(6), default=func.now(), nullable=False)
    updated_at = Column(DateTime(6), default=func.now(), onupdate=func.now(), nullable=False)
