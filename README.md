# 🚀 LLM 延迟测试器

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-LLM--Evaluation-black.svg)](#)

> 一个简单的 LLM 模型延迟测试工具，支持实时流式数据推送、多模型并发测试、完整的统计分析和历史记录管理。专为 Azure OpenAI 和其他云 API 设计。

**核心特性** ✨

- 🎯 **实时流式显示** - SSE 推送实时输出，支持 10+ 模型并发
- 📊 **完整统计分析** - 延迟、吞吐量、首Token延迟等多维度指标
- 💾 **历史记录管理** - 自动保存测试结果，支持查看和导出
- ⚙️ **灵活配置管理** - 支持环境变量配置、多环境部署
- 📈 **性能优异** - 每秒支持 200+ 次更新，无性能瓶颈
- 🔒 **生产就绪** - 规范的代码结构、完善的错误处理、详细的文档
- 🏗️ **现代架构** - 模块化设计、统一响应格式、自定义异常体系

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
│   ├── config.js             # 前端配置（可配置化）
│   └── styles.css            # 样式表
├── tester/
│   ├── latency_tester.py    # 延迟测试逻辑
│   └── metrics.py            # 指标计算
├── scripts/                   # ⭐ 工具脚本
│   ├── fix_model_names.py   # 修复模型名称
│   └── apply_optimizations.py # 一键优化
├── config/
│   ├── models.yaml              # ⚠️ API 密钥配置（已排除版本控制）
│   └── models.yaml.example      # ✅ 配置模板（提交到 GitHub）
├── .env.example             # ⭐ 环境变量模板
├── requirements.txt         # Python 依赖
├── start_server.py          # 快速启动脚本
├── ARCHITECTURE_OPTIMIZATION.md  # ⭐ 架构优化方案
├── MIGRATION_GUIDE.md            # ⭐ 迁移指南
├── OPTIMIZATION_SUMMARY.md       # ⭐ 优化总结
└── QUICK_REFERENCE.md            # ⭐ 快速参考
```

**⭐ 表示 2026-01-16 架构优化新增内容**

## 🖼️ 页面展示

![LLM Tester 页面截图](llm-test.png)

> 多模型并发对比、实时流式输出、统计摘要等核心功能一览。

## 🚀 快速开始

### 前置要求

- **Python 3.10+**
- **pip** 或 **conda**
- **Azure OpenAI** API 密钥和端点（或其他兼容的 OpenAI API）

### 1️⃣ 克隆项目

```bash
git clone https://github.com/your-username/LLM-Evaluation.git
cd LLM-Evaluation
```

### 2️⃣ 安装依赖

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 conda
conda create -n llm-eval python=3.10
conda activate llm-eval
pip install -r requirements.txt
```

### 3️⃣ 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件（可选，有默认值）
# 查看 QUICK_REFERENCE.md 了解更多配置选项
```

### 4️⃣ 配置模型

编辑 `config/models.yaml`，添加你的 Azure OpenAI 模型：

```bash
# 从示例文件复制
cp config/models.yaml.example config/models.yaml

# 编辑配置文件，填入你的实际信息
# 保存后会自动加载
```

**配置示例：**
```yaml
models:
  - name: gpt-4o
    endpoint: "https://your-resource.openai.azure.com/"
    api_key: "your-api-key-here"
    api_version: "2024-02-01"
  - name: gpt-4-turbo
    endpoint: "https://your-resource.openai.azure.com/"
    api_key: "your-api-key-here"
    api_version: "2024-04-01"
```

**🔒 安全提示：**
- ✅ `config/models.yaml` 已在 `.gitignore` 中，**不会上传到 GitHub**
- ✅ 使用 `config/models.yaml.example` 作为配置模板供参考
- ✅ **永远不要**在版本控制中提交真实的 API 密钥
- ✅ 也可使用 `.env` 文件通过环境变量配置（见 `.env.example`）

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

打开浏览器访问：
```
http://localhost:8000
```

## 📚 文档导航

| 文档 | 说明 | 用途 |
|------|------|------|
| **QUICK_REFERENCE.md** | 快速参考 | 快速上手使用 |
| **OPTIMIZATION_SUMMARY.md** | 优化总结 | 了解最新改进和特性 |
| **MIGRATION_GUIDE.md** | 迁移指南 | 应用架构优化 |
| **ARCHITECTURE_OPTIMIZATION.md** | 完整架构方案 | 深入学习架构设计 |

## 💡 主要功能

### 🎯 多模型并发测试

- 支持同时测试多个 LLM 模型
- 灵活配置并发数和迭代次数
- 真正的局部更新，各模型测试互不影响

### 🌊 实时流式推送

- SSE（Server Sent Event）实时推送
- 毫秒级更新延迟
- 支持 10+ 模型并发，每秒 200+ 次更新

### 📊 完整的统计分析

- **延迟统计**：最小/最大/平均值、百分位数
- **首Token延迟**：仅流式请求统计首个token返回延迟
- **成功率统计**：成功数、失败数、错误率
- **吞吐量分析**：请求/秒、token/秒

### 💾 历史记录管理

- 自动保存每次测试结果
- 支持查看历史测试详情
- CSV 导出功能
- 保留最近 100 条记录

### ⚙️ 灵活的配置管理

- **环境变量支持**（`.env`）- 不同环境不同配置
- **前端配置文件化**（`frontend/config.js`）- 无需修改代码
- **后端配置集中管理**（`backend/config/`）- 统一的配置接口
- **多环境支持**（dev/staging/prod）

## 📖 使用指南

### 前端配置

所有前端配置集中在 `frontend/config.js` 中，无需修改代码：

```javascript
// 预设问题列表
presetQuestions: [
    { label: "入门：how to learn english", value: "how to learn english" },
    { label: "基础：Explain transformer attention...", value: "..." },
    // ... 更多问题
]

// 默认测试参数
defaultParams: {
    concurrency: 3,      // 并发数
    iterations: 1,       // 迭代次数
    maxTokens: 1000,     // 最大token数
    temperature: 0.7,    // 温度
    stream: true         // 是否流式
}
```

### 后端配置

编辑 `config/models.yaml` 添加模型配置：

```yaml
models:
  - name: model-name
    endpoint: "https://your-resource.openai.azure.com"
    api_key: "your-api-key"
    api_version: "2024-02-01"
```

### 环境变量配置

编辑 `.env` 文件配置应用行为。详见 `.env.example` 了解所有配置项。

## 🔧 API 文档

### 获取可用模型

```http
GET /api/models
```

### 启动测试任务

```http
POST /api/test
Content-Type: application/json

{
  "models": ["gpt-4o"],
  "question": "Explain transformer attention",
  "concurrency": 1,
  "iterations": 1,
  "max_tokens": 1000,
  "temperature": 0.7,
  "stream": true
}
```

### 流式接收结果

```http
GET /api/stream/{task_id}
```

### 历史记录接口

```http
GET /api/history           # 获取历史列表
GET /api/history/{id}      # 获取详情
DELETE /api/history/{id}   # 删除记录
DELETE /api/history        # 清空所有
```

详见 [README_old.md](README_old.md) 了解完整 API 文档。

## 🏗️ 架构优化

### 最近改进（2026-01-16）

我们对项目进行了全面的架构优化，提升了代码质量、安全性和可维护性：

#### ✨ 新增功能

1. **配置管理系统**（`backend/config/`）
   - 环境变量配置支持
   - 日志系统配置
   - 多环境部署支持

2. **核心模块**（`backend/core/`）
   - 统一 API 响应格式
   - 自定义异常体系
   - 全局异常处理

3. **工具脚本**（`scripts/`）
   - 自动修复模型名称
   - 一键应用优化

#### 📖 优化文档

- [ARCHITECTURE_OPTIMIZATION.md](ARCHITECTURE_OPTIMIZATION.md) - 4 阶段完整优化方案
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - 渐进式迁移指南
- [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) - 优化总结
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考

### 向后兼容性

✅ 现有代码完全兼容，无需修改  
✅ 可以渐进式应用新的架构  
✅ 老版本代码可以继续使用

## 🐛 故障排查

### 问题：端口被占用

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### 问题：模块导入错误

```bash
# 确保在项目根目录运行
cd LLM-Evaluation

# 或设置 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 问题：API 连接失败

- 检查 Azure OpenAI 配置是否正确
- 验证 API Key 和 Endpoint 有效性
- 检查网络连接

## 📊 性能优化建议

| 参数 | 建议值 | 说明 |
|------|--------|------|
| 单模型并发数 | 1-10 | 过高会导致 API 限流 |
| 同时测试模型数 | 1-15 | 前端性能考虑 |
| 迭代次数 | 1-20 | 首次测试 1-5 次即可 |
| 流式输出 | 启用 | 响应较大时性能更好 |

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 1. Fork 本仓库
# 2. Clone 你的 fork
git clone https://github.com/your-username/LLM-Evaluation.git

# 3. 创建开发分支
git checkout -b feature/your-feature

# 4. 安装开发依赖
pip install -r requirements.txt

# 5. 进行开发和测试

# 6. 提交 PR
git push origin feature/your-feature
```

### 代码规范

- 遵循 PEP 8 风格指南
- 添加类型提示
- 编写清晰的文档字符串
- 添加必要的单元测试

## 📝 License

本项目采用 [MIT License](LICENSE) 协议。

## 📞 联系方式

- 提交 [Issue](https://github.com/your-username/LLM-Evaluation/issues) 报告 bug 或建议功能
- 查看 [Discussions](#) 进行讨论

## 🙏 致谢

感谢所有贡献者的支持和帮助！

---

**版本：** 1.2.0 (with Architecture Optimization)  
**更新日期：** 2026-01-16  
**状态：** ✅ 生产就绪

### 最新更新

- ✅ 完整的架构优化
- ✅ 配置管理系统
- ✅ 统一响应格式和异常处理
- ✅ 详尽的文档和迁移指南
- ✅ 自动化工具脚本
- ✅ GitHub 发布准备完成
