-- 迁移: 清理跨门派技能学习记录
-- 原因: 011 补发中阶技能时未按门派过滤，所有玩家误学了其他门派技能
-- 影响: 删除 player_skills 中 school_id 与玩家门派不一致的非通用技能记录；
--       保留本门派技能与通用技能（school_id IS NULL 的技能）
-- 风险: 仅删除误学记录，幂等，重复执行无副作用

USE jingwutang;
SET NAMES utf8mb4;

DELETE ps FROM player_skills ps
JOIN skill_definitions sd ON sd.id = ps.skill_id
JOIN players p ON p.id = ps.player_id
WHERE sd.school_id IS NOT NULL
  AND p.school_id IS NOT NULL
  AND sd.school_id <> p.school_id;
