"""FastAPI 主入口"""
import asyncio
import json
import sys
import threading
from pathlib import Path
from typing import List, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

# 添加项目根目录到路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.models import ModelConfigRequest, TestRequest, TestResponse, StreamChunk
from backend.task_manager import task_manager
from backend.history_manager import HistoryManager
from tester.latency_tester import LatencyTester, ModelConfig, RequestRecord, MODEL_PARAM_SUPPORT
from tester.metrics import records_to_dataframe, summarize_latency
import yaml

app = FastAPI(title="LLM Latency Tester API", version="1.0.0")

# 初始化历史记录管理器
history_manager = HistoryManager()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（前端）
FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

CONFIG_PATH = BASE_DIR / "config" / "models.yaml"
CONFIG_LOCK = threading.Lock()


def read_model_config_items() -> List[Dict]:
    """从配置文件读取原始模型列表"""
    with CONFIG_LOCK:
        if not CONFIG_PATH.exists():
            return []
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return raw.get("models", [])


def save_model_config_items(items: List[Dict]):
    """将模型配置写回文件"""
    with CONFIG_LOCK:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            yaml.safe_dump({"models": items}, f, sort_keys=False)


def load_model_configs() -> Dict[str, ModelConfig]:
    """从配置文件加载模型配置"""
    configs = {}
    for item in read_model_config_items():
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        cfg = ModelConfig(
            name=name,
            endpoint=item["endpoint"],
            api_key=item["api_key"],
            api_version=item["api_version"],
            prompt="Hello, test",  # 默认提示词
            max_tokens=item.get("max_tokens", 1000),
            temperature=item.get("temperature", 0.7),
            concurrency=item.get("concurrency", 1),
            iterations=item.get("iterations", 1),
            stream=item.get("stream", False),
        )
        configs[cfg.name] = cfg
    
    return configs


