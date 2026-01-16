"""自定义异常类"""
from typing import Any, Optional


class APIException(Exception):
    """API基础异常"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"ERROR_{status_code}"
        self.details = details
        super().__init__(self.message)


class ModelNotFoundException(APIException):
    """模型未找到异常"""
    
    def __init__(self, model_name: str):
        super().__init__(
            message=f"模型 '{model_name}' 不存在",
            status_code=404,
            error_code="MODEL_NOT_FOUND",
            details={"model_name": model_name}
        )


class TaskNotFoundException(APIException):
    """任务未找到异常"""
    
    def __init__(self, task_id: str):
        super().__init__(
            message=f"任务 '{task_id}' 不存在",
            status_code=404,
            error_code="TASK_NOT_FOUND",
            details={"task_id": task_id}
        )


class ConfigurationException(APIException):
    """配置错误异常"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=f"配置错误: {message}",
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details=details
        )


class ValidationException(APIException):
    """验证错误异常"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=f"验证失败: {message}",
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class RateLimitException(APIException):
    """限流异常"""
    
    def __init__(self, message: str = "请求过于频繁，请稍后再试"):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class AuthenticationException(APIException):
    """认证失败异常"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_FAILED"
        )
