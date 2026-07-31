-- 迁移: 调整商城商品价格
-- 影响分析: 仅更新 4 个商品的 price / price_type，不删除数据；重复执行结果一致（幂等）
-- 调整后:
--   体力药剂(小): 5 金币
--   体力药剂(大): 1 元宝
--   经验加成券: 100 金币
--   强化石: 5 元宝

USE jingwutang;

SET NAMES utf8mb4;

UPDATE shop_items SET price = 5, price_type = 1 WHERE name = '体力药剂(小)';
UPDATE shop_items SET price = 1, price_type = 2 WHERE name = '体力药剂(大)';
UPDATE shop_items SET price = 100, price_type = 1 WHERE name = '经验加成券';
UPDATE shop_items SET price = 5, price_type = 2 WHERE name = '强化石';
