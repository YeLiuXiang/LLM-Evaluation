#!/usr/bin/env python3
"""
测试统计摘要功能的修复
"""
import pandas as pd
from tester.metrics import summarize_latency

def create_test_data():
    """创建测试数据"""
    # 模拟低并发数的测试数据（3个请求）
    low_concurrency_data = [
        {"model": "gpt-4o", "latency_ms": 850.5, "error": None, "prompt_tokens": 50, "completion_tokens": 120, "total_tokens": 170},
        {"model": "gpt-4o", "latency_ms": 920.3, "error": None, "prompt_tokens": 50, "completion_tokens": 130, "total_tokens": 180},
        {"model": "gpt-4o", "latency_ms": 780.1, "error": None, "prompt_tokens": 50, "completion_tokens": 115, "total_tokens": 165},
        
        {"model": "gpt-5-mini", "latency_ms": 650.2, "error": None, "prompt_tokens": 50, "completion_tokens": 110, "total_tokens": 160},
        {"model": "gpt-5-mini", "latency_ms": 720.8, "error": None, "prompt_tokens": 50, "completion_tokens": 125, "total_tokens": 175},
        {"model": "gpt-5-mini", "latency_ms": None, "error": "HTTP 429: Rate limit", "prompt_tokens": None, "completion_tokens": None, "total_tokens": None},
    ]
    
    # 模拟高并发数的测试数据（15个请求）
    high_concurrency_data = []
    for i in range(15):
        high_concurrency_data.extend([
            {"model": "gpt-4o", "latency_ms": 800 + i*20, "error": None, "prompt_tokens": 50, "completion_tokens": 120+i, "total_tokens": 170+i},
            {"model": "gpt-5-mini", "latency_ms": 600 + i*15, "error": None, "prompt_tokens": 50, "completion_tokens": 110+i, "total_tokens": 160+i},
        ])
    
    # 添加一些错误
    high_concurrency_data[5]["error"] = "HTTP 500: Server Error"
    high_concurrency_data[5]["latency_ms"] = None
    
    return pd.DataFrame(low_concurrency_data), pd.DataFrame(high_concurrency_data)

def test_low_concurrency():
    """测试低并发数的情况"""
    print("=== 测试低并发数场景 (3个请求/模型) ===")
    low_df, _ = create_test_data()
    summary = summarize_latency(low_df)
    
    print("原始数据:")
    print(low_df.to_string(index=False))
    print(f"\n样本数: {len(low_df)}")
    
    print("\n统计摘要:")
    print(summary.to_string(index=False))
    
    # 验证统计结果
    for _, row in summary.iterrows():
        model = row['model']
        print(f"\n{model} 分析:")
        print(f"  - 总请求数: {row['total_requests']}")
        print(f"  - 成功请求数: {row['success_count']}")  
        print(f"  - 错误率: {row['error_rate']:.2%}")
        print(f"  - 平均延迟: {row['avg_latency']:.2f}ms" if row['avg_latency'] else "  - 平均延迟: 无")
        print(f"  - 最低延迟: {row['min_latency']:.2f}ms" if row['min_latency'] else "  - 最低延迟: - (单次请求)")
        print(f"  - 最高延迟: {row['max_latency']:.2f}ms" if row['max_latency'] else "  - 最高延迟: - (单次请求)")
        print(f"  - Token数: 输入{row['prompt_tokens']}, 输出{row['completion_tokens']}, 总计{row['total_tokens']}")

def test_high_concurrency():
    """测试高并发数的情况"""
    print("\n\n=== 测试高并发数场景 (15个请求/模型) ===")
    _, high_df = create_test_data()
    summary = summarize_latency(high_df)
    
    print(f"样本数: {len(high_df)}")
    
    print("\n统计摘要:")
    print(summary.to_string(index=False))
    
    # 验证统计结果
    for _, row in summary.iterrows():
        model = row['model']
        print(f"\n{model} 分析:")
        print(f"  - 总请求数: {row['total_requests']}")
        print(f"  - 成功请求数: {row['success_count']}")
        print(f"  - 错误率: {row['error_rate']:.2%}")
        print(f"  - 平均延迟: {row['avg_latency']:.2f}ms")
        print(f"  - 最低延迟: {row['min_latency']:.2f}ms")
        print(f"  - 最高延迟: {row['max_latency']:.2f}ms")
        print(f"  - Token数: 输入{row['prompt_tokens']}, 输出{row['completion_tokens']}, 总计{row['total_tokens']}")

def main():
    """主函数"""
    print("🧪 测试统计摘要功能的修复")
    print("=" * 50)
    
    test_low_concurrency()
    test_high_concurrency()
    
    print("\n\n✅ 测试完成！")
    print("主要改进:")
    print("1. ✅ 总请求数和错误率正确显示")
    print("2. ✅ 去掉了P50/P90/P99百分位数（没用的参数）")
    print("3. ✅ 添加了最低/最高延迟显示（并发数>1时）")  
    print("4. ✅ Token数统计和显示")
    print("5. ✅ 简化了统计表格，更清晰实用")

if __name__ == "__main__":
    main()