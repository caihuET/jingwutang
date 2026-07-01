"""API 集成测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from fastapi.testclient import TestClient
from app import app


class TestHealthAPI(unittest.TestCase):
    """健康检查"""

    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["status"], "ok")


class TestAuthAPI(unittest.TestCase):
    """认证接口测试"""

    def setUp(self):
        self.client = TestClient(app)

    def test_login_missing_fields(self):
        resp = self.client.post("/api/v1/auth/login", json={"username": "", "password": ""})
        data = resp.json()
        self.assertIn("code", data)

    def test_login_empty_request(self):
        resp = self.client.post("/api/v1/auth/login", json={})
        self.assertEqual(resp.status_code, 422)

    def test_register_empty_request(self):
        resp = self.client.post("/api/v1/auth/register", json={})
        self.assertEqual(resp.status_code, 422)


class TestBattleAPI(unittest.TestCase):
    """战斗接口测试"""

    def setUp(self):
        self.client = TestClient(app)

    def test_battle_missing_map(self):
        resp = self.client.post("/api/v1/battle/pve", json={"map_id": 999})
        data = resp.json()
        self.assertIn("code", data)

    def test_battle_invalid_params(self):
        resp = self.client.post("/api/v1/battle/pve", json={"map_id": "abc"})
        self.assertEqual(resp.status_code, 422)


class TestEquipmentAPI(unittest.TestCase):
    """装备接口测试"""

    def setUp(self):
        self.client = TestClient(app)

    def test_equip_invalid_id(self):
        resp = self.client.post("/api/v1/equipment/equip", json={"equip_id": 99999})
        data = resp.json()
        self.assertIn("code", data)

    def test_unequip_invalid_id(self):
        resp = self.client.post("/api/v1/equipment/unequip", json={"equip_id": 99999})
        data = resp.json()
        self.assertIn("code", data)

    def test_enhance_invalid_id(self):
        resp = self.client.post("/api/v1/equipment/enhance", json={"equip_id": 99999})
        data = resp.json()
        self.assertIn("code", data)


class TestSkillAPI(unittest.TestCase):
    """技能接口测试"""

    def setUp(self):
        self.client = TestClient(app)

    def test_skill_list(self):
        resp = self.client.get("/api/v1/skill/list?player_id=1")
        data = resp.json()
        self.assertIn("code", data)

    def test_set_slots_too_many(self):
        resp = self.client.post("/api/v1/skill/slot", json={"skill_ids": [1, 2, 3, 4, 5, 6]})
        data = resp.json()
        self.assertIn("code", data)


class TestTaskAPI(unittest.TestCase):
    """任务接口测试"""

    def setUp(self):
        self.client = TestClient(app)

    def test_task_list(self):
        resp = self.client.get("/api/v1/task/list?player_id=1")
        data = resp.json()
        self.assertIn("code", data)

    def test_task_list_filtered(self):
        resp = self.client.get("/api/v1/task/list?player_id=1&task_type=1")
        data = resp.json()
        self.assertIn("code", data)

    def test_claim_invalid_task(self):
        resp = self.client.post("/api/v1/task/claim", json={"task_id": 99999})
        data = resp.json()
        self.assertIn("code", data)


class TestPlayerAPI(unittest.TestCase):
    """角色接口测试"""

    def setUp(self):
        self.client = TestClient(app)

    def test_player_info_missing_param(self):
        resp = self.client.get("/api/v1/player/info")
        self.assertEqual(resp.status_code, 422)

    def test_player_info_nonexistent(self):
        resp = self.client.get("/api/v1/player/info?player_id=99999")
        data = resp.json()
        self.assertIn("code", data)

    def test_create_player_missing_name(self):
        resp = self.client.post("/api/v1/player/create", json={"gender": 1, "school_id": 1})
        self.assertEqual(resp.status_code, 422)


class TestPageExists(unittest.TestCase):
    """前端页面存在性测试"""

    def test_index_page_exists(self):
        self.assertTrue(os.path.exists("frontend/pages/index.html"))

    def test_game_page_exists(self):
        self.assertTrue(os.path.exists("frontend/pages/game.html"))

    def test_player_page_exists(self):
        self.assertTrue(os.path.exists("frontend/pages/player.html"))

    def test_battle_page_exists(self):
        self.assertTrue(os.path.exists("frontend/pages/battle.html"))

    def test_equipment_page_exists(self):
        self.assertTrue(os.path.exists("frontend/pages/equipment.html"))

    def test_skills_page_exists(self):
        self.assertTrue(os.path.exists("frontend/pages/skills.html"))

    def test_tasks_page_exists(self):
        self.assertTrue(os.path.exists("frontend/pages/tasks.html"))


class TestStaticFiles(unittest.TestCase):
    """静态资源存在性测试"""

    def test_common_js_exists(self):
        self.assertTrue(os.path.exists("static/js/common.js"))

    def test_player_js_exists(self):
        self.assertTrue(os.path.exists("static/js/player.js"))

    def test_battle_js_exists(self):
        self.assertTrue(os.path.exists("static/js/battle.js"))

    def test_equipment_js_exists(self):
        self.assertTrue(os.path.exists("static/js/equipment.js"))

    def test_skills_js_exists(self):
        self.assertTrue(os.path.exists("static/js/skills.js"))

    def test_tasks_js_exists(self):
        self.assertTrue(os.path.exists("static/js/tasks.js"))

    def test_game_css_exists(self):
        self.assertTrue(os.path.exists("static/css/game.css"))

    def test_auth_js_exists(self):
        self.assertTrue(os.path.exists("static/js/auth.js"))

    def test_login_css_exists(self):
        self.assertTrue(os.path.exists("static/css/login.css"))


if __name__ == "__main__":
    unittest.main()
