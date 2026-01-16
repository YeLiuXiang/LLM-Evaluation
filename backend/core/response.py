"""统一API响应格式"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """统一API响应模型"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[Any] = Field(None, description="响应数据")
    message: str = Field("", description="响应消息")
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


def success_response(
    data: Any = None,
    message: str = "操作成功"
) -> dict:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
    
    Returns:
        响应字典
    """
    return APIResponse(
        success=True,
        data=data,
        message=message
    ).model_dump()


def error_response(
    error: str,
    message: str = "操作失败",
    data: Any = None
) -> dict:
    """
    创建错误响应
    
    Args:
        error: 错误信息
        message: 错误消息
        data: 附加数据
    
    Returns:
        响应字典
    """
    return APIResponse(
        success=False,
        data=data,
        message=message,
        error=error
    ).model_dump()


def paginated_response(
    items: list,
    total: int,
    page: int = 1,
    page_size: int = 50,
    message: str = "查询成功"
) -> dict:
    """
    创建分页响应
    
    Args:
        items: 数据列表
        total: 总数量
        page: 当前页码
        page_size: 每页大小
        message: 响应消息
    
    Returns:
        响应字典
    """
    return success_response(
        data={
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        },
        message=message
    )
