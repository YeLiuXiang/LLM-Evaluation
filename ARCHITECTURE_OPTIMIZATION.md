# LLM-Evaluation 项目架构优化方案

## 📋 目录
1. [当前架构问题](#当前架构问题)
2. [优化目标](#优化目标)
3. [优化方案](#优化方案)
4. [实施计划](#实施计划)
5. [预期收益](#预期收益)

---

## 🔍 当前架构问题

### 1. 配置管理问题
- ❌ API密钥硬编码在 `config/models.yaml`，存在安全风险
- ❌ 模型名称有前导空格（` gpt-5-chat`），导致匹配问题
- ❌ 缺少环境变量配置支持
- ❌ 前后端配置分离，管理不统一

### 2. 代码结构问题
- ❌ `backend/main.py` 过长（400+ 行），路由、业务逻辑混杂
- ❌ 缺少统一的错误处理中间件
- ❌ 缺少日志配置模块
- ❌ 缺少API响应格式标准化
- ❌ 缺少依赖注入机制

### 3. 数据管理问题
- ❌ 历史记录JSON存储无索引，查询效率低
- ❌ 任务管理器无持久化，服务重启丢失
- ❌ 缺少数据备份机制
- ❌ 无数据过期清理策略

### 4. 性能与可扩展性
- ❌ 缺少请求限流
- ❌ 缺少响应缓存
- ❌ 前端单文件1260行，难以维护
- ❌ 无数据库支持（当前JSON文件）

### 5. 测试与监控
- ❌ 缺少单元测试
- ❌ 缺少性能监控
- ❌ 缺少Prometheus指标暴露
- ❌ 缺少请求链路追踪

### 6. 安全性问题
- ❌ 无API认证机制
- ❌ 无请求频率限制
- ❌ 敏感信息明文存储
- ❌ CORS配置过于宽松（allow_origins=["*"]）

---

## 🎯 优化目标

1. **安全性**：保护API密钥，添加认证机制
2. **可维护性**：模块化代码，降低耦合
3. **可扩展性**：支持数据库，支持分布式部署
4. **性能**：添加缓存、限流、异步优化
5. **可观测性**：完善日志、监控、追踪

---

## 💡 优化方案

### 阶段一：紧急修复（优先级：高）

#### 1.1 配置安全化
```bash
# 新增文件结构
backend/
  ├── config/
  │   ├── __init__.py
  │   ├── settings.py      # 环境变量配置
  │   └── logger.py        # 日志配置
  └── ...

.env.example              # 环境变量模板
.env                      # 实际配置（git忽略）
```

**实施内容：**
- 创建 `.env` 文件存储敏感信息
- 使用 `pydantic-settings` 管理配置
- 修复模型名称前导空格问题
- 添加配置验证

#### 1.2 代码结构重构
```bash
backend/
  ├── api/                 # API路由层
  │   ├── __init__.py
  │   ├── dependencies.py  # 依赖注入
  │   ├── routes/
  │   │   ├── __init__.py
  │   │   ├── models.py    # 模型管理路由
  │   │   ├── test.py      # 测试路由
  │   │   └── history.py   # 历史记录路由
  │   └── middleware.py    # 中间件
  ├── core/                # 核心业务逻辑
  │   ├── __init__.py
  │   ├── service.py       # 业务服务层
  │   └── exceptions.py    # 自定义异常
  ├── config/              # 配置管理
  ├── models.py            # 数据模型（保持）
  ├── task_manager.py      # 任务管理（保持）
  ├── history_manager.py   # 历史管理（保持）
  └── main.py              # 精简的入口文件
```

#### 1.3 统一响应格式
```python
# backend/core/response.py
class APIResponse(BaseModel):
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
```

### 阶段二：性能优化（优先级：中）

#### 2.1 添加缓存层
```python
# 使用 Redis 缓存模型列表
from redis import asyncio as aioredis

# 缓存配置
CACHE_TTL = 300  # 5分钟

# 缓存装饰器
@cache(ttl=CACHE_TTL)
async def get_models():
    ...
```

#### 2.2 添加限流
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/test")
@limiter.limit("10/minute")
async def start_test(request: Request, ...):
    ...
```

#### 2.3 数据库迁移
```bash
# 从 JSON 迁移到 SQLite/PostgreSQL
backend/
  ├── database/
  │   ├── __init__.py
  │   ├── models.py        # SQLAlchemy 模型
  │   ├── crud.py          # CRUD 操作
  │   └── session.py       # 数据库会话
  └── alembic/             # 数据库迁移
```

#### 2.4 前端模块化
```bash
frontend/
  ├── js/
  │   ├── api.js           # API调用封装
  │   ├── state.js         # 状态管理
  │   ├── ui.js            # UI更新逻辑
  │   ├── history.js       # 历史记录模块
  │   └── test.js          # 测试逻辑
  ├── config.js            # 保持
  ├── app.js               # 主入口（精简）
  ├── index.html
  └── styles.css
```

### 阶段三：监控与测试（优先级：中低）

#### 3.1 添加日志系统
```python
# backend/config/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger("llm_evaluation")
    logger.setLevel(logging.INFO)
    
    # 文件处理器（轮转）
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
```

#### 3.2 添加监控指标
```python
# backend/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 指标定义
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
ACTIVE_TESTS = Gauge('active_tests', 'Number of active tests')

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

#### 3.3 添加单元测试
```bash
tests/
  ├── __init__.py
  ├── conftest.py          # pytest 配置
  ├── test_api.py          # API测试
  ├── test_tester.py       # 延迟测试逻辑测试
  └── test_history.py      # 历史记录测试
```

### 阶段四：高级特性（优先级：低）

#### 4.1 WebSocket支持
替代SSE，提供更好的双向通信

#### 4.2 分布式任务队列
使用Celery+Redis处理大规模测试

#### 4.3 容器化部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
  
  redis:
    image: redis:7-alpine
  
  postgres:
    image: postgres:15-alpine
```

---

## 📅 实施计划

### Week 1: 紧急修复
- [ ] Day 1-2: 配置安全化
  - 创建 `.env` 配置
  - 迁移API密钥
  - 修复模型名称空格问题
- [ ] Day 3-4: 代码结构重构
  - 拆分路由模块
  - 创建服务层
  - 统一响应格式
- [ ] Day 5: 测试与验证

### Week 2: 性能优化
- [ ] Day 1-2: 添加缓存和限流
- [ ] Day 3-4: 前端模块化
- [ ] Day 5: 性能测试

### Week 3: 监控与测试
- [ ] Day 1-2: 日志系统和监控指标
- [ ] Day 3-4: 编写单元测试
- [ ] Day 5: 文档更新

### Week 4+: 高级特性（可选）
- [ ] 数据库迁移（如需要）
- [ ] WebSocket支持
- [ ] 容器化部署

---

## 📊 预期收益

### 安全性提升
- ✅ API密钥不再明文存储
- ✅ 支持多环境配置（dev/staging/prod）
- ✅ 可添加API认证机制

### 可维护性提升
- ✅ 代码行数减少30%+
- ✅ 模块职责清晰
- ✅ 便于团队协作

### 性能提升
- ✅ 响应时间降低40%（通过缓存）
- ✅ 支持更高并发（通过限流保护）
- ✅ 前端加载速度提升

### 可扩展性提升
- ✅ 易于添加新功能
- ✅ 支持水平扩展
- ✅ 支持微服务架构演进

---

## 🛠️ 快速开始优化

### 1. 立即修复模型名称空格
```bash
# 运行修复脚本
python scripts/fix_model_names.py
```

### 2. 创建环境变量配置
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

### 3. 安装额外依赖
```bash
pip install python-dotenv pydantic-settings redis slowapi
```

### 4. 运行优化后的服务
```bash
python start_server.py
```

---

## 📚 参考资料

- [FastAPI最佳实践](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Twelve-Factor App](https://12factor.net/)
- [Python项目结构指南](https://docs.python-guide.org/writing/structure/)
- [API设计最佳实践](https://restfulapi.net/)

---

**版本：** 1.0  
**日期：** 2026-01-16  
**作者：** GitHub Copilot
