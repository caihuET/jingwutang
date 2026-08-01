-- 迁移: 任务系统重构（每日刷新 + 主线补齐 + 成就扩充 + 进度修复）
-- 影响分析:
--   1. player_tasks 新增 daily_reset_date，用于每日任务跨天重置
--   2. task_definitions 现有日常任务启用 daily_refresh；修正不可完成的任务
--   3. 新增主线/日常/成就任务定义
-- 风险: 仅新增列和任务行，不删数据；重复执行会重复插入任务，注意只执行一次

USE jingwutang;

ALTER TABLE player_tasks
    ADD COLUMN daily_reset_date DATE NULL AFTER completed_at;

-- 启用现有日常任务的每日重置
UPDATE task_definitions SET daily_refresh = 1 WHERE task_type = 2;

-- 修正/替换旧任务：竞技场未上线，替换为好友任务；补齐 28 级主线；金币任务改为历练
UPDATE task_definitions SET
    name = '以武会友',
    description = '添加 2 位好友',
    requirement_type = 'add_friend',
    requirement_value = 2,
    reward_exp = 1500, reward_gold = 600, reward_reputation = 10,
    min_level = 25, sort_order = 11, daily_refresh = 0
WHERE name = '竞技场初战';

UPDATE task_definitions SET
    name = '初露锋芒',
    description = '击败 5 次精英怪',
    requirement_type = 'kill_boss',
    requirement_value = 5,
    reward_exp = 1800, reward_gold = 800, reward_reputation = 0,
    min_level = 28, sort_order = 12, daily_refresh = 0
WHERE name = '广交好友';

UPDATE task_definitions SET
    name = '勤修苦练',
    description = '完成 5 次历练',
    requirement_type = 'pve_battle',
    requirement_value = 5,
    reward_exp = 600, reward_gold = 300, reward_reputation = 10,
    min_level = 1, sort_order = 2, daily_refresh = 1
WHERE name = '获取金币';

-- 同步已领取任务的目标值
UPDATE player_tasks pt
JOIN task_definitions td ON pt.task_id = td.id
SET pt.target = td.requirement_value,
    pt.progress = LEAST(pt.progress, td.requirement_value)
WHERE td.name IN ('以武会友', '初露锋芒', '勤修苦练');

-- 新增主线任务
INSERT INTO task_definitions (name, task_type, description, requirement_type, requirement_value, reward_exp, reward_gold, reward_reputation, min_level, sort_order, daily_refresh) VALUES
('小有所成', 1, '完成 8 次历练', 'pve_battle', 8, 900, 450, 0, 12, 13, 0),
('装备进阶', 1, '强化 5 次装备', 'enhance_equip', 5, 1200, 600, 0, 18, 14, 0),
('经脉初探', 1, '打通 2 个穴位', 'breakthrough', 2, 1400, 700, 0, 22, 15, 0),
('修为有成', 1, '打通 10 个穴位', 'breakthrough', 10, 2400, 1000, 0, 32, 16, 0),
('名动一方', 1, '完成 30 次历练', 'pve_battle', 30, 3000, 1200, 0, 38, 17, 0),
('威震江湖', 1, '达到 45 级', 'reach_level', 45, 5000, 2000, 80, 45, 18, 0),
('强者之路', 1, '击败 15 次精英怪', 'kill_boss', 15, 8000, 3000, 120, 50, 19, 0),
('绝顶高手', 1, '强化 30 次装备', 'enhance_equip', 30, 10000, 4000, 150, 55, 20, 0),
('一代宗师', 1, '达到 60 级', 'reach_level', 60, 20000, 8000, 500, 60, 21, 0);

-- 新增日常任务
INSERT INTO task_definitions (name, task_type, description, requirement_type, requirement_value, reward_exp, reward_gold, reward_reputation, min_level, sort_order, daily_refresh) VALUES
('斩妖除魔', 2, '击杀小怪 10 次', 'kill_monster', 10, 350, 180, 5, 1, 3, 1),
('装备焕新', 2, '穿戴 2 件装备', 'equip_item', 2, 250, 120, 0, 1, 6, 1);

-- 新增成就任务
INSERT INTO task_definitions (name, task_type, description, requirement_type, requirement_value, reward_exp, reward_gold, reward_reputation, min_level, sort_order, daily_refresh) VALUES
('强化达人', 4, '累计强化 50 次', 'enhance_equip', 50, 8000, 3000, 150, 1, 2, 0),
('装备收藏家', 4, '累计穿戴 30 件装备', 'equip_item', 30, 6000, 2500, 120, 1, 3, 0),
('经脉贯通', 4, '累计打通 30 个穴位', 'breakthrough', 30, 10000, 4000, 200, 1, 4, 0),
('好友遍天下', 4, '累计添加 10 位好友', 'add_friend', 10, 4000, 1500, 80, 1, 5, 0),
('经脉圆满1条', 4, '任意经脉圆满 1 条', 'meridian_complete', 1, 3000, 1200, 50, 1, 6, 0),
('经脉圆满2条', 4, '任意经脉圆满 2 条', 'meridian_complete', 2, 4000, 1600, 80, 1, 7, 0),
('经脉圆满3条', 4, '任意经脉圆满 3 条', 'meridian_complete', 3, 5000, 2000, 120, 1, 8, 0),
('经脉圆满4条', 4, '任意经脉圆满 4 条', 'meridian_complete', 4, 6000, 2500, 160, 1, 9, 0),
('经脉圆满5条', 4, '任意经脉圆满 5 条', 'meridian_complete', 5, 8000, 3000, 200, 1, 10, 0);
