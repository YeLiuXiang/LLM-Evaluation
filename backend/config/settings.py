"""环境变量配置管理"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # CORS配置
    ALLOWED_ORIGINS: str = "*"  # 逗号分隔的来源列表
    
    # 数据存储配置
    HISTORY_FILE: str = "data/test_history.json"
    MAX_HISTORY_RECORDS: int = 100
    
    # 任务配置
    TASK_CLEANUP_INTERVAL: int = 3600  # 1小时
    REQUEST_TIMEOUT: float = 60.0
    
    # 限流配置
    ENABLE_RATE_LIMIT: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # 缓存配置
    ENABLE_CACHE: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 监控配置
    ENABLE_METRICS: bool = False
    
    # 模型配置
    MODELS_CONFIG_FILE: str = "config/models.yaml"
    
    # 日志配置
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_SIZE: int = 10  # MB
    LOG_BACKUP_COUNT: int = 5
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """将CORS来源字符串转换为列表"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    @property
    def base_dir(self) -> Path:
        """项目根目录"""
        return Path(__file__).parent.parent.parent
    
    @property
    def models_config_path(self) -> Path:
        """模型配置文件完整路径"""
        return self.base_dir / self.MODELS_CONFIG_FILE
    
    @property
    def history_file_path(self) -> Path:
        """历史记录文件完整路径"""
        return self.base_dir / self.HISTORY_FILE
    
    @property
    def log_file_path(self) -> Path:
        """日志文件完整路径"""
        return self.base_dir / self.LOG_FILE


# 全局配置实例
settings = Settings()
