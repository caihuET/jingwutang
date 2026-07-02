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

    # 运行迁移：battle_logs.defender_id 改为 signed（init.sql 误设为 UNSIGNED）
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE battle_logs MODIFY COLUMN defender_id BIGINT NULL"))
            conn.commit()
    except Exception:
        pass

    # 初始化任务数据（如果表为空）
    try:
        with engine.connect() as conn:
            cnt = conn.execute(text("SELECT COUNT(*) FROM task_definitions")).scalar()
            if cnt == 0:
                sql = open("migrations/init.sql", "r", encoding="utf-8").read()
                i = sql.find("INSERT INTO task_definitions")
                j = sql.index(";", i) + 1
                conn.execute(text(sql[i:j]))
                conn.commit()
                import logging
                logging.getLogger(__name__).info("任务数据初始化完成")
    except Exception:
        pass


    # 初始化技能定义（如果表为空，从 init.sql 提取）
    try:
        with engine.connect() as conn:
            cnt = conn.execute(text("SELECT COUNT(*) FROM skill_definitions")).scalar()
            if cnt == 0:
                sql_text = open("migrations/init.sql", "r", encoding="utf-8").read()
                si = sql_text.find("INSERT INTO skill_definitions")
                ei = sql_text.index(";", si) + 1
                conn.execute(text(sql_text[si:ei]))
                conn.commit()
            
            # 为已有角色补发门派技能（如果还没有技能）
            rows = conn.execute(text("""
                SELECT p.id, p.school_id FROM players p 
                WHERE NOT EXISTS (SELECT 1 FROM player_skills ps WHERE ps.player_id = p.id)
            """)).fetchall()
            for pid, sid in rows:
                sk = conn.execute(text(
                    "SELECT id FROM skill_definitions WHERE school_id = :s ORDER BY id"
                ), {"s": sid}).fetchall()
                for i, (skid,) in enumerate(sk):
                    slot = i + 1 if i < 4 else None
                    conn.execute(text(
                        "INSERT INTO player_skills (player_id, skill_id, level, proficiency, slot_position, is_learned) VALUES (:p, :s, 1, 0, :sl, 1)"
                    ), {"p": pid, "s": skid, "sl": slot})
            if rows:
                conn.commit()
    except Exception:
        pass

    # 初始化装备定义（如果表为空）
    try:
        with engine.connect() as conn:
            cnt = conn.execute(text("SELECT COUNT(*) FROM equipment_definitions")).scalar()
            if cnt == 0:
                conn.execute(text("""
                    INSERT INTO equipment_definitions (name, slot, quality, level_required, base_attack, base_defense, base_hp) VALUES
                    ('青铜短剑', 1, 1, 1, 8, 0, 0),
                    ('粗布帽', 2, 1, 1, 0, 3, 5),
                    ('麻布衣', 3, 1, 1, 0, 5, 10),
                    ('破旧腰带', 4, 1, 1, 0, 2, 0),
                    ('草鞋', 5, 1, 1, 0, 1, 0),
                    ('木项链', 6, 1, 1, 1, 0, 5),
                    ('铁剑', 1, 2, 5, 18, 0, 0),
                    ('青铜盔', 2, 2, 5, 0, 8, 12),
                    ('皮甲', 3, 2, 5, 0, 12, 25),
                    ('铁腰带', 4, 2, 5, 0, 5, 0),
                    ('布靴', 5, 2, 5, 0, 3, 0),
                    ('银项链', 6, 2, 5, 3, 0, 10),
                    ('精钢剑', 1, 3, 15, 35, 0, 0),
                    ('精钢盔', 2, 3, 15, 0, 15, 25),
                    ('锁子甲', 3, 3, 15, 0, 22, 50),
                    ('虎皮带', 4, 3, 15, 0, 8, 0),
                    ('鹿皮靴', 5, 3, 15, 0, 6, 0),
                    ('翡翠项链', 6, 3, 15, 8, 0, 20)
                """))
                conn.commit()
    except Exception:
        pass
