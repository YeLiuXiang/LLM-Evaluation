"""异步任务管理器"""
import asyncio
import uuid
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TaskState:
    """任务状态"""
    task_id: str
    status: str = "pending"
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class TaskManager:
    """全局任务管理器（内存存储）"""
    
    def __init__(self):
        self._tasks: Dict[str, TaskState] = {}
        self._cleanup_interval = 3600  # 1小时后清理已完成任务
    
    def create_task(self) -> str:
        """创建新任务并返回 task_id"""
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = TaskState(task_id=task_id, status="created")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[TaskState]:
        """获取任务状态"""
        return self._tasks.get(task_id)
    
    def update_status(self, task_id: str, status: str):
        """更新任务状态"""
        if task_id in self._tasks:
            self._tasks[task_id].status = status
            if status in ("completed", "error"):
                self._tasks[task_id].completed_at = datetime.now()
    
    async def push_data(self, task_id: str, data: dict):
        """推送数据到任务队列"""
        task = self.get_task(task_id)
        if task:
            await task.queue.put(data)
    
    async def push_complete(self, task_id: str):
        """发送完成信号"""
        await self.push_data(task_id, None)
        self.update_status(task_id, "completed")
    
    async def push_error(self, task_id: str, error: str):
        """发送错误信号"""
        await self.push_data(task_id, {"error": error})
        task = self.get_task(task_id)
        if task:
            task.error = error
        self.update_status(task_id, "error")
    
    def cleanup_old_tasks(self):
        """清理过期任务（可定期调用）"""
        now = datetime.now()
        to_remove = []
        for task_id, task in self._tasks.items():
            if task.completed_at:
                elapsed = (now - task.completed_at).total_seconds()
                if elapsed > self._cleanup_interval:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self._tasks[task_id]


# 全局单例
task_manager = TaskManager()
