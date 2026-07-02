-- 精武堂 数据库初始化脚本
CREATE DATABASE IF NOT EXISTS jingwutang CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE jingwutang;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(32) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    register_ip VARCHAR(45) NOT NULL,
    status TINYINT DEFAULT 1,
    last_login_at DATETIME(6) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX idx_username (username),
    INDEX idx_register_ip (register_ip)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS schools (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(16) NOT NULL UNIQUE,
    description TEXT NULL,
    base_strength INT DEFAULT 5,
    base_agility INT DEFAULT 5,
    base_constitution INT DEFAULT 5,
    base_spirit INT DEFAULT 5,
    growth_type VARCHAR(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO schools (id, name, description, base_strength, base_agility, base_constitution, base_spirit, growth_type) VALUES
(1, '少林', '外防血肉之盾', 8, 4, 10, 5, 'tank'),
(2, '武当', '内功续航宗师', 5, 6, 6, 10, 'dps'),
(3, '峨眉', '治疗辅助圣手', 4, 5, 8, 8, 'healer'),
(4, '唐门', '外功暴击刺客', 7, 10, 4, 5, 'assassin'),
(5, '丐帮', '均衡持续作战', 6, 7, 7, 6, 'balanced'),
(6, '明教', '暴力输出狂战', 10, 6, 6, 4, 'dps');

CREATE TABLE IF NOT EXISTS players (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL UNIQUE,
    name VARCHAR(32) NOT NULL UNIQUE,
    gender TINYINT NOT NULL,
    school_id INT NOT NULL,
    level INT DEFAULT 1,
    exp BIGINT DEFAULT 0,
    guild_id BIGINT UNSIGNED NULL,
    hp INT NOT NULL,
    max_hp INT NOT NULL,
    mp INT NOT NULL,
    max_mp INT NOT NULL,
    stamina INT DEFAULT 100,
    gold BIGINT DEFAULT 0,
    ingot INT DEFAULT 0,
    reputation INT DEFAULT 0,
    combat_power INT DEFAULT 0,
    title VARCHAR(64) NULL,
    free_points INT DEFAULT 0,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX idx_user_id (user_id),
    INDEX idx_name (name),
    INDEX idx_level (level),
    INDEX idx_combat_power (combat_power),
    INDEX idx_school (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS player_attributes (
    player_id BIGINT UNSIGNED PRIMARY KEY,
    strength INT DEFAULT 10,
    agility INT DEFAULT 10,
    constitution INT DEFAULT 10,
    spirit INT DEFAULT 10,
    extra_attack INT DEFAULT 0,
    extra_defense INT DEFAULT 0,
    extra_magic_attack INT DEFAULT 0,
    extra_magic_defense INT DEFAULT 0,
    extra_hp INT DEFAULT 0,
    extra_mp INT DEFAULT 0,
    extra_speed INT DEFAULT 0,
    extra_crit_rate DECIMAL(5,2) DEFAULT 0,
    extra_dodge_rate DECIMAL(5,2) DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS skill_definitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    school_id INT NULL,
    skill_type TINYINT NOT NULL,
    damage_type TINYINT NOT NULL,
    base_damage INT DEFAULT 0,
    damage_per_level INT DEFAULT 0,
    mp_cost INT DEFAULT 0,
    mp_cost_per_level INT DEFAULT 0,
    cooldown INT DEFAULT 0,
    target_type TINYINT DEFAULT 1,
    max_level INT DEFAULT 10,
    description VARCHAR(256) NOT NULL,
    INDEX idx_school (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS player_skills (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    player_id BIGINT UNSIGNED NOT NULL,
    skill_id INT NOT NULL,
    level INT DEFAULT 1,
    proficiency INT DEFAULT 0,
    slot_position TINYINT NULL,
    is_learned TINYINT DEFAULT 1,
    UNIQUE KEY uk_player_skill (player_id, skill_id),
    INDEX idx_player (player_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS equipment_definitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    slot TINYINT NOT NULL,
    quality TINYINT NOT NULL,
    level_required INT DEFAULT 1,
    base_attack INT DEFAULT 0,
    base_defense INT DEFAULT 0,
    base_magic_attack INT DEFAULT 0,
    base_magic_defense INT DEFAULT 0,
    base_hp INT DEFAULT 0,
    base_speed INT DEFAULT 0,
    max_gem_slots TINYINT DEFAULT 0,
    is_sellable TINYINT DEFAULT 1,
    sell_price INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS player_equipment (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    player_id BIGINT UNSIGNED NOT NULL,
    equip_def_id INT NOT NULL,
    slot TINYINT NOT NULL,
    quality TINYINT NOT NULL,
    is_equipped TINYINT DEFAULT 0,
    enhance_level INT DEFAULT 0,
    enhance_attack INT DEFAULT 0,
    enhance_defense INT DEFAULT 0,
    enhance_hp INT DEFAULT 0,
    durability INT DEFAULT 100,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_player (player_id),
    INDEX idx_player_equip (player_id, slot)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 初始门派技能
INSERT INTO skill_definitions (name, school_id, skill_type, damage_type, base_damage, damage_per_level, mp_cost, cooldown, description) VALUES
('罗汉拳', 1, 2, 1, 130, 12, 12, 0, '少林入门拳法，造成外功伤害'),
('金钟罩', 1, 4, 0, 0, 0, 20, 3, '提升自身防御，持续2回合'),
('太和剑法', 2, 2, 1, 150, 15, 15, 0, '武当基础剑法，造成外功伤害'),
('八卦掌', 2, 3, 2, 180, 18, 25, 1, '以柔克刚，造成内功伤害'),
('回春术', 3, 4, 0, 0, 0, 20, 2, '恢复己方生命值'),
('天女散花', 3, 3, 2, 160, 16, 22, 1, '内功攻击，造成范围伤害'),
('暴雨梨花', 4, 2, 1, 170, 17, 18, 1, '唐门暗器绝技，暴击率提升'),
('毒影针', 4, 3, 2, 140, 14, 15, 0, '淬毒飞针，造成内功伤害'),
('降龙掌', 5, 2, 1, 190, 19, 22, 1, '丐帮绝学，造成大量外功伤害'),
('打狗棒法', 5, 2, 1, 140, 14, 12, 0, '丐帮基础棒法'),
('烈焰刀', 6, 2, 1, 185, 18, 20, 1, '明教刀法，造成大量外功伤害'),
('圣火令', 6, 3, 2, 175, 17, 20, 1, '明教内功，造成内功伤害');

-- 任务定义
CREATE TABLE IF NOT EXISTS task_definitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    task_type TINYINT NOT NULL,
    description TEXT NULL,
    requirement_type VARCHAR(32) NOT NULL,
    requirement_value INT NOT NULL,
    reward_exp INT DEFAULT 0,
    reward_gold INT DEFAULT 0,
    reward_reputation INT DEFAULT 0,
    reward_item_id INT NULL,
    daily_refresh TINYINT DEFAULT 0,
    min_level INT DEFAULT 1,
    max_level INT NULL,
    sort_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 角色任务
CREATE TABLE IF NOT EXISTS player_tasks (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    player_id BIGINT UNSIGNED NOT NULL,
    task_id INT NOT NULL,
    progress INT DEFAULT 0,
    target INT NOT NULL,
    status TINYINT DEFAULT 0,
    completed_at DATETIME(6) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_player_task (player_id, task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 战斗日志
CREATE TABLE IF NOT EXISTS battle_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    attacker_id BIGINT UNSIGNED NOT NULL,
    defender_id BIGINT NULL,
    battle_type TINYINT NOT NULL,
    result TINYINT NOT NULL,
    rounds INT NOT NULL,
    log_detail JSON NULL,
    drop_exp INT DEFAULT 0,
    drop_gold INT DEFAULT 0,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_attacker (attacker_id),
    INDEX idx_battle_type (battle_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 初始任务
INSERT INTO task_definitions (name, task_type, description, requirement_type, requirement_value, reward_exp, reward_gold, reward_reputation, min_level, sort_order) VALUES
('初入江湖', 1, '在青云山击败 5 个山贼', 'kill_monster', 5, 200, 100, 10, 1, 1),
('小试牛刀', 1, '击败山寇首领', 'kill_boss', 1, 500, 200, 30, 5, 2),
('第一次历练', 1, '完成 3 次历练', 'pve_battle', 3, 400, 200, 0, 5, 3),
('装备入门', 1, '穿戴 2 件装备', 'equip_item', 2, 600, 300, 0, 10, 4),
('强化初探', 1, '强化 1 次装备', 'enhance_equip', 1, 500, 250, 0, 10, 5),
('技能领悟', 1, '配置 1 个出战技能', 'skill_level', 1, 800, 400, 0, 15, 6),
('击败山贼头目', 1, '击败 3 次精英怪', 'kill_boss', 3, 1000, 500, 0, 20, 7),
('修为小成', 1, '经脉打通 5 个穴位', 'breakthrough', 5, 2000, 800, 0, 30, 8),
('竞技场初战', 1, '参与 1 次竞技场', 'arena_battle', 1, 1500, 600, 10, 25, 9),
('广交好友', 1, '添加 3 位好友', 'add_friend', 3, 1000, 500, 20, 30, 10),
('高手之路', 1, '达到 40 级', 'reach_level', 40, 2500, 1000, 30, 35, 11),
('扬名立万', 1, '加入帮派', 'join_guild', 1, 3000, 1200, 50, 40, 12),
('每日历练', 2, '完成 3 次历练', 'pve_battle', 3, 300, 150, 0, 1, 1),
('击败强敌', 2, '击败精英怪 2 次', 'kill_boss', 2, 400, 200, 10, 1, 2),
('装备强化', 2, '强化装备 1 次', 'enhance_equip', 1, 0, 0, 20, 1, 3),
('获取金币', 2, '获得 500 金币', 'reach_level', 500, 200, 0, 5, 1, 4),
('经脉修炼', 2, '打通穴位 1 个', 'breakthrough', 1, 500, 100, 15, 1, 5),
('百战勇士', 4, '累计战斗胜利 100 场', 'pve_battle', 100, 5000, 2000, 100, 1, 1),
('千锤百炼', 4, '强化装备 50 次', 'enhance_equip', 50, 3000, 0, 0, 1, 2),
('富甲一方', 4, '累计获得 10 万金币', 'reach_level', 100000, 0, 10000, 0, 1, 3),
('武林高手', 4, '等级达到 60 级', 'reach_level', 60, 10000, 5000, 200, 1, 4),
('六脉通达', 4, '经脉全部打通', 'breakthrough', 20, 8000, 0, 500, 1, 5);

