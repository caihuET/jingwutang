-- 迁移: 修复 skill_definitions 名称乱码与缺失
-- 原因: mysql 客户端连接字符集非 utf8mb4，导致中文被丢弃
-- 影响: 仅更新 name / description 两列，重复执行结果一致

SET NAMES utf8mb4;

USE jingwutang;

UPDATE skill_definitions SET name = '罗汉拳', description = '少林入门拳法，造成外功伤害' WHERE id = 1;
UPDATE skill_definitions SET name = '金钟罩', description = '提升自身防御，持续3回合' WHERE id = 2;
UPDATE skill_definitions SET name = '太极剑法', description = '武当基础剑法，造成外功伤害' WHERE id = 3;
UPDATE skill_definitions SET name = '八卦掌', description = '以柔克刚，造成内功伤害' WHERE id = 4;
UPDATE skill_definitions SET name = '回春术', description = '恢复己方生命值' WHERE id = 5;
UPDATE skill_definitions SET name = '天女散花', description = '内功攻击，造成范围伤害' WHERE id = 6;
UPDATE skill_definitions SET name = '暴雨梨花', description = '唐门暗器绝技，暴击率提升' WHERE id = 7;
UPDATE skill_definitions SET name = '毒影针', description = '淬毒飞针，造成内功伤害' WHERE id = 8;
UPDATE skill_definitions SET name = '降龙掌', description = '丐帮绝学，造成大量外功伤害' WHERE id = 9;
UPDATE skill_definitions SET name = '打狗棒法', description = '丐帮基础棒法' WHERE id = 10;
UPDATE skill_definitions SET name = '烈焰刀', description = '明教刀法，造成大量外功伤害' WHERE id = 11;
UPDATE skill_definitions SET name = '圣火令', description = '明教内功，造成内功伤害' WHERE id = 12;
UPDATE skill_definitions SET name = '般若掌', description = '少林高阶掌法，蕴含佛门罡气' WHERE id = 13;
UPDATE skill_definitions SET name = '龙爪手', description = '少林绝技，擒拿撕裂造成重创' WHERE id = 14;
UPDATE skill_definitions SET name = '易筋锻骨', description = '易筋经深层功法，大幅强化体质' WHERE id = 15;
UPDATE skill_definitions SET name = '纯阳剑气', description = '纯阳内劲化为剑气，内功伤害' WHERE id = 16;
UPDATE skill_definitions SET name = '太乙玄门剑', description = '武当剑法巅峰，外功贯穿伤害' WHERE id = 17;
UPDATE skill_definitions SET name = '紫霄神功', description = '紫霄宫心法，大幅提升内功修为' WHERE id = 18;
UPDATE skill_definitions SET name = '佛光普照', description = '峨眉佛门心法，持续恢复生命' WHERE id = 19;
UPDATE skill_definitions SET name = '倚天剑法', description = '倚天剑法，凌厉无比的外功伤害' WHERE id = 20;
UPDATE skill_definitions SET name = '九阳神功', description = '至阳内功，大幅提升生命和防御' WHERE id = 21;
UPDATE skill_definitions SET name = '夺魂镖', description = '唐门夺命飞镖，外功伤害并减速' WHERE id = 22;
UPDATE skill_definitions SET name = '天罗地网', description = '天罗地网，范围毒雾内功伤害' WHERE id = 23;
UPDATE skill_definitions SET name = '万毒归宗', description = '万毒归一，使敌人持续中毒' WHERE id = 24;
UPDATE skill_definitions SET name = '龙战于野', description = '降龙掌法，愈战愈勇造成外功伤害' WHERE id = 25;
UPDATE skill_definitions SET name = '亢龙有悔', description = '降龙十八掌至强一式，巨额伤害' WHERE id = 26;
UPDATE skill_definitions SET name = '天下无狗', description = '打狗棒法绝招，横扫造成内功伤害' WHERE id = 27;
UPDATE skill_definitions SET name = '圣火焚天', description = '圣火令内功，烈焰焚天内功伤害' WHERE id = 28;
UPDATE skill_definitions SET name = '光明圣火令', description = '圣火令至高武功，灼烧内功伤害' WHERE id = 29;
UPDATE skill_definitions SET name = '乾坤逆转', description = '乾坤大挪移化境，反弹部分伤害' WHERE id = 30;
