# 贡献指南

感谢你有兴趣为 LLM Evaluation 做出贡献！本文档提供了贡献流程的指南。

## 📋 行为准则

本项目遵守贡献者盟约。通过参与本项目，您承诺遵守其条款。请阅读 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) 了解详情。

## 🚀 如何贡献

### 报告 Bug

发现 bug？请按以下步骤报告：

1. **检查现有 Issue**：确保 bug 尚未被报告
2. **提供详细信息**：
   - 清晰的标题和描述
   - Python 版本和操作系统
   - 复现步骤
   - 实际输出和期望输出
   - 错误日志和堆栈跟踪
3. **提交 Issue**：在 GitHub 上提交详细的 bug report

### 建议功能

有新功能想法？我们欢迎建议！

1. **检查现有 Issue**：确保功能尚未被建议
2. **详细描述**：
   - 功能的用途
   - 预期行为
   - 可能的实现方案
3. **提交讨论**：在 Discussions 中分享你的想法

### 提交 Pull Request

准备好贡献代码？请按以下步骤进行：

#### 1. Fork 和克隆

```bash
# Fork 本仓库
# Clone 你的 fork
git clone https://github.com/your-username/LLM-Evaluation.git
cd LLM-Evaluation
```

#### 2. 创建分支

```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 或创建修复分支
git checkout -b fix/issue-name
```

#### 3. 开发和测试

```bash
# 安装开发依赖
pip install -r requirements.txt

# 进行开发...

# 测试你的更改
python -m pytest tests/
```

#### 4. 遵循代码规范

- **Python 代码**：遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 风格指南
- **类型提示**：添加类型注解
- **文档字符串**：使用清晰的文档字符串
- **提交信息**：使用清晰、描述性的提交信息

**提交信息格式：**
```
<type>: <description>

<body>

<footer>
```

**类型包括：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更改
- `style`: 代码风格更改（格式、缺少分号等）
- `refactor`: 代码重构
- `perf`: 性能改进
- `test`: 添加或修改测试
- `chore`: 构建、依赖更新等

**示例：**
```
feat: add config management system

- Implement environment variable configuration
- Add settings.py for centralized config
- Support multi-environment deployment

Closes #123
```

#### 5. 提交 PR

```bash
# 推送到你的 fork
git push origin feature/your-feature-name

# 在 GitHub 上创建 Pull Request
# - 提供清晰的标题和描述
# - 链接相关的 Issue
# - 描述你的更改内容
```

#### 6. 代码审查

- 等待维护者审查
- 根据反馈进行修改
- 不要关闭 PR，让审查者批准

## 📚 开发指南

### 项目结构

```
LLM-Evaluation/
├── backend/          # FastAPI 后端
├── frontend/         # 前端代码
├── tester/          # 测试逻辑
├── config/          # 配置文件
├── scripts/         # 工具脚本
└── docs/            # 文档（如有）
```

### 设置开发环境

```bash
# 1. 克隆项目
git clone https://github.com/your-username/LLM-Evaluation.git
cd LLM-Evaluation

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 设置环境变量
cp .env.example .env

# 6. 运行开发服务器
python start_server.py
```

### 代码风格

我们使用以下工具检查代码质量：

```bash
# 使用 pylint
pylint backend/ tester/

# 使用 black 格式化代码
black backend/ tester/

# 使用 isort 整理导入
isort backend/ tester/
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api.py

# 生成覆盖率报告
pytest --cov=backend --cov=tester
```

## 📝 文档贡献

改进文档也很重要！

- 修复错误和拼写
- 改进清晰度和可读性
- 添加更多示例
- 翻译文档

## 🎓 学习资源

新手? 查看这些资源：

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Python 开发者指南](https://devguide.python.org/)
- [Git 学习资源](https://git-scm.com/book/zh/v2)

## ❓ 有问题？

- 查看现有的 [Issues](https://github.com/your-username/LLM-Evaluation/issues)
- 在 [Discussions](https://github.com/your-username/LLM-Evaluation/discussions) 提问
- 查看 [Wiki](https://github.com/your-username/LLM-Evaluation/wiki)

## ✅ PR 检查清单

在提交 PR 前，请检查：

- [ ] 我已经 fork 并创建了新分支
- [ ] 我的代码遵循项目的代码风格
- [ ] 我已经添加了必要的注释和文档
- [ ] 我的更改不会破坏现有的单元测试
- [ ] 我已经添加了新功能的测试
- [ ] 我的提交信息清晰明了
- [ ] 我已经更新了 README（如适用）

## 🎉 感谢

感谢你的贡献！每一个贡献都有助于使 LLM Evaluation 变得更好。

---

**需要帮助？** 在 Issues 中提问或查看 ARCHITECTURE_OPTIMIZATION.md 了解更多信息。
