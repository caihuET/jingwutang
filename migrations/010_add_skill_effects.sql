-- 迁移: 技能系统升级（杀伤距离 / 单群攻 / 附加效果）
-- 影响分析:
--   1. skill_definitions 新增 attack_range(1=近身 2=中程 3=远程)、aoe_targets(群攻目标数)
--   2. 新增 skill_effects 表，存储治疗/灼烧/中毒/buff/debuff 等效果
--   3. 更新 5 个群攻技能 target_type=2、aoe_targets=3
--   4. 按门派定位补齐 attack_range 与效果种子
-- 风险: 仅新增列/表/更新与插入，不删除数据；重复执行结果一致（幂等）

USE jingwutang;
SET NAMES utf8mb4;

-- 1. 新增列（不存在时才添加）
SET @col_range = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='skill_definitions' AND COLUMN_NAME='attack_range');
SET @sql_range = IF(@col_range = 0,
    'ALTER TABLE skill_definitions ADD COLUMN attack_range TINYINT DEFAULT 2 AFTER target_type',
    'SELECT 1');
PREPARE stmt_range FROM @sql_range; EXECUTE stmt_range; DEALLOCATE PREPARE stmt_range;

SET @col_aoe = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='skill_definitions' AND COLUMN_NAME='aoe_targets');
SET @sql_aoe = IF(@col_aoe = 0,
    'ALTER TABLE skill_definitions ADD COLUMN aoe_targets TINYINT DEFAULT 1 AFTER attack_range',
    'SELECT 1');
PREPARE stmt_aoe FROM @sql_aoe; EXECUTE stmt_aoe; DEALLOCATE PREPARE stmt_aoe;

