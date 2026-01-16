"""历史记录管理器"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


class HistoryManager:
    def __init__(self, history_file: str = "data/test_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """确保历史记录文件存在"""
        if not self.history_file.exists():
            self.history_file.write_text(json.dumps([], ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """加载历史记录"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            return []
    
    def _save_history(self, history: List[Dict[str, Any]]):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def add_record(self, summary_data: List[Dict[str, Any]], test_config: Dict[str, Any]) -> str:
        """
        添加测试记录
        
        Args:
            summary_data: 统计摘要数据
            test_config: 测试配置（问题、参数等）
        
        Returns:
            记录ID
        """
        history = self._load_history()
        
        # 生成唯一ID（使用时间戳）
        record_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        record = {
            "id": record_id,
            "timestamp": datetime.now().isoformat(),
            "test_config": test_config,
            "summary": summary_data,
            "model_count": len(summary_data),
        }
        
        # 插入到列表开头（最新的在前面）
        history.insert(0, record)
        
        # 限制历史记录数量（保留最近100条）
        if len(history) > 100:
            history = history[:100]
        
        self._save_history(history)
        return record_id
    
    def get_all_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取所有历史记录（摘要信息）
        
        Args:
            limit: 返回的最大记录数
        
        Returns:
            历史记录列表
        """
        history = self._load_history()
        
        # 返回简化的记录列表（不包含完整的summary数据）
        return [
            {
                "id": record["id"],
                "timestamp": record["timestamp"],
                "model_count": record.get("model_count", 0),
                "question": record.get("test_config", {}).get("question", "")[:50] + "..." if len(record.get("test_config", {}).get("question", "")) > 50 else record.get("test_config", {}).get("question", ""),
                "models": [item.get("model", "") for item in record.get("summary", [])][:5],  # 只返回前5个模型名
            }
            for record in history[:limit]
        ]
    
    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定的历史记录（完整数据）
        
        Args:
            record_id: 记录ID
        
        Returns:
            历史记录详情
        """
        history = self._load_history()
        
        for record in history:
            if record["id"] == record_id:
                return record
        
        return None
    
    def delete_record(self, record_id: str) -> bool:
        """
        删除指定的历史记录
        
        Args:
            record_id: 记录ID
        
        Returns:
            是否删除成功
        """
        history = self._load_history()
        
        for i, record in enumerate(history):
            if record["id"] == record_id:
                history.pop(i)
                self._save_history(history)
                return True
        
        return False
    
    def clear_all(self):
        """清空所有历史记录"""
        self._save_history([])
