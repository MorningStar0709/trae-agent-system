# 贡献指南

感谢你关注 Trae Skills 项目！我们欢迎各种形式的贡献，包括但不限于报告问题、提交修复、改进文档或创建新的 Skills。

## 贡献方式

### 报告问题

如果你发现 bug 或有功能建议，请通过 GitHub Issues 报告。请包含以下信息：

- **问题描述**：清晰描述遇到的问题或建议的功能
- **复现步骤**：如果是 bug，提供详细的复现步骤
- **环境信息**：Windows 版本、Trae 版本等
- **期望 vs 实际**：描述期望的行为和实际的行为

### 提交代码

#### Fork & Clone

1. Fork 本仓库
2. 克隆你的 Fork 到本地
   ```powershell
   git clone https://github.com/MorningStar0709/trae-skills.git
   cd trae-skills
   ```

3. 创建特性分支
   ```powershell
   git checkout -b feature/your-feature-name
   ```

#### 开发规范

##### Skill 结构规范

所有 Skill 必须包含：

```
skill-name/
├── SKILL.md                    # 必需：技能主文件
├── examples/                  # 可选：输入输出示例
├── templates/                  # 可选：模板文件
├── resources/                  # 可选：资源文件
└── scripts/                    # 可选：辅助脚本
```

##### 命名规范

- **Skill 目录名**：kebab-case（如 `skill-name`）
- **Skill 名称**：小写字母、数字和连字符
- **描述长度**：不超过 1024 字符
- **中文优先**：触发描述使用简体中文

##### 代码规范

- **Python 脚本**：
  - 使用 Python 3 标准库，避免外部依赖
  - 包含失败路径和非零退出码
  - 输出机器可读的格式（推荐 JSON）
  
- **PowerShell 示例**：
  - 优先使用跨平台兼容的命令
  - 避免 bash 特定语法
  - 路径使用正斜杠或正确的 Windows 格式

##### Windows/Trae 适配要求

- 避免硬编码 Unix 路径（`/tmp/`、`~/`）
- 避免 Unix 特定命令（`sudo`、`chmod`、`rm -rf`）
- 避免 `bash` 代码块用于主机端指导
- 使用 PowerShell 兼容的命令示例
- 路径示例使用 `%userprofile%` 或绝对路径

#### 验证清单

提交前请运行以下验证：

```powershell
# 1. 验证 Skill 格式
python skills/skill-creator/scripts/quick_validate.py skills/<skill-name>

# 2. 运行稳定性扫描
python skills/skill-stability-review/scripts/review_skills.py --skill skills/<skill-name> --json

# 3. 检查 Windows 兼容性
python skills/skill-stability-review/scripts/review_skills.py --root . --markdown
```

#### 提交 Pull Request

1. 确保所有验证通过
2. 填写清晰的 PR 描述：
   - 解决的问题或新增的功能
   - 测试验证结果
   - 截图或演示（如适用）
3. 关联相关 Issues（使用 `Fixes #issue-number`）

### 改进文档

- 使用简体中文，保持术语一致
- 代码示例需验证可执行性
- 更新相关文件的交叉引用
- 检查文档的 Windows 环境适配性

## 开发工作流

### 本地测试

1. **创建测试 Skill**
   ```powershell
   mkdir skills/test-skill
   # 创建基本的 SKILL.md
   ```

2. **运行验证**
   ```powershell
   python skills/skill-creator/scripts/quick_validate.py skills/test-skill
   ```

3. **测试扫描**
   ```powershell
   python skills/skill-stability-review/scripts/review_skills.py --skill skills/test-skill --markdown
   ```

### 代码审查

所有提交都需要经过代码审查，重点关注：

- **功能正确性**：Skill 是否按预期工作
- **Windows 兼容性**：是否适配 Windows 环境
- **触发边界**：是否避免误触发
- **失败处理**：是否有清晰的错误处理
- **文档完整性**：是否包含必要的说明

## 问题解答

**Q: 如何确定我的 Skill 是否需要创建？**

A: 如果你发现以下情况，可以考虑创建 Skill：
- 相同的任务重复出现多次
- 需要特定的触发条件和边界
- 需要明确的执行流程和失败处理

**Q: Skill 和 Rule 的区别是什么？**

A: 
- **Skill**：可复用的能力模块，包含完整的工作流程和执行逻辑
- **Rule**：轻量级的指令文件，控制 Trae 在特定场景下的行为

**Q: 如何测试 Skill 在真实场景下的表现？**

A:
1. 在 Trae IDE 中导入 Skill
2. 使用常见的触发短语进行测试
3. 验证边界情况（应触发和不应触发的场景）
4. 检查输出格式是否符合预期

## 联系方式

- **GitHub Issues**: [提交问题](https://github.com/MorningStar0709/trae-skills/issues)
- **Email**: （可选）

## 行为准则

请保持友善和专业的交流态度，尊重他人的观点和建议。我们欢迎多元化的贡献，但所有贡献者都应遵守基本的社区行为准则。

---

再次感谢你的贡献！每一个贡献都对项目的发展至关重要。