-- 2. skill_effects 表
CREATE TABLE IF NOT EXISTS skill_effects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_id INT NOT NULL,
    effect_type VARCHAR(32) NOT NULL,
    base_value INT DEFAULT 0,
    value_per_level INT DEFAULT 0,
    duration INT DEFAULT 0,
    target_type TINYINT DEFAULT 1,
    sort_order INT DEFAULT 0,
    INDEX idx_skill (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 群攻技能
UPDATE skill_definitions SET target_type=2, aoe_targets=3
WHERE name IN ('真武七截阵','天女散花','天罗地网','天下无狗','圣火焚天');

-- 4. 杀伤距离（1=近身 2=中程 3=远程）
UPDATE skill_definitions SET attack_range=1
WHERE name IN ('罗汉拳','金钟罩','金刚指','达摩杖','易筋经','般若掌','龙爪手','易筋锻骨','九阴白骨爪','降龙掌','擒龙功','铜锤手','龙战于野','亢龙有悔','烈焰刀','七伤拳','大光明拳','乾坤大挪移','乾坤逆转');
UPDATE skill_definitions SET attack_range=2
WHERE name IN ('太极剑法','八卦掌','纯阳剑','真武七截阵','梯云纵','纯阳剑气','太乙玄门剑','紫霄神功','天女散花','飘雪穿云','慈航普渡','佛光普照','倚天剑法','九阳神功','回春术','迷魂散','打狗棒法','逍遥游','天下无狗','圣火令','圣火焚天','光明圣火令');
UPDATE skill_definitions SET attack_range=3
WHERE name IN ('暴雨梨花','毒影针','追心箭','机关术','万毒归宗','夺魂镖','天罗地网');

-- 5. 附加效果种子（幂等插入）
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'defense_up', 25, 0, 3, 2, 1 FROM skill_definitions sd WHERE sd.name='金钟罩'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='defense_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'defense_up', 10, 0, 2, 2, 1 FROM skill_definitions sd WHERE sd.name='达摩杖'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='defense_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'max_hp_up', 15, 0, 4, 2, 1 FROM skill_definitions sd WHERE sd.name='易筋经'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='max_hp_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'armor_penetration', 30, 0, 0, 1, 1 FROM skill_definitions sd WHERE sd.name='金刚指'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='armor_penetration');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'crit_up', 15, 0, 0, 2, 1 FROM skill_definitions sd WHERE sd.name='龙爪手'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='crit_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'max_hp_up', 20, 0, 5, 2, 1 FROM skill_definitions sd WHERE sd.name='易筋锻骨'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='max_hp_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'defense_up', 15, 0, 5, 2, 2 FROM skill_definitions sd WHERE sd.name='易筋锻骨'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='defense_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'dodge_up', 20, 0, 2, 2, 1 FROM skill_definitions sd WHERE sd.name='梯云纵'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='dodge_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'armor_penetration', 30, 0, 0, 1, 1 FROM skill_definitions sd WHERE sd.name='太乙玄门剑'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='armor_penetration');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'magic_attack_up', 20, 0, 5, 2, 1 FROM skill_definitions sd WHERE sd.name='紫霄神功'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='magic_attack_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'heal', 100, 12, 0, 2, 1 FROM skill_definitions sd WHERE sd.name='回春术'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='heal');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'heal', 180, 20, 0, 2, 1 FROM skill_definitions sd WHERE sd.name='慈航普渡'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='heal');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'shield', 40, 0, 2, 2, 2 FROM skill_definitions sd WHERE sd.name='慈航普渡'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='shield');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'crit_up', 10, 0, 0, 2, 1 FROM skill_definitions sd WHERE sd.name='九阴白骨爪'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='crit_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'heal_over_time', 10, 1, 3, 2, 1 FROM skill_definitions sd WHERE sd.name='佛光普照'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='heal_over_time');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'max_hp_up', 25, 0, 5, 2, 1 FROM skill_definitions sd WHERE sd.name='九阳神功'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='max_hp_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'defense_up', 20, 0, 5, 2, 2 FROM skill_definitions sd WHERE sd.name='九阳神功'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='defense_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'crit_up', 15, 0, 0, 2, 1 FROM skill_definitions sd WHERE sd.name='暴雨梨花'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='crit_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'poison', 8, 1, 1, 1, 1 FROM skill_definitions sd WHERE sd.name='毒影针'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='poison');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'guaranteed_hit', 0, 0, 0, 1, 1 FROM skill_definitions sd WHERE sd.name='追心箭'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='guaranteed_hit');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'poison', 10, 1, 3, 1, 1 FROM skill_definitions sd WHERE sd.name='机关术'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='poison');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'speed_down', 10, 0, 3, 1, 2 FROM skill_definitions sd WHERE sd.name='机关术'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='speed_down');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'dodge_down', 15, 0, 2, 1, 1 FROM skill_definitions sd WHERE sd.name='迷魂散'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='dodge_down');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'speed_down', 20, 0, 2, 1, 1 FROM skill_definitions sd WHERE sd.name='夺魂镖'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='speed_down');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'poison', 8, 1, 2, 1, 1 FROM skill_definitions sd WHERE sd.name='天罗地网'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='poison');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'poison', 15, 2, 3, 1, 1 FROM skill_definitions sd WHERE sd.name='万毒归宗'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='poison');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'defense_down', 10, 0, 3, 1, 2 FROM skill_definitions sd WHERE sd.name='万毒归宗'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='defense_down');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'speed_up', 15, 0, 3, 2, 1 FROM skill_definitions sd WHERE sd.name='逍遥游'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='speed_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'dodge_up', 10, 0, 3, 2, 2 FROM skill_definitions sd WHERE sd.name='逍遥游'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='dodge_up');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'lifesteal', 30, 0, 0, 2, 1 FROM skill_definitions sd WHERE sd.name='擒龙功'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='lifesteal');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'stack_damage', 10, 0, 0, 2, 1 FROM skill_definitions sd WHERE sd.name='龙战于野'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='stack_damage');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'defense_down', 20, 0, 2, 1, 1 FROM skill_definitions sd WHERE sd.name='亢龙有悔'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='defense_down');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'defense_down', 15, 0, 2, 1, 1 FROM skill_definitions sd WHERE sd.name='天下无狗'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='defense_down');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'burn', 5, 1, 1, 1, 1 FROM skill_definitions sd WHERE sd.name='圣火令'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='burn');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'reflect', 25, 0, 4, 2, 1 FROM skill_definitions sd WHERE sd.name='乾坤大挪移'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='reflect');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'backlash', 10, 0, 0, 2, 1 FROM skill_definitions sd WHERE sd.name='七伤拳'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='backlash');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'burn', 8, 1, 2, 1, 1 FROM skill_definitions sd WHERE sd.name='圣火焚天'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='burn');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'burn', 12, 2, 3, 1, 1 FROM skill_definitions sd WHERE sd.name='光明圣火令'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='burn');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'reflect', 35, 0, 5, 2, 1 FROM skill_definitions sd WHERE sd.name='乾坤逆转'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='reflect');
INSERT INTO skill_effects (skill_id, effect_type, base_value, value_per_level, duration, target_type, sort_order)
SELECT sd.id, 'undying', 0, 0, 5, 2, 2 FROM skill_definitions sd WHERE sd.name='乾坤逆转'
AND NOT EXISTS (SELECT 1 FROM skill_effects e WHERE e.skill_id=sd.id AND e.effect_type='undying');
