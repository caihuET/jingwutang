-- 迁移: 帮派入帮申请审核
-- 影响分析:
--   1. 新增 guild_applications 表，不改动已有表结构，不删除列
--   2. 加入帮派改为先申请，帮主审核通过后才成为成员
-- 风险: 重复执行不会产生重复数据

USE jingwutang;

CREATE TABLE IF NOT EXISTS guild_applications (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    guild_id INT NOT NULL,
    player_id BIGINT UNSIGNED NOT NULL,
    status TINYINT DEFAULT 0,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_guild_status (guild_id, status),
    INDEX idx_player (player_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
