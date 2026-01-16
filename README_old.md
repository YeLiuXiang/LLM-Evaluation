# 🚀 LLM 延迟测试器

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 一个专业的 LLM 模型延迟测试工具，支持实时流式数据推送、多模型并发测试、完整的统计分析和历史记录管理。

**主要特性** ✨
- 🎯 **实时流式显示** - SSE 推送实时输出，支持 10+ 模型并发
- 📊 **完整统计分析** - 延迟、吞吐量、首Token延迟等多维度指标
- 💾 **历史记录管理** - 自动保存测试结果，支持查看和导出
- ⚙️ **灵活配置管理** - 支持环境变量配置、多环境部署
- 📈 **性能优异** - 每秒支持 200+ 次更新，无性能瓶颈
- 🔒 **生产就绪** - 规范的代码结构、完善的错误处理、详细的文档

## 📁 项目结构

```
LLM-Evaluation/
├── backend/
│   ├── config/                # ⭐ 配置管理系统
│   │   ├── settings.py       # 环境变量配置
│   │   └── logger.py         # 日志配置
│   ├── core/                  # ⭐ 核心模块
│   │   ├── response.py       # 统一响应格式
│   │   └── exceptions.py     # 自定义异常
│   ├── main.py               # FastAPI 入口
│   ├── main_optimized.py     # ⭐ 优化示例
│   ├── task_manager.py       # 任务管理器
│   ├── history_manager.py    # 历史记录管理
│   └── models.py             # 数据模型
├── frontend/
│   ├── index.html            # 主页面
│   ├── app.js                # 前端逻辑
│   ├── config.js             # 前端配置
│   └── styles.css            # 样式表
├── tester/
│   ├── latency_tester.py    # 延迟测试逻辑
│   └── metrics.py            # 指标计算
├── scripts/                   # ⭐ 工具脚本
│   ├── fix_model_names.py   # 修复模型名称
│   └── apply_optimizations.py # 一键优化
├── config/
│   └── models.yaml          # 模型配置
├── .env.example             # ⭐ 环境变量模板
├── requirements.txt         # Python 依赖
├── start_server.py          # 快速启动脚本
├── ARCHITECTURE_OPTIMIZATION.md  # ⭐ 架构优化方案
├── MIGRATION_GUIDE.md            # ⭐ 迁移指南
├── OPTIMIZATION_SUMMARY.md       # ⭐ 优化总结
└── QUICK_REFERENCE.md            # ⭐ 快速参考
```

**⭐ 表示架构优化新增内容**

## 🚀 快速开始

### 前置要求

- Python 3.10+
- pip 或 conda
- Azure OpenAI API 密钥和端点

### 1️⃣ 克隆项目

```bash
git clone https://github.com/your-username/LLM-Evaluation.git
cd LLM-Evaluation
```

### 2️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 3️⃣ 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件（可选，使用默认值也可以）
# 详见 .env.example 或 QUICK_REFERENCE.md
```

### 4️⃣ 配置模型

编辑 `config/models.yaml`：

```yaml
models:
  - name: gpt-4o
    endpoint: "https://your-resource.openai.azure.com"
    api_key: "your-api-key"
    api_version: "2024-02-01"
```

### 5️⃣ 启动服务

```bash
# 方法一：一键启动（推荐）
python start_server.py

# 方法二：直接运行
python -m uvicorn backend.main:app --reload

# 方法三：生产环境部署
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

### 6️⃣ 访问应用

打开浏览器：
```
http://localhost:8000
```

## 📚 文档导航

| 文档 | 说明 | 适合对象 |
|------|------|----------|
| **QUICK_REFERENCE.md** | 快速参考，快速开始使用 | 所有人 |
| **OPTIMIZATION_SUMMARY.md** | 优化总结，了解最新改进 | 项目负责人、开发者 |
| **MIGRATION_GUIDE.md** | 迁移指南，应用架构优化 | 开发者 |
| **ARCHITECTURE_OPTIMIZATION.md** | 完整方案，深入了解架构 | 架构师、技术负责人 |

