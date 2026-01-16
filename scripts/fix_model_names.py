"""修复模型配置文件中的名称空格问题"""
import sys
from pathlib import Path

# 添加项目根目录到路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import yaml


def fix_model_names():
    """修复模型名称中的前导/尾随空格"""
    config_path = BASE_DIR / "config" / "models.yaml"
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    # 读取配置
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    if not config or "models" not in config:
        print("❌ 配置文件格式错误")
        return False
    
    # 统计和修复
    fixed_count = 0
    models = config.get("models", [])
    
    for model in models:
        if "name" in model:
            original_name = model["name"]
            fixed_name = str(original_name).strip()
            
            if original_name != fixed_name:
                print(f"修复: '{original_name}' -> '{fixed_name}'")
                model["name"] = fixed_name
                fixed_count += 1
    
    # 保存修复后的配置
    if fixed_count > 0:
        # 备份原文件
        backup_path = config_path.with_suffix(".yaml.backup")
        with config_path.open("r", encoding="utf-8") as f:
            backup_content = f.read()
        with backup_path.open("w", encoding="utf-8") as f:
            f.write(backup_content)
        print(f"✅ 已备份原文件到: {backup_path}")
        
        # 保存修复后的配置
        with config_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
        
        print(f"✅ 已修复 {fixed_count} 个模型名称")
        print(f"✅ 配置已保存到: {config_path}")
        return True
    else:
        print("✅ 没有发现需要修复的模型名称")
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 修复模型配置文件中的名称空格")
    print("=" * 60)
    print()
    
    success = fix_model_names()
    
    print()
    if success:
        print("✅ 修复完成！")
    else:
        print("❌ 修复失败！")
        sys.exit(1)
