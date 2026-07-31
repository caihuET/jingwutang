"""FastAPI 应用入口"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.utils.errors import AppException
from config import config

app = FastAPI(title="精武堂 API", root_path=config.APP_ROOT_PATH)

@app.on_event("startup")
async def on_startup():
    """应用启动时自动创建数据库表"""
    import logging
    logger = logging.getLogger(__name__)
    from src.models.database import init_db
    from src.service.chat_ws import ws_manager
    try:
        init_db()
        logger.info("数据库表初始化完成")
    except Exception as e:
        logger.warning("数据库初始化失败，服务将继续运行: %s", e)
    await ws_manager.start_listener()


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
from src.api.meridian import router as meridian_router
from src.api.shop import router as shop_router
from src.api.title import router as title_router
from src.api.social import router as social_router
from src.api.guild import router as guild_router
from src.api.chat import router as chat_ws_router
from src.api.ranking import router as ranking_router

app.include_router(auth_router, prefix="/api/v1", tags=["认证"])
app.include_router(player_router, prefix="/api/v1", tags=["角色"])
app.include_router(battle_router, prefix="/api/v1", tags=["战斗"])
app.include_router(equipment_router, prefix="/api/v1", tags=["装备"])
app.include_router(skill_router, prefix="/api/v1", tags=["技能"])
app.include_router(task_router, prefix="/api/v1", tags=["任务"])
app.include_router(meridian_router, prefix="/api/v1", tags=["经脉"])
app.include_router(shop_router, prefix="/api/v1", tags=["商城"])
app.include_router(title_router, prefix="/api/v1", tags=["称号"])
app.include_router(social_router, prefix="/api/v1", tags=["社交"])
app.include_router(guild_router, prefix="/api/v1", tags=["帮派"])
app.include_router(chat_ws_router, prefix="/api/v1", tags=["聊天"])
app.include_router(ranking_router, prefix="/api/v1", tags=["排行"])


@app.get("/api/v1/health")
def health_check():
    return {"code": 0, "data": {"status": "ok"}, "message": "success"}
