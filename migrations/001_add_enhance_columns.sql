-- 迁移: 补充 player_equipment 表缺少的强化字段
-- 影响分析: 新增 3 列，默认值 0，不影响现有数据

ALTER TABLE player_equipment
    ADD COLUMN enhance_attack INT DEFAULT 0 AFTER enhance_level,
    ADD COLUMN enhance_defense INT DEFAULT 0 AFTER enhance_attack,
    ADD COLUMN enhance_hp INT DEFAULT 0 AFTER enhance_defense;