## 📖 使用说明

### 🎯 主要功能

#### 1. 多模型并发测试
- ✅ 支持同时测试多个 LLM 模型
- ✅ 灵活配置并发数和迭代次数
- ✅ 真正的局部更新，互不影响

#### 2. 实时流式推送
- ✅ SSE 服务器推送事件
- ✅ 毫秒级实时更新
- ✅ 支持 10+ 模型并发，每秒 200+ 次更新

#### 3. 完整的统计分析
- ✅ 延迟统计（最小/最大/平均值）
- ✅ 首Token延迟（仅流式）
- ✅ 错误率和成功率统计
- ✅ 吞吐量分析

#### 4. 历史记录管理
- ✅ 自动保存测试结果
- ✅ 支持查看历史测试
- ✅ CSV 导出功能
- ✅ 最近 100 条记录

#### 5. 灵活的配置管理
- ✅ 环境变量支持（`.env`）
- ✅ 前端配置文件化（`frontend/config.js`）
- ✅ 后端配置集中管理
- ✅ 多环境支持（dev/staging/prod）

### 📖 使用说明

#### 前端配置 (`frontend/config.js`)

前端所有可配置参数已集中到 `frontend/config.js` 文件中，无需修改代码即可调整默认值。

**预设问题列表**：包含 5 个不同复杂度等级的问题
```javascript
presetQuestions: [
    { label: "入门：how to learn english", value: "..." },
    { label: "基础：Explain how transformer attention...", value: "..." },
    { label: "进阶：Compare gpt-5.1 and gpt-4o...", value: "..." },
    { label: "高级：Design a roadmap for building...", value: "..." },
    { label: "专家：Estimate the trade-offs...", value: "..." }
]
```

**默认测试参数**：
```javascript
defaultParams: {
    concurrency: 3,          // 默认并发数
    iterations: 1,           // 默认迭代次数
    maxTokens: 1000,         // 默认最大Token数
    temperature: 0.7,        // 默认温度
    stream: true             // 默认启用流式响应
}
```

**参数范围限制**：用于前端表单验证
```javascript
limits: {
    concurrency: { min: 1, max: 20 },
    iterations: { min: 1, max: 50 },
    maxTokens: { min: 10, max: 4000, step: 10 },
    temperature: { min: 0, max: 2, step: 0.1 }
}
```

**新增模型默认配置**：
```javascript
newModelDefaults: {
    maxTokens: 1000,
    temperature: 0.7,
    concurrency: 1,
    iterations: 1,
    stream: true,
    apiVersion: "2024-12-01-preview"
}
```

修改这些配置无需编辑 HTML 或 JavaScript 代码，直接在 `config.js` 中修改即可生效。

#### 后端模型配置 (`config/models.yaml`)

编辑 `config/models.yaml` 文件，添加你的模型配置：

```yaml
models:
  - name: gpt-4o
    endpoint: "https://your-resource.openai.azure.com"
    api_key: "your-api-key"
    api_version: "2024-02-01"
    max_tokens: 1000
    temperature: 0.7
```

### 主界面布局

1. **左侧配置栏（320px）**
  - 模型选择（多选）
  - 预设问题下拉（从 `frontend/config.js` 读取，支持自定义扩展）
  - 测试问题输入（支持自定义内容）
  - 参数配置（并发、迭代、tokens、temperature）
  - 流式开关
  - 开始/停止按钮

2. **主内容区（固定 5 列横向滚动）**
   - 每列显示一个模型的实时输出
   - 卡片高度：70vh
   - 超过 5 个模型时，横向滚动查看
   - 每个卡片包含：头部标题、输出内容、状态和耗时

### 操作流程

1. **选择模型**：在左侧勾选要测试的模型（默认全选）
2. **输入问题**：可从“预设问题”下拉选择 `how to learn english` 或其他多复杂度问题，也可直接自定义内容
3. **配置参数**：根据需要调整并发数、迭代次数等参数
4. **开始测试**：点击"开始测试"按钮
5. **查看结果**：实时观察各模型的流式输出
6. **查看统计**：测试完成后自动显示统计摘要表
7. **下载结果**：点击"下载结果"按钮导出CSV文件
8. **历史记录**：点击"📜 历史记录"按钮查看之前的测试结果

