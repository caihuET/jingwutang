"""全模块导入与 BOM 检测"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
import glob


class TestAllImports(unittest.TestCase):
    def test_all_py_files_have_no_bom(self):
        root = os.path.join(os.path.dirname(__file__), "..")
        for path in glob.glob(os.path.join(root, "src/**/*.py"), recursive=True):
            with open(path, "rb") as f:
                data = f.read(3)
            self.assertNotEqual(data[:3], b"\xef\xbb\xbf",
                                f"BOM found in {os.path.relpath(path, root)}")

    def test_core_imports(self):
        from src.utils.constants import (ErrorCode, EXP_TABLE, SchoolType)
        self.assertIsNotNone(ErrorCode)
        self.assertTrue(len(EXP_TABLE) > 0)
        self.assertEqual(SchoolType.SHAOLIN, 1)

    def test_battle_engine_import(self):
        from src.service.battle_engine import (
            BattleEngine, BattleUnit, BattleResult, MONSTERS
        )
        self.assertIsNotNone(BattleEngine)
        self.assertIsNotNone(BattleUnit)
        self.assertIsNotNone(BattleResult)
        self.assertTrue(len(MONSTERS) > 0)

    def test_security_import(self):
        from src.utils.security import hash_password, verify_password, create_token
        self.assertIsNotNone(hash_password)
        self.assertIsNotNone(verify_password)
        self.assertIsNotNone(create_token)

    def test_validators_import(self):
        from src.utils.validators import (
            validate_username, validate_password, validate_nickname
        )
        self.assertIsNotNone(validate_username)
        self.assertIsNotNone(validate_password)
        self.assertIsNotNone(validate_nickname)

    def test_errors_import(self):
        from src.utils.errors import AppException, BadRequestError, GameException
        self.assertTrue(issubclass(GameException, AppException))
        self.assertTrue(issubclass(BadRequestError, AppException))


class TestSecurityBasic(unittest.TestCase):
    def test_hash_and_verify(self):
        from src.utils.security import hash_password, verify_password
        pwd = "TestPass123"
        hashed = hash_password(pwd)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPass", hashed))

    def test_token_creation(self):
        from src.utils.security import create_token, verify_token
        token = create_token(42)
        payload = verify_token(token)
        self.assertEqual(payload["user_id"], 42)
        self.assertIn("exp", payload)
        self.assertIn("iat", payload)


if __name__ == "__main__":
    unittest.main()
