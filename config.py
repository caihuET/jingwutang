"""应用配置"""
import os


class Config:
    """应用配置类, 从环境变量读取"""

    # 路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 数据库
    DB_HOST = os.getenv("DB_HOST", "mysql")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Aa123,,")
    DB_NAME = os.getenv("DB_NAME", "jingwutang")
    DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "jingwutang-dev-secret-key-2026")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_HOURS = 24

    # 应用
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    APP_ROOT_PATH = os.getenv("APP_ROOT_PATH", "/game/jwt")

    # 静态文件
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")


config = Config()