### 功能特性

✅ **真正的局部更新**：单个模型输出变化不影响其他模型卡片  
✅ **流式实时显示**：通过 SSE 接收流式数据，实时更新  
✅ **固定 5 列布局**：每列精确 20% 宽度，横向滚动查看更多  
✅ **性能优异**：支持 10+ 模型并发，每秒 200+ 次更新  
✅ **状态指示**：连接中、流式输出、已完成、错误等状态  
✅ **统计摘要**：测试完成后显示总请求数、成功/失败数、错误率、最小/最大延迟等，流式请求额外显示首Token延迟统计  
✅ **结果下载**：导出 CSV 格式的统计摘要表数据（仅包含聚合数据，不包含模型响应内容）  
✅ **配置文件化**：预设问题和默认参数通过 `frontend/config.js` 集中管理，无需修改代码  
✅ **参数验证**：前端表单根据 `config.js` 中的 `limits` 自动验证参数范围  
✅ **历史记录**：自动保存每次测试的统计摘要，支持查看和管理历史测试结果

## 🔧 API 接口说明

### GET /api/models
获取可用模型列表

**响应示例：**
```json
{
  "models": [
    {
      "name": "gpt-4o",
      "endpoint": "https://xxx.openai.azure.com",
      "api_version": "2024-02-01"
    }
  ]
}
```

### POST /api/test
启动测试任务

**请求体：**
```json
{
  "models": ["gpt-4o", "gpt-35-turbo"],
  "question": "Explain transformer attention",
  "concurrency": 1,
  "iterations": 1,
  "max_tokens": 1000,
  "temperature": 0.7,
  "stream": true
}
```

**响应：**
```json
{
  "task_id": "uuid-string",
  "status": "started",
  "message": "已启动 2 个模型的测试任务"
}
```

### GET /api/stream/{task_id}
SSE 流式推送测试结果

**事件类型：**

1. **chunk** - 流式数据块
```json
{
  "model": "gpt-4o",
  "chunk": "Hello",
  "request_id": 1,
  "status": "streaming"
}
```

2. **summary** - 统计摘要
```json
[
  {
    "model": "gpt-4o",
    "total_requests": 10,
    "success_count": 10,
    "error_count": 0,
    "error_rate": 0.0,
    "min_latency": 1000.0,
    "max_latency": 1500.0,
    "avg_latency": 1234.56,
    "first_token_avg": 256.78,
    "first_token_min": 200.0,
    "first_token_max": 300.0
  }
]
```

**延迟统计说明：**
- `avg_latency/min_latency/max_latency`：完整响应延迟（从请求开始到接收完所有内容）
- `first_token_avg/min/max`：仅流式请求有效，统计第一个token返回的延迟

3. **complete** - 完成信号
```json
{
  "status": "completed"
}
```

4. **error** - 错误信息
```json
{
  "error": "错误描述"
}
```

### GET /api/history
获取历史记录列表

**查询参数：**
- `limit`: 返回的最大记录数（默认50）

**响应示例：**
```json
{
  "status": "success",
  "count": 10,
  "records": [
    {
      "id": "20260116_143022_123456",
      "timestamp": "2026-01-16T14:30:22.123456",
      "model_count": 3,
      "question": "how to learn english",
      "models": ["gpt-4o", "gpt-35-turbo", "gpt-4"]
    }
  ]
}
```

### GET /api/history/{record_id}
获取历史记录详情

**响应示例：**
```json
{
  "status": "success",
  "record": {
    "id": "20260116_143022_123456",
    "timestamp": "2026-01-16T14:30:22.123456",
    "test_config": {
      "question": "how to learn english",
      "models": ["gpt-4o", "gpt-35-turbo"],
      "concurrency": 3,
      "iterations": 1,
      "max_tokens": 1000,
      "temperature": 0.7,
      "stream": true
    },
    "summary": [
      {
        "model": "gpt-4o",
        "avg_latency": 1234.56,
        ...
      }
    ],
    "model_count": 2
  }
}
```

