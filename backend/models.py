"""数据模型定义（Pydantic）"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ModelConfigRequest(BaseModel):
    """模型配置请求"""
    name: str
    endpoint: str
    api_key: str
    api_version: str = "2024-02-01"


class TestRequest(BaseModel):
    """测试请求"""
    models: List[str] = Field(..., description="要测试的模型名称列表")
    question: str = Field(..., description="测试问题")
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    concurrency: Optional[int] = 1
    iterations: Optional[int] = 1
    stream: Optional[bool] = True


class TestResponse(BaseModel):
    """测试响应"""
    task_id: str
    status: Literal["started", "running", "completed", "error"]
    message: str


class StreamChunk(BaseModel):
    """流式数据块"""
    model: str
    chunk: str
    request_id: Optional[int] = None
    status: Optional[Literal["connecting", "streaming", "completed", "error"]] = None
    duration: Optional[float] = None
    error: Optional[str] = None


class ModelSummary(BaseModel):
    """模型统计摘要"""
    name: str
    avg_latency: float
    p50: float
    p90: float
    p99: float
    error_rate: float
    total_requests: int
