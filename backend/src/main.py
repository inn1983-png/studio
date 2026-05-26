"""
Txtovideo Studio - FastAPI应用入口
"""

import time

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from src.api.health import router as health_router
from src.middleware import (
    error_handler_middleware,
    logging_middleware,
    security_middleware,
    performance_monitoring_middleware,
)
from src.middleware.security import rate_limit_middleware
from src.api.v1 import api_router
from src.api.websocket import router as websocket_router
from src.core.config import settings
from src.core.exceptions import TxtovideoException
from src.core.logging import logger, setup_logging

# 设置日志
setup_logging()

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": f"{settings.APP_NAME} Team",
        "url": f"https://github.com/your-org/{settings.APP_CELERY_NAME}-studio",
        "email": f"team@{settings.APP_CELERY_NAME}-studio.com",
    },
    license_info={
        "name": "Apache License 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0",
    },
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
)

# 添加受信任主机中间件
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# 添加自定义中间件 (顺序重要)
# 注意：中间件的执行顺序是注册的逆序
app.middleware("http")(error_handler_middleware)          # 最外层，处理所有异常
app.middleware("http")(performance_monitoring_middleware) # 性能监控
app.middleware("http")(logging_middleware)                # 日志记录
app.middleware("http")(security_middleware)               # 安全检查
app.middleware("http")(rate_limit_middleware)             # 速率限制


# 添加请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加请求处理时间头"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# 注册路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router, prefix="/health")
app.include_router(websocket_router, prefix="/ws")


@app.on_event("startup")
async def startup_event():
    import logging
    app_logger = logging.getLogger(__name__)

    app_logger.info(f"🚀 {settings.APP_NAME} 正在启动...")
    app_logger.info(f"📝 环境: {settings.ENVIRONMENT}")
    app_logger.info(f"🌐 调试模式: {settings.DEBUG}")
    app_logger.info(f"🔗 API地址: http://0.0.0.0:8000")
    app_logger.info(f"📖 API文档: http://0.0.0.0:8000/docs")

    try:
        from src.core.database import AsyncSessionLocal, create_database_engine
        from src.models.api_key import APIKey, APIKeyStatus
        from src.models.user import User
        from sqlalchemy import select

        if AsyncSessionLocal is None:
            await create_database_engine()

        from src.core.database import AsyncSessionLocal as SessionFactory

        async with SessionFactory() as db:
                result = await db.execute(select(User))
                users = result.scalars().all()

                for user in users:
                    existing = await db.execute(
                        select(APIKey).where(
                            APIKey.user_id == user.id,
                            APIKey.provider == "local"
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    local_key = APIKey(
                        user_id=user.id,
                        name="本地模型 (Local LLM)",
                        provider="local",
                        base_url="http://localhost:8081/v1",
                        status=APIKeyStatus.ACTIVE,
                    )
                    local_key.set_api_key("local-llm-key")
                    db.add(local_key)

                await db.commit()
                app_logger.info("✅ 本地模型 API Key 已就绪")
    except Exception as e:
        app_logger.warning(f"⚠️ 自动创建本地模型 Key 失败（可忽略）: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    import logging
    app_logger = logging.getLogger(__name__)
    app_logger.info(f"🛑 {settings.APP_NAME} 正在关闭...")
    # 这里可以添加清理逻辑


@app.exception_handler(TxtovideoException)
async def txtovideo_exception_handler(request: Request, exc: TxtovideoException):
    """Txtovideo自定义异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": time.time(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误" if not settings.DEBUG else str(exc),
            "timestamp": time.time(),
        },
    )


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用 {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/info")
async def app_info(current_user: User = Depends(get_current_user_required)):
    """应用信息"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "api_prefix": settings.API_V1_PREFIX,
        "monitoring": {
            "structured_logging": settings.STRUCTURED_LOGGING,
        },
    }


@app.get("/brand")
async def brand_config():
    """品牌配置（前端可访问，无需认证）"""
    return {
        "appName": settings.APP_NAME,
        "appDescription": settings.APP_DESCRIPTION,
        "logoText": settings.APP_LOGO_TEXT,
        "copyright": settings.APP_COPYRIGHT,
    }


def main():
    """主函数入口"""
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        use_colors=True,
    )


if __name__ == "__main__":
    main()
