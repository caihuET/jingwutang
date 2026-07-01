"""数据库连接"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import config

engine = create_engine(config.DB_URL, pool_size=10, max_overflow=20, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库：自动创建数据库和表"""
    from sqlalchemy import text
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        import pymysql
        conn = pymysql.connect(
            host=config.DB_HOST, port=config.DB_PORT,
            user=config.DB_USER, password=config.DB_PASSWORD,
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` CHARACTER SET utf8mb4")
        conn.close()
        Base.metadata.create_all(bind=engine)

    # 运行迁移：补充 player_equipment 缺少的增强字段
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE player_equipment ADD COLUMN enhance_attack INT DEFAULT 0"))
            conn.execute(text("ALTER TABLE player_equipment ADD COLUMN enhance_defense INT DEFAULT 0"))
            conn.execute(text("ALTER TABLE player_equipment ADD COLUMN enhance_hp INT DEFAULT 0"))
            conn.commit()
    except Exception:
        pass  # 列已存在时忽略
