"""
优化后的 FastAPI 主入口（示例）

这是一个演示文件，展示了如何使用新的配置管理、统一响应格式和异常处理。
实际使用时，可以逐步将 backend/main.py 迁移到这个架构。
"""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# 新的配置和核心模块
from backend.config import settings, setup_logger
from backend.core import (
    APIException,
    success_response,
    error_response,
    ModelNotFoundException,
    ValidationException
)

# 现有模块
from backend.task_manager import task_manager
from backend.history_manager import HistoryManager

# 配置日志
logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("=" * 60)
    logger.info("🚀 LLM 延迟测试器启动中...")
    logger.info(f"环境: {'开发' if settings.DEBUG else '生产'}")
    logger.info(f"日志级别: {settings.LOG_LEVEL}")
    logger.info(f"CORS来源: {settings.allowed_origins_list}")
    logger.info("=" * 60)
    
    # 启动后台清理任务
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield
    
    # 关闭时
    cleanup_task.cancel()
    logger.info("👋 应用已关闭")


async def periodic_cleanup():
    """定期清理过期任务"""
    while True:
        try:
            await asyncio.sleep(settings.TASK_CLEANUP_INTERVAL)
            task_manager.cleanup_old_tasks()
            logger.info("✅ 完成任务清理")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"任务清理失败: {e}")


# 创建应用
app = FastAPI(
    title="LLM Latency Tester API",
    version="2.0.0",
    description="基于优化架构的LLM延迟测试工具",
    lifespan=lifespan
)

# CORS配置（使用配置文件中的设置）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """处理自定义API异常"""
    logger.warning(f"API异常: {exc.message} (状态码: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error=exc.message,
            message=exc.error_code,
            data=exc.details
        )
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    logger.warning(f"HTTP异常: {exc.detail} (状态码: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error=exc.detail,
            message=f"HTTP_{exc.status_code}"
        )
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=error_response(
            error="服务器内部错误",
            message="INTERNAL_SERVER_ERROR"
        )
    )


# 挂载静态文件
FRONTEND_DIR = settings.base_dir / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ==================== 路由示例 ====================

@app.get("/")
async def root():
    """根路径"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return success_response(
        data={
            "message": "LLM Latency Tester API",
            "version": "2.0.0",
            "docs": "/docs"
        }
    )


@app.get("/api/health")
async def health_check():
    """健康检查（使用统一响应格式）"""
    return success_response(
        data={
            "status": "healthy",
            "active_tasks": len([
                t for t in task_manager._tasks.values()
                if t.status == "running"
            ]),
            "debug": settings.DEBUG
        },
        message="服务运行正常"
    )


@app.get("/api/config/info")
async def get_config_info():
    """获取配置信息（脱敏）"""
    return success_response(
        data={
            "debug": settings.DEBUG,
            "log_level": settings.LOG_LEVEL,
            "rate_limit_enabled": settings.ENABLE_RATE_LIMIT,
            "cache_enabled": settings.ENABLE_CACHE,
            "metrics_enabled": settings.ENABLE_METRICS,
            "max_history_records": settings.MAX_HISTORY_RECORDS
        },
        message="配置信息"
    )


# ==================== 演示：使用新异常系统 ====================

@app.get("/api/demo/model/{model_name}")
async def demo_get_model(model_name: str):
    """
    演示路由：展示如何抛出自定义异常
    
    抛出的异常会被全局异常处理器捕获并转换为统一格式
    """
    # 模拟：如果模型不存在，抛出ModelNotFoundException
    if model_name == "nonexistent":
        raise ModelNotFoundException(model_name)
    
    # 模拟：如果参数无效，抛出ValidationException
    if not model_name.strip():
        raise ValidationException("模型名称不能为空")
    
    # 正常返回
    return success_response(
        data={"model_name": model_name, "status": "active"},
        message=f"模型 {model_name} 信息"
    )


# ==================== 提示信息 ====================

@app.on_event("startup")
async def startup_message():
    """启动提示"""
    logger.info("")
    logger.info("📖 使用说明：")
    logger.info(f"   - 前端界面: http://localhost:{settings.PORT}")
    logger.info(f"   - API文档: http://localhost:{settings.PORT}/docs")
    logger.info(f"   - 健康检查: http://localhost:{settings.PORT}/api/health")
    logger.info(f"   - 配置信息: http://localhost:{settings.PORT}/api/config/info")
    logger.info("")
    logger.info("💡 提示：")
    logger.info("   1. 已修复模型名称空格问题")
    logger.info("   2. 已添加配置管理系统（查看 .env.example）")
    logger.info("   3. 已添加统一响应格式")
    logger.info("   4. 已添加全局异常处理")
    logger.info("   5. 建议查看 ARCHITECTURE_OPTIMIZATION.md 了解完整优化方案")
    logger.info("")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_optimized:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
