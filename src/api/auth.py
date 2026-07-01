"""认证 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.auth_service import AuthService

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
