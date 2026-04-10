# 贡献指南

感谢你考虑为 Nuonuo Pet 做出贡献！

## 如何贡献

### 报告 Bug

如果你发现了 bug，请创建一个 Issue，包含：
- 清晰的标题和描述
- 复现步骤
- 期望行为和实际行为
- 截图（如果适用）
- 环境信息

### 提出新功能

如果你有新功能的想法，请创建一个 Issue，包含：
- 功能描述
- 使用场景
- 可能的实现方式

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/your-username/nuonuo-pet.git
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **进行更改**
   - 遵循代码规范
   - 添加必要的测试
   - 更新相关文档

4. **提交更改**
   ```bash
   git commit -m "feat: add your feature"
   ```

5. **推送到分支**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 填写 PR 模板
   - 关联相关 Issue
   - 等待代码审查

## 代码规范

### Python
- 遵循 PEP 8
- 使用 Black 格式化
- 添加类型注解
- 编写文档字符串

### TypeScript
- 使用 ESLint 和 Prettier
- 添加类型定义
- 编写注释

### C
- 遵循 ESP-IDF 风格
- 添加注释
- 处理错误返回值

## 测试要求

- 新功能必须添加测试
- 所有测试必须通过
- 代码覆盖率不能降低

## 文档要求

- 更新相关文档
- API 更改需要更新 API 文档
- 新功能需要更新 CHANGELOG

## 行为准则

- 尊重所有贡献者
- 接受建设性批评
- 关注对项目最有利的事情
- 对社区保持友好和包容

## 许可证

通过贡献代码，你同意你的代码将以 MIT 许可证授权。
