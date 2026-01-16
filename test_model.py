#!/usr/bin/env python3
"""
快速测试单个模型的诊断脚本
用法: python test_model.py gpt-5-mini
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.main import load_model_configs
from tester.latency_tester import LatencyTester


async def main():
    model_name = sys.argv[1] if len(sys.argv) > 1 else "gpt-5-mini"
    
    configs = load_model_configs()
    if model_name not in configs:
        print(f"❌ 模型 '{model_name}' 不存在")
        print(f"可用模型: {list(configs.keys())}")
        return
    
    config = configs[model_name]
    print(f"🔍 测试模型: {model_name}")
    print(f"   Endpoint: {config.endpoint}")
    print(f"   API Version: {config.api_version}")
    print(f"   Stream: {config.stream}")
    print()
    
    tester = LatencyTester(request_timeout=30.0)
    test_question = "你好，请简要自我介绍"
    
    print(f"📤 发送请求...\n")
    records = await tester.run_models([config], question=test_question)
    
    for record in records:
        print(f"✅ 响应完成:")
        print(f"   延迟: {record.latency_ms:.0f}ms")
        print(f"   状态: {record.status}")
        if record.error:
            print(f"   ❌ 错误: {record.error}")
        if record.response_text:
            print(f"   📝 响应: {record.response_text[:200]}...")
        if record.total_tokens:
            print(f"   📊 Tokens: {record.prompt_tokens} + {record.completion_tokens} = {record.total_tokens}")


if __name__ == "__main__":
    asyncio.run(main())
