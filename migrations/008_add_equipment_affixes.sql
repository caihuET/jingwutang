-- 迁移: 装备属性系统（基础属性补齐 + 强化成长公式 + 附加属性）
-- 影响分析:
--   1. equipment_definitions 新增 base_mp，并补齐各模板的内功攻击/内功防御/内力/速度及腰带生命
--   2. player_equipment 新增 4 个强化属性列，强化改为按穿戴等级带+品质重算
--   3. 新增 player_equipment_affixes 表存储附加属性
-- 风险: 仅新增列/表与 UPDATE 模板数值，不删除列和数据；存量玩家装备需再执行补发脚本
-- 注意: 只执行一次；重复执行 ALTER 会报列已存在

USE jingwutang;

ALTER TABLE equipment_definitions
    ADD COLUMN base_mp INT DEFAULT 0 AFTER base_hp;

ALTER TABLE player_equipment
    ADD COLUMN enhance_magic_attack INT DEFAULT 0 AFTER enhance_defense,
    ADD COLUMN enhance_magic_defense INT DEFAULT 0 AFTER enhance_magic_attack,
    ADD COLUMN enhance_mp INT DEFAULT 0 AFTER enhance_hp,
    ADD COLUMN enhance_speed INT DEFAULT 0 AFTER enhance_mp;

CREATE TABLE IF NOT EXISTS player_equipment_affixes (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    equip_id BIGINT UNSIGNED NOT NULL,
    affix_type TINYINT NOT NULL COMMENT '1=外攻 2=外防 3=内攻 4=内防 5=速度 6=生命 7=内力 8=体力上限',
    value INT NOT NULL,
    sort_order TINYINT DEFAULT 0,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_equip_id (equip_id),
    CONSTRAINT fk_equip_affix FOREIGN KEY (equip_id) REFERENCES player_equipment(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 补齐装备模板基础属性（部位定位见设计文档）
-- 武器：内功攻击 = 40% 外功攻击
UPDATE equipment_definitions SET base_magic_attack = 3 WHERE name = '青铜短剑';
UPDATE equipment_definitions SET base_magic_attack = 7 WHERE name = '铁剑';
UPDATE equipment_definitions SET base_magic_attack = 14 WHERE name = '精钢剑';
UPDATE equipment_definitions SET base_magic_attack = 24 WHERE name = '玄铁重剑';
UPDATE equipment_definitions SET base_magic_attack = 40 WHERE name = '天罡剑';
UPDATE equipment_definitions SET base_magic_attack = 64 WHERE name = '屠龙刀';

-- 头盔：内功防御 = 60% 外功防御，内力 = 20% 生命
UPDATE equipment_definitions SET base_magic_defense = 2, base_mp = 1 WHERE name = '粗布帽';
UPDATE equipment_definitions SET base_magic_defense = 5, base_mp = 2 WHERE name = '青铜盔';
UPDATE equipment_definitions SET base_magic_defense = 9, base_mp = 5 WHERE name = '精钢盔';
UPDATE equipment_definitions SET base_magic_defense = 15, base_mp = 8 WHERE name = '玄铁头盔';
UPDATE equipment_definitions SET base_magic_defense = 24, base_mp = 12 WHERE name = '天罡盔';
UPDATE equipment_definitions SET base_magic_defense = 39, base_mp = 20 WHERE name = '赤龙盔';

-- 衣甲：内功防御 = 60% 外功防御，内力 = 20% 生命
UPDATE equipment_definitions SET base_magic_defense = 3, base_mp = 2 WHERE name = '麻布衣';
UPDATE equipment_definitions SET base_magic_defense = 7, base_mp = 5 WHERE name = '皮甲';
UPDATE equipment_definitions SET base_magic_defense = 13, base_mp = 10 WHERE name = '锁子甲';
UPDATE equipment_definitions SET base_magic_defense = 21, base_mp = 16 WHERE name = '金丝软甲';
UPDATE equipment_definitions SET base_magic_defense = 33, base_mp = 24 WHERE name = '天蚕宝甲';
UPDATE equipment_definitions SET base_magic_defense = 54, base_mp = 40 WHERE name = '火凤宝衣';

-- 腰带：内功防御 = 40% 外功防御，新增生命，内力 = 30% 生命，少量速度
UPDATE equipment_definitions SET base_magic_defense = 1, base_hp = 5, base_mp = 2, base_speed = 1 WHERE name = '破旧腰带';
UPDATE equipment_definitions SET base_magic_defense = 2, base_hp = 10, base_mp = 3, base_speed = 2 WHERE name = '铁腰带';
UPDATE equipment_definitions SET base_magic_defense = 3, base_hp = 20, base_mp = 6, base_speed = 3 WHERE name = '虎皮带';
UPDATE equipment_definitions SET base_magic_defense = 5, base_hp = 30, base_mp = 9, base_speed = 4 WHERE name = '龙纹腰带';
UPDATE equipment_definitions SET base_magic_defense = 8, base_hp = 45, base_mp = 14, base_speed = 5 WHERE name = '蟠龙腰带';
UPDATE equipment_definitions SET base_magic_defense = 12, base_hp = 60, base_mp = 18, base_speed = 6 WHERE name = '朱雀腰带';

-- 靴子：内功防御 = 40% 外功防御，主加速度
UPDATE equipment_definitions SET base_magic_defense = 0, base_speed = 3 WHERE name = '草鞋';
UPDATE equipment_definitions SET base_magic_defense = 1, base_speed = 6 WHERE name = '布靴';
UPDATE equipment_definitions SET base_magic_defense = 2, base_speed = 10 WHERE name = '鹿皮靴';
UPDATE equipment_definitions SET base_magic_defense = 4, base_speed = 15 WHERE name = '追风靴';
UPDATE equipment_definitions SET base_magic_defense = 6, base_speed = 22 WHERE name = '踏云靴';
UPDATE equipment_definitions SET base_magic_defense = 9, base_speed = 30 WHERE name = '腾云靴';

-- 项链：内功攻击 = 80% 外功攻击，内功防御/内力/速度
UPDATE equipment_definitions SET base_magic_attack = 1, base_magic_defense = 2, base_mp = 10, base_speed = 1 WHERE name = '木项链';
UPDATE equipment_definitions SET base_magic_attack = 2, base_magic_defense = 4, base_mp = 20, base_speed = 2 WHERE name = '银项链';
UPDATE equipment_definitions SET base_magic_attack = 6, base_magic_defense = 6, base_mp = 40, base_speed = 3 WHERE name = '翡翠项链';
UPDATE equipment_definitions SET base_magic_attack = 12, base_magic_defense = 10, base_mp = 60, base_speed = 4 WHERE name = '玛瑙项链';
UPDATE equipment_definitions SET base_magic_attack = 20, base_magic_defense = 16, base_mp = 90, base_speed = 5 WHERE name = '血玉项链';
UPDATE equipment_definitions SET base_magic_attack = 32, base_magic_defense = 24, base_mp = 140, base_speed = 6 WHERE name = '凤鸣项链';
