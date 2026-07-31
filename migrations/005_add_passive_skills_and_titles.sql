-- 迁移: 被动技能 + 称号系统
-- 影响分析:
--   1. skill_definitions 新增 unlock_level 字段，并新增 6 个门派被动技能（skill_type=5，Lv.20 解锁）
--   2. players 新增 equipped_title_id 字段（当前佩戴称号）
--   3. task_definitions 新增 reward_title_id 字段（成就任务奖励称号）
--   4. 新增 title_definitions / player_titles 表及种子数据
--   5. 商城称号道具（item_type=4）与成就任务通过 title_id 关联发放
-- 风险: 全部为新增列/新增表/新增行，不修改或删除已有数据；重复执行结果一致（幂等）

USE jingwutang;

-- 1. skill_definitions 增加解锁等级字段（列不存在时才添加）
SET @col_skill = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='skill_definitions' AND COLUMN_NAME='unlock_level');
SET @sql_skill = IF(@col_skill = 0,
    'ALTER TABLE skill_definitions ADD COLUMN unlock_level INT DEFAULT 0 AFTER cooldown',
    'SELECT 1');
PREPARE stmt_skill FROM @sql_skill; EXECUTE stmt_skill; DEALLOCATE PREPARE stmt_skill;

-- 2. players 增加当前佩戴称号 ID（列不存在时才添加）
SET @col_title = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='players' AND COLUMN_NAME='equipped_title_id');
SET @sql_title = IF(@col_title = 0,
    'ALTER TABLE players ADD COLUMN equipped_title_id INT NULL AFTER title',
    'SELECT 1');
PREPARE stmt_title FROM @sql_title; EXECUTE stmt_title; DEALLOCATE PREPARE stmt_title;

-- 3. task_definitions 增加奖励称号 ID（列不存在时才添加）
SET @col_reward = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='task_definitions' AND COLUMN_NAME='reward_title_id');
SET @sql_reward = IF(@col_reward = 0,
    'ALTER TABLE task_definitions ADD COLUMN reward_title_id INT NULL AFTER reward_item_id',
    'SELECT 1');
PREPARE stmt_reward FROM @sql_reward; EXECUTE stmt_reward; DEALLOCATE PREPARE stmt_reward;

-- 4. 被动技能种子（skill_type=5，unlock_level=20）
INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, description)
SELECT '金刚不坏体', 1, 5, 0, 0, 0, 0, 0, 0, 10, 20, '常驻提升防御与生命上限'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='金刚不坏体' AND school_id=1);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, description)
SELECT '太极心法', 2, 5, 0, 0, 0, 0, 0, 0, 10, 20, '常驻提升内功攻击与内力上限'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='太极心法' AND school_id=2);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, description)
SELECT '慈航心经', 3, 5, 0, 0, 0, 0, 0, 0, 10, 20, '每回合回复少量生命'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='慈航心经' AND school_id=3);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, description)
SELECT '百毒不侵', 4, 5, 0, 0, 0, 0, 0, 0, 10, 20, '常驻提升暴击率与闪避率'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='百毒不侵' AND school_id=4);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, description)
SELECT '打狗心法', 5, 5, 0, 0, 0, 0, 0, 0, 10, 20, '常驻提升外功攻击并附带吸血'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='打狗心法' AND school_id=5);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, description)
SELECT '圣火护体', 6, 5, 0, 0, 0, 0, 0, 0, 10, 20, '受到伤害时反弹部分伤害'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='圣火护体' AND school_id=6);

-- 5. 称号定义表
CREATE TABLE IF NOT EXISTS title_definitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    title_level TINYINT DEFAULT 1,
    source_type TINYINT NOT NULL,
    source_id INT NULL,
    display_effect VARCHAR(32) DEFAULT 'none',
    description VARCHAR(128) DEFAULT '',
    sort_order INT DEFAULT 0,
    is_active TINYINT DEFAULT 1,
    INDEX idx_source (source_type, source_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 角色称号表
CREATE TABLE IF NOT EXISTS player_titles (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    player_id BIGINT UNSIGNED NOT NULL,
    title_id INT NOT NULL,
    obtained_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    is_equipped TINYINT DEFAULT 0,
    UNIQUE KEY uk_player_title (player_id, title_id),
    INDEX idx_player (player_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. 商城称号种子（source_type=1）
INSERT INTO title_definitions (name, title_level, source_type, source_id, display_effect, description, sort_order)
SELECT '武林至尊', 4, 1, si.id, 'marquee', '商城购买获得', 1
FROM shop_items si WHERE si.name='称号·武林至尊'
AND NOT EXISTS (SELECT 1 FROM title_definitions WHERE name='武林至尊');

INSERT INTO title_definitions (name, title_level, source_type, source_id, display_effect, description, sort_order)
SELECT '江湖侠客', 1, 1, si.id, 'none', '商城购买获得', 2
FROM shop_items si WHERE si.name='称号·江湖侠客'
AND NOT EXISTS (SELECT 1 FROM title_definitions WHERE name='江湖侠客');

-- 8. 成就称号种子（source_type=2，关联已有成就任务）
INSERT INTO title_definitions (name, title_level, source_type, source_id, display_effect, description, sort_order)
SELECT '百战勇士', 2, 2, td.id, 'glow', '累计战斗胜利 100 场', 3
FROM task_definitions td WHERE td.name='百战勇士'
AND NOT EXISTS (SELECT 1 FROM title_definitions WHERE name='百战勇士');

INSERT INTO title_definitions (name, title_level, source_type, source_id, display_effect, description, sort_order)
SELECT '千锤百炼', 2, 2, td.id, 'glow', '强化装备 50 次', 4
FROM task_definitions td WHERE td.name='千锤百炼'
AND NOT EXISTS (SELECT 1 FROM title_definitions WHERE name='千锤百炼');

INSERT INTO title_definitions (name, title_level, source_type, source_id, display_effect, description, sort_order)
SELECT '富甲一方', 3, 2, td.id, 'gradient', '累计获得 10 万金币', 5
FROM task_definitions td WHERE td.name='富甲一方'
AND NOT EXISTS (SELECT 1 FROM title_definitions WHERE name='富甲一方');

INSERT INTO title_definitions (name, title_level, source_type, source_id, display_effect, description, sort_order)
SELECT '武林高手', 4, 2, td.id, 'marquee', '等级达到 60 级', 6
FROM task_definitions td WHERE td.name='武林高手'
AND NOT EXISTS (SELECT 1 FROM title_definitions WHERE name='武林高手');

INSERT INTO title_definitions (name, title_level, source_type, source_id, display_effect, description, sort_order)
SELECT '六脉通达', 3, 2, td.id, 'gradient', '经脉全部打通', 7
FROM task_definitions td WHERE td.name='六脉通达'
AND NOT EXISTS (SELECT 1 FROM title_definitions WHERE name='六脉通达');

-- 9. 成就任务关联奖励称号
UPDATE task_definitions td
JOIN title_definitions t ON t.source_type=2 AND t.name=td.name
SET td.reward_title_id = t.id
WHERE td.task_type=4 AND td.reward_title_id IS NULL;

-- 10. 称号等级改为 1-4 四档尊贵等级（灰<绿<紫<金），已执行过旧版本的库在此校正
UPDATE title_definitions SET title_level = CASE
    WHEN name='江湖侠客' THEN 1
    WHEN name IN ('百战勇士','千锤百炼') THEN 2
    WHEN name IN ('富甲一方','六脉通达') THEN 3
    WHEN name IN ('武林至尊','武林高手') THEN 4
    ELSE title_level END;
