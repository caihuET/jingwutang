"""认证 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.auth_service import AuthService
from src.utils.security import verify_token
from src.utils.redis_client import is_session_valid

router = APIRouter()


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

