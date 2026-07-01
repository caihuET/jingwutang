"""FastAPI 应用入口"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.utils.errors import AppException
from config import config

app = FastAPI(title="精武堂 API", root_path=config.APP_ROOT_PATH)


from fastapi.responses import JSONResponse
import os

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "data": None, "message": exc.message or ""},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={"code": 5000, "data": None, "message": "服务器内部错误"},
    )


# 注册路由
from src.api.auth import router as auth_router
from src.api.player import router as player_router
from src.api.battle import router as battle_router
from src.api.equipment import router as equipment_router
from src.api.skill import router as skill_router
from src.api.task import router as task_router

app.include_router(auth_router, prefix="/api/v1", tags=["认证"])
app.include_router(player_router, prefix="/api/v1", tags=["角色"])
app.include_router(battle_router, prefix="/api/v1", tags=["战斗"])
app.include_router(equipment_router, prefix="/api/v1", tags=["装备"])
app.include_router(skill_router, prefix="/api/v1", tags=["技能"])
app.include_router(task_router, prefix="/api/v1", tags=["任务"])


@app.get("/")
def root_page():
    from fastapi.responses import HTMLResponse
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>精武堂</title>
<style>
body{display:flex;align-items:center;justify-content:center;min-height:100vh;background:#1a1a2e;color:#c9a96e;font-family:sans-serif;margin:0}
.card{text-align:center;padding:40px;border:2px solid #c9a96e;border-radius:12px;background:linear-gradient(180deg,#fff8e7,#f0e6d0)}
h1{font-size:36px;letter-spacing:8px;color:#8b1a1a}
.btn{display:inline-block;padding:12px 32px;background:linear-gradient(135deg,#8b1a1a,#5c0e0e);color:#c9a96e;text-decoration:none;border-radius:6px;margin:4px}
</style></head>
<body><div class="card">
<h1>精武堂</h1>
<p>服务器运行正常</p>
<a class="btn" href="/game/jwt/api/v1/health">健康检查</a>
</div></body></html>"""
    return HTMLResponse(content=html)

@app.get("/api/v1/health")
def health_check():
    return {"code": 0, "data": {"status": "ok"}, "message": "success"}
