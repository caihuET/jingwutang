"""输入校验单元测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from src.utils.validators import (
    validate_username, validate_password,
    validate_nickname, check_sensitive_words,
)


class TestValidateUsername(unittest.TestCase):
    def test_valid_usernames(self):
        self.assertTrue(validate_username("test123"))
        self.assertTrue(validate_username("abc_def"))
        self.assertTrue(validate_username("wuxia_001"))
        self.assertTrue(validate_username("abcd1234"))
        self.assertTrue(validate_username("a1b2c3d4"))

    def test_too_short(self):
        self.assertFalse(validate_username("abc"))
        self.assertFalse(validate_username("ab"))

    def test_too_long(self):
        self.assertFalse(validate_username("a" * 17))
        self.assertFalse(validate_username("abcdefghijklmnopq"))

    def test_invalid_chars(self):
        self.assertFalse(validate_username("test 123"))
        self.assertFalse(validate_username("test-123"))
        self.assertFalse(validate_username("test.123"))
        self.assertFalse(validate_username("测试账号"))

    def test_empty(self):
        self.assertFalse(validate_username(""))
        self.assertFalse(validate_username(None))


class TestValidatePassword(unittest.TestCase):
    def test_valid_passwords(self):
        self.assertTrue(validate_password("Abcd1234"))
        self.assertTrue(validate_password("Passw0rd"))
        self.assertTrue(validate_password("1234abcd"))
        self.assertTrue(validate_password("a1b2c3d4e5"))
        self.assertTrue(validate_password("MyP@ss123"))

    def test_too_short(self):
        self.assertFalse(validate_password("Abc12"))
        self.assertFalse(validate_password("a1b2c"))

    def test_no_letters(self):
        self.assertFalse(validate_password("12345678"))

    def test_no_numbers(self):
        self.assertFalse(validate_password("Abcdefgh"))

    def test_too_long(self):
        self.assertFalse(validate_password("a" * 9 + "1" * 12))


class TestValidateNickname(unittest.TestCase):
    def test_chinese(self):
        self.assertTrue(validate_nickname("剑指苍穹"))
        self.assertTrue(validate_nickname("清风"))
        self.assertTrue(validate_nickname("踏雪无痕"))
        self.assertFalse(validate_nickname("龙"))  # single char < 2 min

    def test_english(self):
        self.assertTrue(validate_nickname("Sword"))
        self.assertTrue(validate_nickname("DragonSlayer"))

    def test_too_short_chinese(self):
        self.assertFalse(validate_nickname(""))

    def test_too_long_english(self):
        self.assertFalse(validate_nickname("a" * 17))


class TestSensitiveWords(unittest.TestCase):
    def test_normal_words(self):
        self.assertTrue(check_sensitive_words("剑指苍穹"))
        self.assertTrue(check_sensitive_words("江湖侠客"))

    def test_sensitive(self):
        self.assertFalse(check_sensitive_words("管理员"))
        self.assertFalse(check_sensitive_words("系统"))
        self.assertFalse(check_sensitive_words("Admin"))
        self.assertFalse(check_sensitive_words("ROOT"))
        self.assertFalse(check_sensitive_words("test_user"))


class TestBoundaryConditions(unittest.TestCase):
    """边界条件测试"""
    def test_boundary_username_4chars(self):
        self.assertTrue(validate_username("abcd"))
        self.assertFalse(validate_username("abc"))

    def test_boundary_username_16chars(self):
        self.assertTrue(validate_username("a" * 16))
        self.assertFalse(validate_username("a" * 17))

    def test_boundary_password_8chars(self):
        self.assertTrue(validate_password("Abcd1234"))
        self.assertFalse(validate_password("Abc1234"))


if __name__ == "__main__":
    unittest.main()
