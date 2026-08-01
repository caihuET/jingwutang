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



    import src.models.shop  # noqa: F401



    import src.models.social  # noqa: F401



    import src.models.player  # noqa: F401



    import src.models.title  # noqa: F401



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






    # 运行迁移：补充被动技能/称号字段（列不存在时自动添加，幂等）
    try:
        with engine.connect() as conn:
            migrate_cols = [
                ("skill_definitions", "unlock_level",
                 "ALTER TABLE skill_definitions ADD COLUMN unlock_level INT DEFAULT 0 AFTER cooldown"),
                ("players", "equipped_title_id",
                 "ALTER TABLE players ADD COLUMN equipped_title_id INT NULL AFTER title"),
                ("task_definitions", "reward_title_id",
                 "ALTER TABLE task_definitions ADD COLUMN reward_title_id INT NULL AFTER reward_item_id"),
            ]
            for table_name, column_name, ddl in migrate_cols:
                cnt = conn.execute(text(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND COLUMN_NAME=:c"
                ), {"t": table_name, "c": column_name}).scalar()
                if not cnt:
                    conn.execute(text(ddl))
            conn.execute(text("""
                UPDATE title_definitions SET title_level = CASE
                    WHEN name='江湖侠客' THEN 1
                    WHEN name IN ('百战勇士','千锤百炼') THEN 2
                    WHEN name IN ('富甲一方','六脉通达') THEN 3
                    WHEN name IN ('武林至尊','武林高手') THEN 4
                    ELSE title_level END
            """))
            conn.commit()
    except Exception:
        pass



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



                    INSERT INTO equipment_definitions (name, slot, quality, level_required, base_attack, base_defense, base_magic_attack, base_magic_defense, base_hp, base_mp, base_speed) VALUES

                    ('青铜短剑', 1, 1, 1, 8, 0, 3, 0, 0, 0, 0),

                    ('粗布帽', 2, 1, 1, 0, 3, 0, 2, 5, 1, 0),

                    ('麻布衣', 3, 1, 1, 0, 5, 0, 3, 10, 2, 0),

                    ('破旧腰带', 4, 1, 1, 0, 2, 0, 1, 5, 2, 1),

                    ('草鞋', 5, 1, 1, 0, 1, 0, 0, 0, 0, 3),

                    ('木项链', 6, 1, 1, 1, 0, 1, 2, 5, 10, 1),

                    ('铁剑', 1, 2, 5, 18, 0, 7, 0, 0, 0, 0),

                    ('青铜盔', 2, 2, 5, 0, 8, 0, 5, 12, 2, 0),

                    ('皮甲', 3, 2, 5, 0, 12, 0, 7, 25, 5, 0),

                    ('铁腰带', 4, 2, 5, 0, 5, 0, 2, 10, 3, 2),

                    ('布靴', 5, 2, 5, 0, 3, 0, 1, 0, 0, 6),

                    ('银项链', 6, 2, 5, 3, 0, 2, 4, 10, 20, 2),

                    ('精钢剑', 1, 3, 15, 35, 0, 14, 0, 0, 0, 0),

                    ('精钢盔', 2, 3, 15, 0, 15, 0, 9, 25, 5, 0),

                    ('锁子甲', 3, 3, 15, 0, 22, 0, 13, 50, 10, 0),

                    ('虎皮带', 4, 3, 15, 0, 8, 0, 3, 20, 6, 3),

                    ('鹿皮靴', 5, 3, 15, 0, 6, 0, 2, 0, 0, 10),

                    ('翡翠项链', 6, 3, 15, 8, 0, 6, 6, 20, 40, 3),

                    ('玄铁重剑', 1, 4, 25, 60, 0, 24, 0, 0, 0, 0),

                    ('玄铁头盔', 2, 4, 25, 0, 25, 0, 15, 40, 8, 0),

                    ('金丝软甲', 3, 4, 25, 0, 35, 0, 21, 80, 16, 0),

                    ('龙纹腰带', 4, 4, 25, 0, 12, 0, 5, 30, 9, 4),

                    ('追风靴', 5, 4, 25, 0, 10, 0, 4, 0, 0, 15),

                    ('玛瑙项链', 6, 4, 25, 15, 0, 12, 10, 35, 60, 4),

                    ('天罡剑', 1, 5, 40, 100, 0, 40, 0, 0, 0, 0),

                    ('天罡盔', 2, 5, 40, 0, 40, 0, 24, 60, 12, 0),

                    ('天蚕宝甲', 3, 5, 40, 0, 55, 0, 33, 120, 24, 0),

                    ('蟠龙腰带', 4, 5, 40, 0, 20, 0, 8, 45, 14, 5),

                    ('踏云靴', 5, 5, 40, 0, 15, 0, 6, 0, 0, 22),

                    ('血玉项链', 6, 5, 40, 25, 0, 20, 16, 60, 90, 5),

                    ('屠龙刀', 1, 6, 60, 160, 0, 64, 0, 0, 0, 0),

                    ('赤龙盔', 2, 6, 60, 0, 65, 0, 39, 100, 20, 0),

                    ('火凤宝衣', 3, 6, 60, 0, 90, 0, 54, 200, 40, 0),

                    ('朱雀腰带', 4, 6, 60, 0, 30, 0, 12, 60, 18, 6),

                    ('腾云靴', 5, 6, 60, 0, 22, 0, 9, 0, 0, 30),

                    ('凤鸣项链', 6, 6, 60, 40, 0, 32, 24, 90, 140, 6)

                """))



                conn.commit()



    except Exception:



        pass


    # 迁移: players 表补充 guild_id / vip_until

    try:

        with engine.connect() as conn:

            conn.execute(text("ALTER TABLE players ADD COLUMN guild_id BIGINT NULL"))

            conn.execute(text("ALTER TABLE players ADD COLUMN vip_until DATETIME(6) NULL"))

            conn.commit()

    except Exception:

        pass


    # 迁移: 好友关系与聊天消息补充字段

    try:

        with engine.connect() as conn:

            conn.execute(text("ALTER TABLE friend_relationships ADD COLUMN last_gift_at DATETIME(6) NULL"))

            conn.execute(text("ALTER TABLE chat_messages ADD COLUMN guild_id INT NULL"))

            conn.commit()

    except Exception:

        pass


    # 初始化商城商品（如果表为空）

    try:

        with engine.connect() as conn:

            cnt = conn.execute(text("SELECT COUNT(*) FROM shop_items")).scalar()

            if cnt == 0:

                conn.execute(text("""
                    INSERT INTO shop_items (name, category, item_type, effect_value, price_type, price, daily_limit, description, sort_order) VALUES
                    ('体力药剂(小)', 1, 1, 30, 1, 5, 3, '恢复 30 点体力', 1),
                    ('体力药剂(大)', 1, 1, 80, 2, 1, 2, '恢复 80 点体力', 2),
                    ('经验加成券', 1, 2, 1000, 1, 100, 5, '获得 1000 点经验', 3),
                    ('强化石', 2, 3, 1, 2, 5, 0, '装备强化材料', 1),
                    ('称号·武林至尊', 3, 4, 0, 2, 100, 0, '使用后获得称号', 1),
                    ('称号·江湖侠客', 3, 4, 0, 2, 50, 0, '使用后获得称号', 2),
                    ('VIP周卡', 4, 6, 7, 2, 60, 0, '7 天 VIP', 1),
                    ('VIP月卡', 4, 5, 30, 2, 180, 0, '30 天 VIP', 2)
                """))

                conn.commit()

    except Exception:

        pass

