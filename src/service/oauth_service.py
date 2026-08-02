"""微信/Google OAuth 登录服务"""
import json
import logging
import time
import urllib.parse
import urllib.request

import jwt

from config import config
from src.service.auth_service import AuthService
from src.utils.constants import ErrorCode
from src.utils.errors import GameException

logger = logging.getLogger(__name__)

WECHAT_AUTHORIZE_URL = "https://open.weixin.qq.com/connect/qrconnect"
WECHAT_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
WECHAT_USERINFO_URL = "https://api.weixin.qq.com/sns/userinfo"
GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class OAuthService:
    """第三方登录：授权地址、回调换 token、自动注册"""

    def __init__(self, db):
        self.db = db
        self.auth = AuthService(db)

    def get_wechat_authorize_url(self) -> str:
        """生成微信扫码登录授权地址"""
        self._require_config(config.WECHAT_APP_ID, "微信")
        params = {
            "appid": config.WECHAT_APP_ID,
            "redirect_uri": self._callback_url("wechat"),
            "response_type": "code",
            "scope": "snsapi_login",
            "state": self._create_state("wechat"),
        }
        return "{}?{}#wechat_redirect".format(
            WECHAT_AUTHORIZE_URL, urllib.parse.urlencode(params)
        )

    def get_google_authorize_url(self) -> str:
        """生成 Google 登录授权地址"""
        self._require_config(config.GOOGLE_CLIENT_ID, "Google")
        params = {
            "client_id": config.GOOGLE_CLIENT_ID,
            "redirect_uri": self._callback_url("google"),
            "response_type": "code",
            "scope": "openid email profile",
            "state": self._create_state("google"),
        }
        return "{}?{}".format(
            GOOGLE_AUTHORIZE_URL, urllib.parse.urlencode(params)
        )

    def handle_wechat_callback(self, code: str, state: str) -> dict:
        """处理微信回调并自动注册/登录"""
        self._verify_state(state, "wechat")
        self._require_config(config.WECHAT_APP_ID, "微信")
        data = self._get_json(WECHAT_TOKEN_URL, {
            "appid": config.WECHAT_APP_ID,
            "secret": config.WECHAT_APP_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        })
        openid = data.get("openid")
        if not openid:
            raise GameException(ErrorCode.PARAM_INVALID, "微信登录失败，未获取到 openid")
        profile = {}
        try:
            profile = self._get_json(WECHAT_USERINFO_URL, {
                "access_token": data.get("access_token", ""),
                "openid": openid,
                "lang": "zh_CN",
            })
        except Exception:
            logger.warning("微信用户信息获取失败: openid=%s", openid[-6:])
        oauth_id = data.get("unionid") or openid
        name = profile.get("nickname") or "微信用户" + openid[-4:]
        avatar = profile.get("headimgurl", "")
        return self.auth.oauth_login("wechat", oauth_id, name, "", avatar)

    def handle_google_callback(self, code: str, state: str) -> dict:
        """处理 Google 回调并自动注册/登录"""
        self._verify_state(state, "google")
        self._require_config(config.GOOGLE_CLIENT_ID, "Google")
        token_data = self._post_form(GOOGLE_TOKEN_URL, {
            "code": code,
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "redirect_uri": self._callback_url("google"),
            "grant_type": "authorization_code",
        })
        access_token = token_data.get("access_token")
        if not access_token:
            raise GameException(ErrorCode.PARAM_INVALID, "Google 登录失败，未获取到 token")
        profile = self._get_json(GOOGLE_USERINFO_URL, headers={
            "Authorization": "Bearer " + access_token,
        })
        sub = profile.get("sub")
        if not sub:
            raise GameException(ErrorCode.PARAM_INVALID, "Google 登录失败，未获取到用户信息")
        return self.auth.oauth_login(
            "google",
            sub,
            profile.get("name") or "Google用户" + sub[-4:],
            profile.get("email", ""),
            profile.get("picture", ""),
        )

    def _get_json(self, url: str, params: dict = None,
                  headers: dict = None) -> dict:
        """GET 请求并解析 JSON"""
        if params:
            sep = "&" if "?" in url else "?"
            url += sep + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=headers or {})
        return self._read_json(req)

    def _post_form(self, url: str, data: dict) -> dict:
        """POST 表单并解析 JSON"""
        body = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return self._read_json(req)

    def _read_json(self, req) -> dict:
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            logger.warning("OAuth 请求失败: %s", exc)
            raise GameException(ErrorCode.PARAM_INVALID, "第三方登录服务暂时不可用")

    def _create_state(self, provider: str) -> str:
        """生成短期有效的 state，防 CSRF"""
        payload = {
            "provider": provider,
            "exp": int(time.time()) + 600,
            "iat": int(time.time()),
        }
        return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

    def _verify_state(self, state: str, provider: str) -> None:
        try:
            payload = jwt.decode(
                state, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
            )
        except Exception:
            raise GameException(ErrorCode.PARAM_INVALID, "登录状态已失效，请重新登录")
        if payload.get("provider") != provider:
            raise GameException(ErrorCode.PARAM_INVALID, "登录状态异常，请重新登录")

    def _callback_url(self, provider: str) -> str:
        return "{}/api/v1/auth/oauth/{}/callback".format(
            config.PUBLIC_APP_URL.rstrip("/"), provider
        )

    def _require_config(self, value: str, provider_name: str) -> None:
        if not value:
            raise GameException(
                ErrorCode.PARAM_INVALID, "{} 登录尚未配置".format(provider_name)
            )
