# 架构优化迁移指南

## 📋 概述

本文档指导您如何将现有代码逐步迁移到优化后的架构。建议采用**渐进式迁移**策略，避免大规模重构带来的风险。

---

## ✅ 已完成的优化

### 1. 配置管理系统 ✅
- ✅ 创建 `backend/config/settings.py` - 环境变量配置
- ✅ 创建 `backend/config/logger.py` - 日志配置
- ✅ 创建 `.env.example` - 环境变量模板
- ✅ 修复模型名称空格问题

### 2. 核心模块 ✅
- ✅ 创建 `backend/core/response.py` - 统一响应格式
- ✅ 创建 `backend/core/exceptions.py` - 自定义异常
- ✅ 创建 `backend/main_optimized.py` - 优化后的主文件示例

### 3. 工具脚本 ✅
- ✅ 创建 `scripts/fix_model_names.py` - 修复模型名称

### 4. 依赖更新 ✅
- ✅ 添加 `python-dotenv` - 环境变量加载
- ✅ 添加 `pydantic-settings` - 配置管理
- ✅ 更新 `.gitignore` - 保护敏感信息

---

## 🚀 快速开始

### 步骤1: 安装新依赖

```bash
pip install python-dotenv pydantic-settings
```

### 步骤2: 创建环境变量文件

```bash
# 复制模板
cp .env.example .env

# 编辑 .env 文件（可选，使用默认值也可以）
# 注意：.env 文件已加入 .gitignore，不会被提交
```

### 步骤3: 测试优化后的服务（可选）

```bash
# 运行优化后的示例服务
python -m uvicorn backend.main_optimized:app --reload

# 访问 http://localhost:8000/api/health 查看效果
# 访问 http://localhost:8000/api/config/info 查看配置
```

### 步骤4: 继续使用现有服务

```bash
# 现有服务不受影响，可以继续使用
python start_server.py
```

---

## 📖 迁移路径

### 方案A: 保守迁移（推荐）

**适合**：希望保持现有功能稳定，逐步引入新特性

1. **第1周：配置迁移**
   - 将 `config/models.yaml` 中的敏感信息移到 `.env`
   - 在 `backend/main.py` 中引入 `settings`
   - 逐步替换硬编码配置

2. **第2周：日志优化**
   - 引入 `setup_logger()`
   - 替换现有的 `logging` 配置
   - 添加日志轮转

3. **第3周：响应格式统一**
   - 新增的路由使用 `success_response` / `error_response`
   - 现有路由保持不变

4. **第4周：异常处理**
   - 添加全局异常处理器
   - 新增的业务逻辑使用自定义异常

### 方案B: 完全重构（高级）

**适合**：追求最佳实践，愿意投入更多时间

参考 `ARCHITECTURE_OPTIMIZATION.md` 中的完整方案，进行模块拆分和重构。

---

## 🔧 逐步迁移示例

### 示例1: 迁移配置管理

**原代码** (`backend/main.py`):
```python
CONFIG_PATH = BASE_DIR / "config" / "models.yaml"

def load_model_configs():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return raw.get("models", [])
```

**优化后**:
```python
from backend.config import settings

def load_model_configs():
    config_path = settings.models_config_path
    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return raw.get("models", [])
```

**优势**：
- ✅ 配置路径集中管理
- ✅ 支持环境变量覆盖
- ✅ 便于测试和部署

---

### 示例2: 迁移日志

**原代码**:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

**优化后**:
```python
from backend.config import setup_logger

logger = setup_logger("llm_evaluation")
```

**优势**：
- ✅ 自动配置文件日志轮转
- ✅ 统一日志格式
- ✅ 支持通过 `.env` 调整日志级别

---

### 示例3: 迁移路由响应格式

**原代码**:
```python
@app.get("/api/models")
async def get_models():
    try:
        configs = load_model_configs()
        return {"models": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**优化后**:
```python
from backend.core import success_response, error_response, ConfigurationException

@app.get("/api/models")
async def get_models():
    try:
        configs = load_model_configs()
        return success_response(
            data={"models": configs},
            message="模型列表加载成功"
        )
    except Exception as e:
        raise ConfigurationException(str(e))