@app.get("/")
async def root():
    """根路径，返回前端页面"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "LLM Latency Tester API", "docs": "/docs"}


@app.get("/api/models")
async def get_models():
    """获取可用模型列表及其参数支持信息"""
    try:
        configs = load_model_configs()
        models = [
            {
                "name": cfg.name,
                "endpoint": cfg.endpoint,
                "api_version": cfg.api_version,
                "supported_params": MODEL_PARAM_SUPPORT.get(cfg.name, MODEL_PARAM_SUPPORT["default"]),
            }
            for cfg in configs.values()
        ]
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载模型配置失败: {str(e)}")


@app.get("/api/models/{model_name}")
async def get_model_info(model_name: str):
    """获取单个模型的详细信息"""
    try:
        configs = load_model_configs()
        if model_name not in configs:
            raise HTTPException(status_code=404, detail=f"模型 '{model_name}' 不存在")
        
        cfg = configs[model_name]
        return {
            "name": cfg.name,
            "endpoint": cfg.endpoint,
            "api_version": cfg.api_version,
            "supported_params": MODEL_PARAM_SUPPORT.get(cfg.name, MODEL_PARAM_SUPPORT["default"]),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型信息失败: {str(e)}")


@app.post("/api/models")
async def add_model_config(request: ModelConfigRequest):
    """新增模型配置并持久化"""
    name = request.name.strip()
    endpoint = request.endpoint.strip()
    api_key = request.api_key.strip()
    api_version = request.api_version.strip()

    if not name or not endpoint or not api_key or not api_version:
        raise HTTPException(status_code=400, detail="名称、地址、API Key 和版本均为必填项")

    try:
        existing_items = read_model_config_items()
        if any(str(item.get("name", "")).strip().lower() == name.lower()
               for item in existing_items):
            raise HTTPException(status_code=400, detail=f"模型 '{name}' 已存在")

        # 只保存必要的 4 个字段，其他参数在测试时由用户动态指定
        new_item = {
            "name": name,
            "endpoint": endpoint,
            "api_key": api_key,
            "api_version": api_version,
        }

        existing_items.append(new_item)
        save_model_config_items(existing_items)

        return {"detail": f"模型 '{name}' 已保存"}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"保存模型配置失败: {str(exc)}")


@app.post("/api/test", response_model=TestResponse)
async def start_test(request: TestRequest):
    """启动测试任务"""
    try:
        # 加载模型配置
        all_configs = load_model_configs()
        
        # 验证请求的模型是否存在
        selected_configs = []
        for model_name in request.models:
            if model_name not in all_configs:
                raise HTTPException(
                    status_code=400, 
                    detail=f"模型 '{model_name}' 不存在于配置文件中"
                )
            # 应用覆盖参数
            cfg = all_configs[model_name]
            cfg = cfg.with_overrides(
                prompt=request.question,
                max_tokens=request.max_tokens or cfg.max_tokens,
                temperature=request.temperature or cfg.temperature,
                concurrency=request.concurrency or cfg.concurrency,
                iterations=request.iterations or cfg.iterations,
                stream=request.stream if request.stream is not None else cfg.stream,
            )
            selected_configs.append(cfg)
        
        if not selected_configs:
            raise HTTPException(status_code=400, detail="至少选择一个模型")
        
        # 创建任务
        task_id = task_manager.create_task()
        task_manager.update_status(task_id, "running")
        
        # 后台启动测试
        asyncio.create_task(
            run_test_background(task_id, selected_configs, request.question)
        )
        
        return TestResponse(
            task_id=task_id,
            status="started",
            message=f"已启动 {len(selected_configs)} 个模型的测试任务"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动测试失败: {str(e)}")


async def run_test_background(
    task_id: str, 
    configs: List[ModelConfig], 
    question: str
):
    """后台运行测试任务"""
    try:
        tester = LatencyTester()
        
        # 用于存储所有记录
        all_records: List[RequestRecord] = []
        records_lock = asyncio.Lock()
        
        # 定义流式回调
        def stream_callback(model_name: str, request_id: int, chunk: str):
            """流式回调函数"""
            data = {
                "model": model_name,
                "chunk": chunk,
                "request_id": request_id,
                "status": "streaming"
            }
            # 异步推送数据
            asyncio.create_task(task_manager.push_data(task_id, data))
        
        # 为每个模型创建独立任务，实现真正的并发
        async def run_single_model(config: ModelConfig):
            """运行单个模型并在完成后立即推送统计"""
            try:
                # 运行该模型的测试
                records: List[RequestRecord] = await tester.run_models(
                    [config], 
                    question=question, 
                    stream_callback=stream_callback
                )
                
                # 线程安全地保存记录
                async with records_lock:
                    all_records.extend(records)
                
                # 将最终响应文本推送给前端
                for r in records:
                    if r.response_text:
                        await task_manager.push_data(task_id, {
                            "model": r.model,
                            "chunk": r.response_text,
                            "request_id": r.request_id,
                            "status": "completed",
                            "duration": r.latency_ms,
                        })
                
                # 立即计算并推送该模型的统计数据
                df = records_to_dataframe(records)
                if len(df) > 0:
                    summary = summarize_latency(df)
                    summary_data = summary.to_dict(orient="records")
                    
                    # 推送该模型的统计数据
                    await task_manager.push_data(task_id, {
                        "type": "summary",
                        "data": summary_data,
                        "model_name": config.name,
                        "is_partial": True
                    })
                    print(f"模型 {config.name} 统计已推送")
                    
            except Exception as e:
                print(f"模型 {config.name} 测试失败: {e}")
                # 推送错误统计
                await task_manager.push_data(task_id, {
                    "type": "summary",
                    "data": [{
                        "model": config.name,
                        "avg_latency": None,
                        "min_latency": None,
                        "max_latency": None,
                        "first_token_avg": None,
                        "first_token_min": None,
                        "first_token_max": None,
                        "error_rate": 1.0,
                        "total_requests": config.concurrency * config.iterations,
                        "success_count": 0,
                        "error_count": config.concurrency * config.iterations,
                    }],
                    "model_name": config.name,
                    "is_partial": True,
                    "error": str(e)
                })
        
        # 并发启动所有模型的测试
        tasks = [asyncio.create_task(run_single_model(config)) for config in configs]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 计算完整的统计数据（用于保存历史记录）
        df = records_to_dataframe(all_records)
        print(f"所有模型测试完成，总记录数: {len(df)}")
        
        if len(df) > 0:
            summary = summarize_latency(df)
            summary_data = summary.to_dict(orient="records")
            print("完整统计数据:", summary_data)
            
            # 保存到历史记录
            try:
                test_config = {
                    "question": question or "未指定问题",
                    "models": [config.name for config in configs],
                    "concurrency": configs[0].concurrency if configs else 1,
                    "iterations": configs[0].iterations if configs else 1,
                    "max_tokens": configs[0].max_tokens if configs else 1000,
                    "temperature": configs[0].temperature if configs else 0.7,
                    "stream": configs[0].stream if configs else False,
                }
                record_id = history_manager.add_record(summary_data, test_config)
                print(f"历史记录已保存，ID: {record_id}")
            except Exception as e:
                print(f"保存历史记录失败: {e}")
            
            # 推送最终完成信号（包含完整统计，用于历史记录）
            await task_manager.push_data(task_id, {
                "type": "summary_complete",
                "data": summary_data,
                "is_partial": False
            })
        else:
            print("没有数据需要统计")
        
        await task_manager.push_complete(task_id)
    
    except Exception as e:
        await task_manager.push_error(task_id, str(e))


@app.get("/api/stream/{task_id}")
async def stream_results(task_id: str):
    """SSE 流式推送测试结果"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    async def event_generator():
        """事件生成器"""
        try:
            while True:
                # 从队列中获取数据
                data = await task.queue.get()
                
                # None 表示完成信号
                if data is None:
                    yield {
                        "event": "complete",
                        "data": json.dumps({"status": "completed"})
                    }
                    break
                
                # 检查是否为错误
                if "error" in data:
                    yield {
                        "event": "error",
                        "data": json.dumps({"error": data["error"]})
                    }
                    break
                
                # 检查是否为统计摘要
                if data.get("type") == "summary":
                    yield {
                        "event": "summary",
                        "data": json.dumps(data["data"])
                    }
                    continue
                
                # 检查是否为完整统计摘要
                if data.get("type") == "summary_complete":
                    yield {
                        "event": "summary_complete",
                        "data": json.dumps(data["data"])
                    }
                    continue
                
                # 正常的流式数据块
                yield {
                    "event": "chunk",
                    "data": json.dumps(data)
                }
        
        except asyncio.CancelledError:
            # 客户端断开连接
            pass
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "active_tasks": len([
            t for t in task_manager._tasks.values() 
            if t.status == "running"
        ])
    }


@app.get("/api/history")
async def get_history(limit: int = 50):
    """获取历史记录列表"""
    try:
        records = history_manager.get_all_records(limit=limit)
        return {
            "status": "success",
            "count": len(records),
            "records": records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@app.get("/api/history/{record_id}")
async def get_history_detail(record_id: str):
    """获取历史记录详情"""
    try:
        record = history_manager.get_record(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        return {
            "status": "success",
            "record": record
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记录详情失败: {str(e)}")


@app.delete("/api/history/{record_id}")
async def delete_history(record_id: str):
    """删除历史记录"""
    try:
        success = history_manager.delete_record(record_id)
        if not success:
            raise HTTPException(status_code=404, detail="记录不存在")
        return {
            "status": "success",
            "message": "记录已删除"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除记录失败: {str(e)}")


@app.delete("/api/history")
async def clear_history():
    """清空所有历史记录"""
    try:
        history_manager.clear_all()
        return {
            "status": "success",
            "message": "所有历史记录已清空"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空历史记录失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
