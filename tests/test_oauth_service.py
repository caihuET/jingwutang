"""微信/Google OAuth 登录回归测试"""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.service.auth_service import AuthService
from src.service.oauth_service import OAuthService


class _FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id
        self.status = 1
        self.last_login_at = None


class _FakeRepo:
    """模拟 UserRepository 的第三方登录查询与创建"""

    def __init__(self, existing=None):
        self.existing = existing
        self.created = []
        self.db = SimpleNamespace(commit=lambda: None)

    def get_by_oauth(self, provider, oauth_id):
        return self.existing

    def get_by_username(self, username):
        return None

    def create_oauth(self, username, password_hash, register_ip,
                     provider, oauth_id, oauth_name="",
                     oauth_avatar="", email=""):
        user = _FakeUser(7)
        self.created.append((username, provider, oauth_id, email))
        return user


class TestOAuthService(unittest.TestCase):
    """OAuth 授权地址与 state 校验测试"""

    def test_wechat_url_contains_required_params(self):
        service = OAuthService.__new__(OAuthService)
        with patch.object(OAuthService, "_create_state", return_value="state123"):
            with patch("src.service.oauth_service.config.WECHAT_APP_ID", "wxid"):
                url = service.get_wechat_authorize_url()
        self.assertIn("appid=wxid", url)
        self.assertIn("state=state123", url)
        self.assertIn("wechat_redirect", url)

    def test_google_url_contains_required_params(self):
        service = OAuthService.__new__(OAuthService)
        with patch.object(OAuthService, "_create_state", return_value="gstate"):
            with patch("src.service.oauth_service.config.GOOGLE_CLIENT_ID", "gid"):
                url = service.get_google_authorize_url()
        self.assertIn("client_id=gid", url)
        self.assertIn("state=gstate", url)

    def test_verify_state_rejects_wrong_provider(self):
        service = OAuthService.__new__(OAuthService)
        state = service._create_state("wechat")
        with self.assertRaises(Exception):
            service._verify_state(state, "google")


class TestOAuthAutoRegister(unittest.TestCase):
    """第三方登录自动注册/登录测试"""

    def test_existing_oauth_user_just_logs_in(self):
        repo = _FakeRepo(existing=_FakeUser(7))
        service = AuthService.__new__(AuthService)
        service.repo = repo
        with patch("src.service.auth_service.create_token", return_value="tok"):
            with patch("src.service.auth_service.set_session") as set_session:
                result = service.oauth_login("wechat", "openid_1", "微信用户")
        self.assertFalse(result["created"])
        self.assertEqual(result["user_id"], 7)
        self.assertEqual(result["token"], "tok")
        set_session.assert_called_once_with(7, "tok")
        self.assertEqual(len(repo.created), 0)

    def test_new_oauth_user_is_auto_registered(self):
        repo = _FakeRepo(existing=None)
        service = AuthService.__new__(AuthService)
        service.repo = repo
        with patch("src.service.auth_service.hash_password", return_value="hash"):
            with patch("src.service.auth_service.create_token", return_value="tok"):
                with patch("src.service.auth_service.set_session"):
                    result = service.oauth_login(
                        "google", "sub_1", "Google用户", "a@b.com", "avatar"
                    )
        self.assertTrue(result["created"])
        self.assertEqual(len(repo.created), 1)
        self.assertEqual(repo.created[0][1], "google")
        self.assertEqual(repo.created[0][2], "sub_1")
        self.assertEqual(repo.created[0][3], "a@b.com")


if __name__ == "__main__":
    unittest.main()