```

**优势**：
- ✅ 响应格式统一（包含 success, data, message, timestamp）
- ✅ 异常类型明确
- ✅ 全局异常处理器自动处理

---

### 示例4: 使用自定义异常

**原代码**:
```python
@app.get("/api/models/{model_name}")
async def get_model_info(model_name: str):
    configs = load_model_configs()
    if model_name not in configs:
        raise HTTPException(status_code=404, detail=f"模型 '{model_name}' 不存在")
    return {"model": configs[model_name]}
```

**优化后**:
```python
from backend.core import ModelNotFoundException, success_response

@app.get("/api/models/{model_name}")
async def get_model_info(model_name: str):
    configs = load_model_configs()
    if model_name not in configs:
        raise ModelNotFoundException(model_name)
    
    return success_response(
        data={"model": configs[model_name]},
        message=f"模型 {model_name} 信息"
    )
```

**优势**：
- ✅ 异常语义更清晰
- ✅ 携带结构化的错误详情
- ✅ 便于前端统一处理

---

## 🧪 测试新功能

### 测试配置系统

```bash
# 设置环境变量
export LOG_LEVEL=DEBUG
export DEBUG=False

# 或在 .env 文件中配置
# LOG_LEVEL=DEBUG
# DEBUG=False

# 运行测试
python -c "from backend.config import settings; print(f'日志级别: {settings.LOG_LEVEL}')"
```

### 测试日志系统

```python
from backend.config import setup_logger

logger = setup_logger("test")
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")

# 检查日志文件: logs/app.log
```

### 测试响应格式

```python
from backend.core import success_response, error_response

# 成功响应
response = success_response(data={"value": 123}, message="操作成功")
print(response)
# {'success': True, 'data': {'value': 123}, 'message': '操作成功', 'error': None, 'timestamp': '...'}

# 错误响应
response = error_response(error="模型不存在", message="查询失败")
print(response)
# {'success': False, 'data': None, 'message': '查询失败', 'error': '模型不存在', 'timestamp': '...'}
```

---

## 📊 迁移检查清单

### 配置管理
- [ ] 已创建 `.env` 文件
- [ ] 敏感信息已移出 `models.yaml`
- [ ] 代码中引入 `settings`
- [ ] 测试不同环境配置

### 日志系统
- [ ] 已使用 `setup_logger()`
- [ ] 日志文件正常生成
- [ ] 日志轮转正常工作
- [ ] 日志级别可配置

### 响应格式
- [ ] 新路由使用统一响应格式
- [ ] 错误处理统一
- [ ] 前端适配新格式（如需要）

### 异常处理
- [ ] 已添加全局异常处理器
- [ ] 使用自定义异常类
- [ ] 异常信息结构化

---

## 🆘 常见问题

### Q1: 是否必须立即迁移所有代码？

**A:** 不需要。新旧代码可以共存，建议采用渐进式迁移。

### Q2: `.env` 文件会被提交到 Git 吗？

**A:** 不会。`.env` 已加入 `.gitignore`，只会提交 `.env.example` 模板。

### Q3: 如何在生产环境配置？

**A:** 
1. 复制 `.env.example` 为 `.env`
2. 填入生产环境的配置
3. 或使用环境变量（推荐）：`export LOG_LEVEL=INFO`

### Q4: 优化后性能会受影响吗？

**A:** 不会。配置和日志模块的开销极小，且提供了更好的性能（如通过缓存）。

### Q5: 如何回退到旧版本？

**A:** 现有的 `backend/main.py` 未被修改，随时可以继续使用。

---

## 📚 下一步

1. ✅ **已完成**：基础优化（配置、日志、响应格式、异常处理）
2. **可选**：性能优化（缓存、限流）- 参考 `ARCHITECTURE_OPTIMIZATION.md` 阶段二
3. **可选**：监控与测试 - 参考 `ARCHITECTURE_OPTIMIZATION.md` 阶段三
4. **可选**：高级特性（数据库、WebSocket）- 根据需求决定

---

## 💬 反馈

如有问题或建议，请查看：
- 完整优化方案：`ARCHITECTURE_OPTIMIZATION.md`
- 项目文档：`README.md`
- 示例代码：`backend/main_optimized.py`

---

**最后更新：** 2026-01-16  
**版本：** 1.0
