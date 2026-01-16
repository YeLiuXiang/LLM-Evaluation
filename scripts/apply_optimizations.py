"""一键应用架构优化"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


def run_command(cmd: str, description: str) -> bool:
    """运行命令并显示结果"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"✅ {description} 完成")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        if e.stderr:
            print(e.stderr)
        return False


def main():
    """执行优化步骤"""
    print("=" * 70)
    print("🚀 LLM-Evaluation 架构优化 - 一键应用")
    print("=" * 70)
    
    steps = [
        {
            "cmd": f"{sys.executable} -m pip install python-dotenv pydantic-settings --quiet",
            "desc": "安装新依赖 (python-dotenv, pydantic-settings)",
            "required": True
        },
        {
            "cmd": f"{sys.executable} scripts/fix_model_names.py",
            "desc": "修复模型名称空格问题",
            "required": True
        }
    ]
    
    success_count = 0
    total_count = len(steps)
    
    for step in steps:
        if run_command(step["cmd"], step["desc"]):
            success_count += 1
        elif step.get("required", False):
            print("\n❌ 关键步骤失败，优化中止")
            sys.exit(1)
    
    # 创建 .env 文件（如果不存在）
    print("\n🔧 检查环境变量配置...")
    env_file = BASE_DIR / ".env"
    env_example = BASE_DIR / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("📝 创建 .env 文件...")
        env_file.write_text(env_example.read_text(encoding='utf-8'), encoding='utf-8')
        print("✅ .env 文件已创建（使用默认配置）")
        print("💡 提示：您可以编辑 .env 文件来自定义配置")
    elif env_file.exists():
        print("✅ .env 文件已存在")
    else:
        print("⚠️  警告：未找到 .env.example，跳过 .env 创建")
    
    # 创建日志目录
    print("\n🔧 创建日志目录...")
    logs_dir = BASE_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    print("✅ 日志目录已创建")
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 优化完成统计")
    print("=" * 70)
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失败: {total_count - success_count}/{total_count}")
    
    print("\n" + "=" * 70)
    print("🎉 架构优化应用完成！")
    print("=" * 70)
    
    print("\n📖 下一步操作：")
    print("1. 查看优化文档：")
    print("   - ARCHITECTURE_OPTIMIZATION.md （完整优化方案）")
    print("   - MIGRATION_GUIDE.md （迁移指南）")
    print()
    print("2. 测试优化后的服务：")
    print("   python -m uvicorn backend.main_optimized:app --reload")
    print()
    print("3. 或继续使用现有服务：")
    print("   python start_server.py")
    print()
    print("4. 配置环境变量（可选）：")
    print("   编辑 .env 文件")
    print()
    
    if success_count == total_count:
        print("✅ 所有优化步骤已成功应用！")
        return 0
    else:
        print("⚠️  部分优化步骤失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