### DELETE /api/history/{record_id}
删除指定历史记录

### DELETE /api/history
清空所有历史记录

## 🐛 故障排查

### 1. 端口被占用
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### 2. 模块导入错误
确保在项目根目录运行，或检查 Python 路径：
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/LLM-Evaluation"
```

### 3. CORS 错误
后端已配置允许所有来源，如仍有问题，检查浏览器控制台

### 4. SSE 连接断开
- 检查网络连接
- 查看后端日志
- 确认任务未超时（默认无超时限制）

## 📊 性能优化建议

1. **并发控制**：建议单模型并发数不超过 10
2. **模型数量**：建议同时测试不超过 15 个模型
3. **迭代次数**：首次测试建议 1-5 次，压测时可增加到 20+
4. **流式输出**：大量文本建议启用流式，提升体验
5. **参数配置**：通过修改 `frontend/config.js` 中的 `defaultParams` 快速调整应用全局默认值

## 🔄 配置自定义

### 添加预设问题

在 `frontend/config.js` 中修改 `presetQuestions` 数组：

```javascript
presetQuestions: [
    {
        label: "自定义标签：问题内容",
        value: "完整的问题文本内容"
    },
    // 添加更多问题...
]
```

### 修改默认参数

在 `frontend/config.js` 中修改 `defaultParams` 对象：

```javascript
defaultParams: {
    concurrency: 5,        // 改为 5 并发
    iterations: 3,         // 改为 3 次迭代
    maxTokens: 2000,       // 改为 2000 tokens
    temperature: 0.5,      // 改为 0.5 温度
    stream: false          // 改为禁用流式
}
```

### 调整参数验证范围

在 `frontend/config.js` 中修改 `limits` 对象，调整前端表单验证范围。

### 新增模型默认配置

修改 `newModelDefaults` 对象中的值，应用到新增模型的初始值。

## 🔄 从 Streamlit 版本迁移

如果你之前使用 Streamlit 版本（`app.py`），现在可以：

1. **保留旧版本**：Streamlit 版本仍可用，运行 `streamlit run app.py`
2. **切换到新版本**：运行 `python start_server.py` 使用 FastAPI 版本
3. **数据共享**：两个版本共享相同的 `config/models.yaml` 和 `tester/` 模块

## 🚢 生产部署建议

### Docker 部署

创建 `Dockerfile`：
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

运行：
```bash
docker build -t llm-tester .
docker run -p 8000:8000 llm-tester
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 📞 技术支持

遇到问题？

1. 查看后端日志（终端输出）
2. 查看浏览器控制台（F12 开发者工具）
3. 检查 `config/models.yaml` 配置是否正确
4. 确认 API Key 和 Endpoint 有效

## 🎉 功能对比

| 功能 | Streamlit 版本 | FastAPI 版本 (方案 A) |
|------|---------------|----------------------|
| 局部更新 | ❌ 全页重渲染 | ✅ 真正的局部更新 |
| 流式性能 | ⚠️ 卡顿（5+ 模型） | ✅ 流畅（10+ 模型） |
| 固定 5 列 | ⚠️ 响应式变化 | ✅ 固定布局 |
| 自定义样式 | ⚠️ 受限 | ✅ 完全控制 |
| API 接口 | ❌ 无 | ✅ RESTful + SSE |
| 开发成本 | 低 | 中 |
| 部署复杂度 | 低 | 中 |

---

**版本：** 1.1.0 (方案 A)  
**更新日期：** 2026-01-16  
**最新更新：** 
- 前端参数配置化，所有可配置项已迁移到 `frontend/config.js`
- 添加流式首Token延迟统计指标
- 修复统计摘要显示bug，增强错误处理和日志
- CSV下载文件添加UTF-8 BOM，完美解决中文乱码问题
- 新增历史记录功能，自动保存测试结果并支持查看管理（本地JSON存储）
