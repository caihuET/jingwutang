"""任务定义与迁移一致性单元测试"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.service.task_service import REQ_TYPES


BASE_DIR = os.path.join(os.path.dirname(__file__), "..")


def load_sql(name: str) -> str:
    """读取迁移 SQL 文件"""
    with open(os.path.join(BASE_DIR, "migrations", name), encoding="utf-8") as f:
        return f.read()


def parse_task_rows(sql_text: str) -> list:
    """解析 INSERT INTO task_definitions 的所有任务行"""
    rows = []
    for m in re.finditer(
        r"INSERT INTO task_definitions\s*\(([^)]*)\)\s*VALUES\s*(.*?);",
        sql_text, re.S,
    ):
        cols = [c.strip() for c in m.group(1).split(",")]
        has_daily = "daily_refresh" in cols
        pattern = (
            r"\(\s*'([^']+)',\s*(\d+),\s*'([^']*)',\s*'([^']+)',"
            r"\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)"
        )
        if has_daily:
            pattern += r",\s*(\d+)"
        for row in re.finditer(pattern, m.group(2)):
            name, task_type, _desc, req_type = row.group(1), int(row.group(2)), row.group(3), row.group(4)
            rows.append({
                "name": name,
                "task_type": task_type,
                "requirement_type": req_type,
                "requirement_value": int(row.group(5)),
                "min_level": int(row.group(9)),
                "daily_refresh": int(row.group(11)) if has_daily else 0,
            })
    return rows


def apply_task_updates(rows: list, sql_text: str) -> list:
    """模拟 init.sql 中 UPDATE 后的最终任务状态"""
    row_map = {r["name"]: dict(r) for r in rows}
    if "UPDATE task_definitions SET daily_refresh = 1 WHERE task_type = 2" in sql_text:
        for row in row_map.values():
            if row["task_type"] == 2:
                row["daily_refresh"] = 1
    pattern = (
        r"UPDATE task_definitions SET\s+name = '([^']+)',\s+description = '[^']*',"
        r"\s+requirement_type = '([^']+)',\s+requirement_value = (\d+),"
        r"\s+reward_exp = \d+, reward_gold = \d+, reward_reputation = \d+,"
        r"\s+min_level = (\d+), sort_order = \d+, daily_refresh = (\d+)"
        r"\s+WHERE name = '([^']+)';"
    )
    for m in re.finditer(pattern, sql_text, re.S):
        new_name, req_type, req_value, min_level, daily, old_name = m.groups()
        if old_name in row_map:
            row_map[old_name].update({
                "name": new_name,
                "requirement_type": req_type,
                "requirement_value": int(req_value),
                "min_level": int(min_level),
                "daily_refresh": int(daily),
            })
    return list(row_map.values())


class TestTaskDefinitions(unittest.TestCase):
    """任务种子数据校验"""

    def setUp(self):
        sql_text = load_sql("init.sql")
        self.rows = apply_task_updates(parse_task_rows(sql_text), sql_text)

    def test_req_types_include_new_hooks(self):
        self.assertIn("meridian_complete", REQ_TYPES)
        self.assertIn("kill_monster", REQ_TYPES)

    def test_all_requirement_types_supported(self):
        for row in self.rows:
            self.assertIn(row["requirement_type"], REQ_TYPES, row["name"])

    def test_no_duplicate_names(self):
        names = [r["name"] for r in self.rows]
        self.assertEqual(len(names), len(set(names)))

    def test_main_quest_level_coverage(self):
        main_rows = [r for r in self.rows if r["task_type"] == 1]
        levels = {r["min_level"] for r in main_rows}
        expected = {1, 5, 10, 12, 15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 40, 45, 50, 55, 60}
        self.assertTrue(expected.issubset(levels))
        self.assertGreaterEqual(len(main_rows), 21)

    def test_daily_tasks_refresh(self):
        daily_rows = [r for r in self.rows if r["task_type"] == 2]
        self.assertGreaterEqual(len(daily_rows), 7)
        for row in daily_rows:
            self.assertEqual(row["daily_refresh"], 1, row["name"])

    def test_meridian_achievements(self):
        meridian_rows = [
            r for r in self.rows
            if r["task_type"] == 4 and r["requirement_type"] == "meridian_complete"
        ]
        values = sorted(r["requirement_value"] for r in meridian_rows)
        self.assertEqual(values, [1, 2, 3, 4, 5])

    def test_total_counts(self):
        main_rows = [r for r in self.rows if r["task_type"] == 1]
        daily_rows = [r for r in self.rows if r["task_type"] == 2]
        ach_rows = [r for r in self.rows if r["task_type"] == 4]
        self.assertEqual(len(main_rows), 21)
        self.assertEqual(len(daily_rows), 7)
        self.assertEqual(len(ach_rows), 14)


class TestMigration009(unittest.TestCase):
    """迁移 009 新增任务校验"""

    def setUp(self):
        self.rows = parse_task_rows(load_sql("009_add_task_system.sql"))

    def test_new_inserts_only(self):
        main_new = [r for r in self.rows if r["task_type"] == 1]
        daily_new = [r for r in self.rows if r["task_type"] == 2]
        ach_new = [r for r in self.rows if r["task_type"] == 4]
        self.assertEqual(len(main_new), 9)
        self.assertEqual(len(daily_new), 2)
        self.assertEqual(len(ach_new), 9)

    def test_new_requirement_types_supported(self):
        for row in self.rows:
            self.assertIn(row["requirement_type"], REQ_TYPES, row["name"])

    def test_has_daily_reset_column(self):
        sql_text = load_sql("009_add_task_system.sql")
        self.assertIn("daily_reset_date DATE NULL", sql_text)
        self.assertIn("daily_refresh = 1 WHERE task_type = 2", sql_text)


if __name__ == "__main__":
    unittest.main()
