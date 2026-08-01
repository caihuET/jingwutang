-- 迁移: 补齐服务器缺失的 18 个门派中阶技能（每门派第 3/4/5 个技能）
-- 原因: 服务器 skill_definitions 由旧版种子初始化，仅含 12 个基础技能 + 18 个高阶技能；
--       缺少金刚指/达摩杖/易筋经 等 18 个中阶技能，导致技能页与效果表不完整
-- 影响: 新增 18 行 skill_definitions（按名称幂等），并为所有玩家补发 player_skills
-- 风险: 仅新增数据，不修改/删除已有数据；重复执行结果一致（幂等）

USE jingwutang;
SET NAMES utf8mb4;

-- 少林
INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '金刚指', 1, 2, 1, 200, 18, 20, 1, 1, 10, 5, 1, 1, '少林点穴绝技，无视部分防御'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='金刚指' AND school_id=1);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '达摩杖', 1, 2, 1, 170, 15, 16, 0, 1, 10, 10, 1, 1, '达摩祖师所传杖法，攻守兼备'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='达摩杖' AND school_id=1);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '易筋经', 1, 4, 0, 0, 0, 25, 4, 1, 10, 15, 1, 1, '少林至宝，大幅提升生命上限'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='易筋经' AND school_id=1);

-- 武当
INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '纯阳剑', 2, 2, 1, 220, 20, 20, 1, 1, 10, 5, 2, 1, '纯阳无极剑法，伤害极高'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='纯阳剑' AND school_id=2);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '真武七截阵', 2, 3, 2, 250, 22, 30, 2, 2, 10, 10, 2, 3, '武当镇派绝技，范围内功攻击'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='真武七截阵' AND school_id=2);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '梯云纵', 2, 4, 0, 0, 0, 15, 2, 1, 10, 15, 2, 1, '武当轻功绝学，提升闪避'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='梯云纵' AND school_id=2);

-- 峨眉
INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '慈航普渡', 3, 4, 0, 0, 0, 30, 4, 1, 10, 5, 2, 1, '峨眉至高心法，大量恢复生命'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='慈航普渡' AND school_id=3);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '九阴白骨爪', 3, 2, 1, 210, 19, 18, 1, 1, 10, 10, 2, 1, '九阴真经武功，外功伤害'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='九阴白骨爪' AND school_id=3);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '飘雪穿云', 3, 3, 2, 190, 17, 20, 1, 1, 10, 15, 2, 1, '峨眉高级内功，造成内功伤害'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='飘雪穿云' AND school_id=3);

-- 唐门
INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '追心箭', 4, 2, 1, 230, 21, 22, 1, 1, 10, 5, 3, 1, '唐门追魂箭法，必中目标'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='追心箭' AND school_id=4);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '机关术', 4, 4, 0, 0, 0, 20, 3, 1, 10, 10, 3, 1, '布设机关陷阱，持续伤害敌人'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='机关术' AND school_id=4);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '迷魂散', 4, 3, 2, 170, 16, 18, 1, 1, 10, 15, 2, 1, '毒粉攻击，降低敌人命中'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='迷魂散' AND school_id=4);

-- 丐帮
INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '逍遥游', 5, 4, 0, 0, 0, 20, 3, 1, 10, 5, 2, 1, '丐帮身法绝技，提升速度和闪避'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='逍遥游' AND school_id=5);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '擒龙功', 5, 2, 1, 200, 18, 18, 1, 1, 10, 10, 1, 1, '擒龙控鹤，造成外功伤害并吸血'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='擒龙功' AND school_id=5);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '铜锤手', 5, 2, 1, 180, 16, 14, 0, 1, 10, 15, 1, 1, '丐帮硬功，造成外功伤害'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='铜锤手' AND school_id=5);

-- 明教
INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '乾坤大挪移', 6, 4, 0, 0, 0, 30, 4, 1, 10, 5, 1, 1, '明教至高心法，反弹部分伤害'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='乾坤大挪移' AND school_id=6);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '七伤拳', 6, 2, 1, 260, 24, 25, 2, 1, 10, 10, 1, 1, '先伤己再伤敌，造成巨额外功伤害'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='七伤拳' AND school_id=6);

INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, target_type, max_level, unlock_level, attack_range, aoe_targets, description)
SELECT '大光明拳', 6, 2, 1, 200, 19, 18, 1, 1, 10, 15, 1, 1, '圣火令神功，造成外功伤害'
WHERE NOT EXISTS (SELECT 1 FROM skill_definitions WHERE name='大光明拳' AND school_id=6);

-- 为所有玩家补发缺失技能（已学习的跳过）
INSERT INTO player_skills (player_id, skill_id, level, proficiency, slot_position, is_learned)
SELECT p.id, sd.id, 1, 0, NULL, 1
FROM players p
CROSS JOIN skill_definitions sd
WHERE sd.name IN ('金刚指','达摩杖','易筋经','纯阳剑','真武七截阵','梯云纵','慈航普渡','九阴白骨爪','飘雪穿云','追心箭','机关术','迷魂散','逍遥游','擒龙功','铜锤手','乾坤大挪移','七伤拳','大光明拳')
AND NOT EXISTS (
    SELECT 1 FROM player_skills ps
    WHERE ps.player_id = p.id AND ps.skill_id = sd.id
);
