"""快速启动脚本 - LLM 延迟测试器（FastAPI 版本）"""
import sys
import subprocess
from pathlib import Path

def main():
    """启动 FastAPI 服务器"""
    
    print("=" * 60)
    print("🚀 LLM 延迟测试器 - FastAPI 版本")
    print("=" * 60)
    print()
    
    # 检查依赖
    print("📦 检查依赖...")
    try:
        import fastapi
        import uvicorn
        import sse_starlette
        print("✅ 依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e.name}")
        print("\n请运行以下命令安装依赖：")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    print()
    
    # 检查配置文件
    config_path = Path(__file__).parent / "config" / "models.yaml"
    if not config_path.exists():
        print("⚠️  警告: config/models.yaml 不存在")
        print("请创建配置文件并添加模型信息")
        print()
    else:
        print("✅ 配置文件存在")
        print()
    
    # 启动服务器
    print("🌐 启动服务器...")
    print("访问地址: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    try:
        # 运行 uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
