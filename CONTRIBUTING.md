# 贡献指南

感谢您对 nuonuo-pet 项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请：

1. 检查 [Issues](https://github.com/yourusername/nuonuo-pet/issues) 确认问题尚未被报告
2. 创建新的 Issue，详细描述问题或建议
3. 提供复现步骤、预期行为和实际行为

### 提交代码

1. **Fork 项目**
   ```bash
   # 在 GitHub 上点击 Fork 按钮
   git clone https://github.com/yourusername/nuonuo-pet.git
   cd nuonuo-pet
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **进行更改**
   - 遵循现有代码风格
   - 添加必要的测试
   - 更新相关文档

4. **提交更改**
   ```bash
   git add .
   git commit -m "描述您的更改"
   ```

5. **推送到您的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 访问原项目的 GitHub 页面
   - 点击 "New Pull Request"
   - 描述您的更改

### 代码规范

- 遵循 PEP 8 代码风格
- 使用有意义的变量和函数名
- 添加必要的注释和文档字符串
- 确保代码通过现有测试

### 测试

在提交代码前，请确保：

```bash
# 运行基础测试
cd backend
python tests/test_llm_basic.py

# 运行项目检查
python scripts/check_project.py
```

### 文档

如果您的更改影响了用户功能，请更新相关文档：
- README.md
- API 文档
- 使用说明

## 开发环境设置

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/nuonuo-pet.git
   cd nuonuo-pet
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv-backend
   # Windows
   .venv-backend\Scripts\activate
   # Linux/Mac
   source .venv-backend/bin/activate
   ```

3. **安装开发依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install pytest pytest-asyncio black flake8
   ```

4. **运行开发服务器**
   ```bash
   uvicorn app.main:app --reload
   ```

## 项目结构

了解项目结构有助于您更好地贡献：

```
nuonuo-pet/
├── backend/                 # 后端代码
│   ├── app/                # 应用核心
│   ├── tests/              # 测试文件
│   └── requirements.txt    # 依赖
├── docs/                   # 文档
├── scripts/                # 工具脚本
└── README.md              # 项目说明
```

## 行为准则

- 尊重所有贡献者
- 接受建设性批评
- 专注于对项目最有利的事情
- 对社区保持同理心

## 获取帮助

如果您需要帮助：

- 查看 [文档](docs/)
- 搜索 [Issues](https://github.com/yourusername/nuonuo-pet/issues)
- 创建新的 Issue 寻求帮助

## 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。

---

再次感谢您的贡献！🎉
