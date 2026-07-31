-- 迁移: 商城与社交系统
-- 影响分析:
--   1. players 表新增 guild_id / vip_until 列（帮派、VIP 功能）
--   2. 新增商城表: shop_items / player_items / shop_purchase_logs
--   3. 新增社交表: friend_relationships / chat_messages
--   4. 新增帮派表: guilds / guild_members
--   5. 商城种子数据 8 条
-- 风险: 可重复执行，重复执行不会产生重复数据

USE jingwutang;

-- 1. players 补充帮派与 VIP 字段（列不存在时才添加）
SET @col_guild = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='players' AND COLUMN_NAME='guild_id');
SET @sql1 = IF(@col_guild = 0, 'ALTER TABLE players ADD COLUMN guild_id BIGINT NULL', 'SELECT 1');
PREPARE stmt1 FROM @sql1; EXECUTE stmt1; DEALLOCATE PREPARE stmt1;

SET @col_vip = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='players' AND COLUMN_NAME='vip_until');
SET @sql2 = IF(@col_vip = 0, 'ALTER TABLE players ADD COLUMN vip_until DATETIME(6) NULL', 'SELECT 1');
PREPARE stmt2 FROM @sql2; EXECUTE stmt2; DEALLOCATE PREPARE stmt2;

-- 2. 商城商品表
CREATE TABLE IF NOT EXISTS shop_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    category INT NOT NULL,
    item_type INT NOT NULL,
    effect_value INT DEFAULT 0,
    price_type INT DEFAULT 1,
    price INT DEFAULT 0,
    daily_limit INT DEFAULT 0,
    description VARCHAR(128) DEFAULT '',
    sort_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS player_items (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    player_id BIGINT UNSIGNED NOT NULL,
    item_id INT NOT NULL,
    quantity INT DEFAULT 0,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_player (player_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS shop_purchase_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    player_id BIGINT UNSIGNED NOT NULL,
    item_id INT NOT NULL,
    quantity INT DEFAULT 1,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_player_item (player_id, item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 好友与聊天表
CREATE TABLE IF NOT EXISTS friend_relationships (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    player_id BIGINT UNSIGNED NOT NULL,
    friend_id BIGINT UNSIGNED NOT NULL,
    status TINYINT DEFAULT 0,
    last_gift_at DATETIME(6) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UNIQUE KEY uk_pair (player_id, friend_id),
    INDEX idx_player (player_id),
    INDEX idx_friend (friend_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    channel TINYINT NOT NULL,
    sender_id BIGINT UNSIGNED NOT NULL,
    receiver_id BIGINT UNSIGNED NULL,
    guild_id INT NULL,
    content VARCHAR(256) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_channel (channel, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 帮派表
CREATE TABLE IF NOT EXISTS guilds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(32) UNIQUE NOT NULL,
    leader_id BIGINT UNSIGNED NOT NULL,
    level INT DEFAULT 1,
    exp BIGINT DEFAULT 0,
    announcement VARCHAR(256) DEFAULT '',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS guild_members (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    guild_id INT NOT NULL,
    player_id BIGINT UNSIGNED NOT NULL,
    role TINYINT DEFAULT 5,
    contribution INT DEFAULT 0,
    joined_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UNIQUE KEY uk_guild_player (guild_id, player_id),
    INDEX idx_player (player_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 商城种子数据（表为空时插入，派生表列已显式命名避免 Duplicate column）
INSERT INTO shop_items (name, category, item_type, effect_value, price_type, price, daily_limit, description, sort_order)
SELECT name, category, item_type, effect_value, price_type, price, daily_limit, description, sort_order FROM (
    SELECT '体力药剂(小)' AS name, 1 AS category, 1 AS item_type, 30 AS effect_value, 1 AS price_type, 5 AS price, 3 AS daily_limit, '恢复 30 点体力' AS description, 1 AS sort_order
    UNION ALL SELECT '体力药剂(大)' AS name, 1 AS category, 1 AS item_type, 80 AS effect_value, 2 AS price_type, 1 AS price, 2 AS daily_limit, '恢复 80 点体力' AS description, 2 AS sort_order
    UNION ALL SELECT '经验加成券' AS name, 1 AS category, 2 AS item_type, 1000 AS effect_value, 1 AS price_type, 100 AS price, 5 AS daily_limit, '获得 1000 点经验' AS description, 3 AS sort_order
    UNION ALL SELECT '强化石' AS name, 2 AS category, 3 AS item_type, 1 AS effect_value, 2 AS price_type, 5 AS price, 0 AS daily_limit, '装备强化材料' AS description, 1 AS sort_order
    UNION ALL SELECT '称号·武林至尊' AS name, 3 AS category, 4 AS item_type, 0 AS effect_value, 2 AS price_type, 100 AS price, 0 AS daily_limit, '使用后获得称号' AS description, 1 AS sort_order
    UNION ALL SELECT '称号·江湖侠客' AS name, 3 AS category, 4 AS item_type, 0 AS effect_value, 2 AS price_type, 50 AS price, 0 AS daily_limit, '使用后获得称号' AS description, 2 AS sort_order
    UNION ALL SELECT 'VIP周卡' AS name, 4 AS category, 6 AS item_type, 7 AS effect_value, 2 AS price_type, 60 AS price, 0 AS daily_limit, '7 天 VIP' AS description, 1 AS sort_order
    UNION ALL SELECT 'VIP月卡' AS name, 4 AS category, 5 AS item_type, 30 AS effect_value, 2 AS price_type, 180 AS price, 0 AS daily_limit, '30 天 VIP' AS description, 2 AS sort_order
) AS seed
WHERE NOT EXISTS (SELECT 1 FROM shop_items LIMIT 1);
