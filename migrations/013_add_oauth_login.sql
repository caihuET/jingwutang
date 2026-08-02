-- 013: 微信/Google OAuth 登录字段
USE jingwutang;

SET @col_provider = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='users' AND COLUMN_NAME='oauth_provider');
SET @sql_provider = IF(@col_provider=0,
    'ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(16) NULL',
    'SELECT 1');
PREPARE stmt_provider FROM @sql_provider; EXECUTE stmt_provider; DEALLOCATE PREPARE stmt_provider;

SET @col_id = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='users' AND COLUMN_NAME='oauth_id');
SET @sql_id = IF(@col_id=0,
    'ALTER TABLE users ADD COLUMN oauth_id VARCHAR(64) NULL',
    'SELECT 1');
PREPARE stmt_id FROM @sql_id; EXECUTE stmt_id; DEALLOCATE PREPARE stmt_id;

SET @col_name = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='users' AND COLUMN_NAME='oauth_name');
SET @sql_name = IF(@col_name=0,
    'ALTER TABLE users ADD COLUMN oauth_name VARCHAR(32) NULL',
    'SELECT 1');
PREPARE stmt_name FROM @sql_name; EXECUTE stmt_name; DEALLOCATE PREPARE stmt_name;

SET @col_avatar = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='users' AND COLUMN_NAME='oauth_avatar');
SET @sql_avatar = IF(@col_avatar=0,
    'ALTER TABLE users ADD COLUMN oauth_avatar VARCHAR(512) NULL',
    'SELECT 1');
PREPARE stmt_avatar FROM @sql_avatar; EXECUTE stmt_avatar; DEALLOCATE PREPARE stmt_avatar;

SET @col_email = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='users' AND COLUMN_NAME='email');
SET @sql_email = IF(@col_email=0,
    'ALTER TABLE users ADD COLUMN email VARCHAR(128) NULL',
    'SELECT 1');
PREPARE stmt_email FROM @sql_email; EXECUTE stmt_email; DEALLOCATE PREPARE stmt_email;

SET @idx_oauth = (SELECT COUNT(*) FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA='jingwutang' AND TABLE_NAME='users' AND INDEX_NAME='uk_oauth');
SET @sql_idx = IF(@idx_oauth=0,
    'CREATE UNIQUE INDEX uk_oauth ON users (oauth_provider, oauth_id)',
    'SELECT 1');
PREPARE stmt_idx FROM @sql_idx; EXECUTE stmt_idx; DEALLOCATE PREPARE stmt_idx;
