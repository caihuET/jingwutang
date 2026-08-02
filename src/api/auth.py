"""认证 API"""
import logging
from urllib.parse import urlencode

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from config import config
from src.models.database import get_db
from src.service.auth_service import AuthService
from src.service.oauth_service import OAuthService
from src.utils.errors import GameException
from src.utils.security import verify_token
from src.utils.redis_client import is_session_valid

router = APIRouter()
logger = logging.getLogger(__name__)


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    result = AuthService(db).register(req.username, req.password)
    return {"code": 0, "data": result, "message": "注册成功"}


@router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    result = AuthService(db).login(req.username, req.password)
    return {"code": 0, "data": result, "message": "登录成功"}


@router.get("/auth/check")
def auth_check(token: str = "", db: Session = Depends(get_db)):
    """校验 token 是否为当前有效会话"""
    try:
        payload = verify_token(token)
        user_id = payload.get("user_id")
        valid = bool(user_id) and is_session_valid(user_id, token)
    except Exception:
        valid = False
    return {"code": 0, "data": {"valid": valid}, "message": "ok"}


@router.get("/auth/oauth/wechat/url")
def wechat_oauth_url(db: Session = Depends(get_db)):
    """微信登录授权地址"""
    url = OAuthService(db).get_wechat_authorize_url()
    return {"code": 0, "data": {"url": url}, "message": "ok"}


@router.get("/auth/oauth/google/url")
def google_oauth_url(db: Session = Depends(get_db)):
    """Google 登录授权地址"""
    url = OAuthService(db).get_google_authorize_url()
    return {"code": 0, "data": {"url": url}, "message": "ok"}


@router.get("/auth/oauth/wechat/callback")
def wechat_oauth_callback(code: str, state: str = "",
                          db: Session = Depends(get_db)):
    """微信回调"""
    return _handle_oauth_callback(lambda: OAuthService(db).handle_wechat_callback(code, state))


@router.get("/auth/oauth/google/callback")
def google_oauth_callback(code: str, state: str = "",
                          db: Session = Depends(get_db)):
    """Google 回调"""
    return _handle_oauth_callback(lambda: OAuthService(db).handle_google_callback(code, state))


def _handle_oauth_callback(handler) -> RedirectResponse:
    """统一处理第三方回调结果并跳回前端"""
    try:
        result = handler()
    except GameException as exc:
        return _oauth_redirect(error=exc.message)
    except Exception:
        logger.exception("第三方登录回调处理失败")
        return _oauth_redirect(error="第三方登录失败")
    return _oauth_redirect(
        token=result["token"],
        user_id=result["user_id"],
        created=result["created"],
    )


def _oauth_redirect(**params) -> RedirectResponse:
    """跳转到前端回调页"""
    base = "{}/oauth-callback.html".format(config.PUBLIC_APP_URL.rstrip("/"))
    query = urlencode(params)
    return RedirectResponse(base + ("?" + query if query else ""))
