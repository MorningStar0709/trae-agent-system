# Trae Skills 项目介绍

## 项目概述

本项目是一套专为 **Windows 平台 Trae IDE** 设计的 Skills 工具集，专注于帮助中文用户高效创建、管理和优化 Trae 的智能体（Agent）与规则（Rules）。所有 Skills 均经过严格的 Windows/Trae 适配验证，确保在 Windows 环境下稳定运行。

## 目录结构

```
Trae-skills/
├── docs/                              # 项目文档
│   ├── SKILLS_INTRO.md              # 英文版技术文档
│   └── SKILLS_INTRO_zh.md          # 中文版详细技术文档
├── skills/                            # Skills 核心目录
│   ├── agent-blueprint-architect/    # Agent 蓝图设计工具
│   │   └── SKILL.md
│   ├── creating-trae-rules/          # Trae 规则创建工具
│   │   ├── resources/
│   │   │   └── trae-rules-reference.md  # 官方规则文档参考
│   │   ├── templates/
│   │   │   ├── always-apply.md      # 全局规则模板
│   │   │   ├── git-message.md       # Git 提交规则模板
│   │   │   ├── intelligent-apply.md # 智能触发规则模板
│   │   │   ├── manual-only.md       # 手动触发规则模板
│   │   │   └── specific-files.md    # 文件匹配规则模板
│   │   └── SKILL.md
│   ├── skill-creator/                # Skill 创建工具
│   │   ├── scripts/
│   │   │   └── quick_validate.py    # 快速验证脚本
│   │   └── SKILL.md
│   └── skill-stability-review/       # Skill 稳定性审查工具
│       ├── scripts/
│       │   └── review_skills.py     # 批量扫描脚本
│       └── SKILL.md
├── .github/                           # GitHub 配置
│   ├── ISSUE_TEMPLATE/              # Issue 模板
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── question.md
│   └── PULL_REQUEST_TEMPLATE.md     # PR 模板
├── .gitignore                        # Git 忽略规则
├── CONTRIBUTING.md                  # 贡献指南
├── LICENSE                          # MIT 许可证
├── README.md                        # 英文入口文档
└── README_zh.md                     # 中文入口文档
```

## Skill 详细介绍

### Agent Blueprint Architect

**功能定位**：专为创建和优化 Trae Agent 配置的专用工具。

**核心能力**：
- 为新建 Agent 生成可直接使用的完整配置
- 定义清晰的英文标识名（kebab-case 格式）
- 编写精炼的中文系统提示词
- 设计准确的触发条件和边界
- 配置合理的能力开关（最小必要原则）

**Windows/Trae 适配要点**：
- 默认面向 Windows 版 Trae 使用者设计
- 命令示例优先使用 PowerShell
- 路径示例优先使用 Windows 路径或 `%userprofile%`
- 避免硬编码 Unix shell、macOS 路径或 Linux-only 路径
- 确保本地文件路径、命令执行与 Windows 环境兼容

**使用场景**：
- 创建新的 Trae Agent
- 优化现有 Agent 配置
- 拆分宽泛 Agent 为职责明确的新 Agent
- 设计 Agent 能力开关配置

### Creating Trae Rules

**功能定位**：用于创建、修改和组织 Trae IDE 规则文件的工具。

**核心能力**：
- 在 `.trae/rules/` 目录下创建项目规则
- 支持模块级别的规则配置
- 提供多种激活模式（全局、文件匹配、智能触发、手动）
- 生成符合 Trae 规范的 Git 提交消息规则
- 与 AGENTS.md、CLAUDE.md 协同工作

**Windows/Trae 适配要点**：
- 使用正斜杠作为路径分隔符示例
- 提供 Windows 可访问的路径示例
- 确保 frontmatter 格式符合 Trae 规范
- 验证规则文件嵌套层级（不超过 3 层）
- 支持 `scene: git_message` 的 Git 提交场景

**模板系统**：
| 模板文件 | 用途 | 激活模式 |
|---|---|---|
| always-apply.md | 全局项目约束 | alwaysApply: true |
| specific-files.md | 文件模式匹配 | globs 模式 |
| intelligent-apply.md | 语义触发场景 | description 模式 |
| manual-only.md | 手动引用规则 | #Rule 引用 |
| git-message.md | 提交消息格式 | scene: git_message |

**资源文件**：
- `trae-rules-reference.md`：官方规则文档的本地参考，包含完整的激活模式、路径规范和最佳实践

### Skill Creator

**功能定位**：用于创建、修改和重构 Trae Skills 的完整工作流工具。

**核心能力**：
- 设计 Skill 的触发条件和使用边界
- 定义清晰的输入输出契约
- 编写可执行的工作流程
- 创建辅助资源（examples、templates、resources）
- 验证 Skill 的 frontmatter 格式

**Windows/Trae 适配要点**：
- 明确区分项目级 Skill 和全局 Skill
- 全局 Skill 路径：`%userprofile%\.trae\skills\`（Windows）
- 项目 Skill 路径：`<project>\.trae\skills\`
- Skill 内示例使用正斜杠路径，避免 Windows 硬编码
- 依赖声明需验证 Trae IDE/Trae CLI/MCP 可用性

**辅助脚本**：
- `quick_validate.py`：轻量级 Skill 验证脚本
  - 验证 frontmatter 格式
  - 检查必需字段（name、description）
  - 验证命名规范（kebab-case）
  - 检查描述长度限制（≤1024 字符）
  - 纯 Python 标准库实现，无外部依赖

**创建流程**：
1. 捕获意图：识别重复任务和触发场景
2. 建立基准：理解无 Skill 时 Trae 的默认行为
3. 定义评测用例：覆盖正常路径、边界路径和负向路径
4. 编写最小 Skill：仅包含必要内容
5. 添加资源：仅在直接减少歧义时创建
6. 验证迭代：运行验证脚本并测试

### Skill Stability Review

**功能定位**：用于审查和优化 Trae Skill 稳定性的完整工具，重点保障 Windows/Trae 兼容性。

**核心能力**：
- 扫描 Skill 包的完整内容（SKILL.md + scripts + resources + templates）
- 检测 Windows/Trae 风险模式
- 评估中文用户适配质量
- 验证脚本同步和执行稳定性
- 生成可量化的评分报告

**Windows/Trae 适配要点**：
- 检测 PowerShell 不兼容的命令（bash、export、sudo、chmod）
- 检测 Unix 路径模式（~/、/tmp/）
- 检测 Windows 环境下可能失败的容器命令
- 路径转换规则：
  - Windows 主机示例使用 Windows 路径
  - 容器/远程/URL 路径保持原生形式
  - JSON/config 中的路径正确转义
- 验证脚本退出码行为（非零表示失败）
- 确保 stdout/stderr 输出可机器读取

**辅助脚本**：
- `review_skills.py`：轻量级批量扫描脚本
  - 发现 Skill 文件夹和 SKILL.md
  - 运行 quick_validate.py 进行基础验证
  - 扫描 Windows/Trae 风险模式
  - 生成初步评分和审查线索
  - 支持 JSON 和 Markdown 格式输出
  - 支持单个 Skill 或批量扫描

**评分维度**：
| 维度 | 权重 | 评估内容 |
|---|---|---|
| Agent 执行性 | 25% | 步骤、输入、输出、失败处理清晰度 |
| Windows/Trae 适配 | 20% | 命令、路径、shell 假设兼容性 |
| 脚本同步 | 20% | 脚本与 SKILL.md 一致性 |
| 触发与边界 | 15% | 正确触发、避免重叠、中英文锚点 |
| 中文用户适配 | 10% | 简体中文沟通自然度 |
| 可维护性 | 10% | 简洁性、作用域、更新难度 |

**严重性等级**：
- **Blocking**：破坏执行、风险破坏性行为、损坏输出
- **High**：可能导致错误 shell、错误路径、虚假成功
- **Medium**：导致可避免的歧义、手动摩擦、偶尔误触发
- **Low**：文案、可维护性、包装噪音

**推荐扫描命令**：
```powershell
# 完整目录扫描
python .\skill-stability-review\scripts\review_skills.py --root "C:\Users\skyler\.trae\skills" --markdown --include-generated

# 单个 Skill JSON 扫描
python .\skill-stability-review\scripts\review_skills.py --skill "C:\Users\skyler\.trae\skills\everything-search" --json
```

## Windows/Trae 适配亮点

### 统一的平台策略

| 特性 | Windows 适配实现 |
|---|---|
| 路径规范 | 优先使用 `%userprofile%`、绝对路径，避免 Unix 风格 `~/` 和 `/tmp/` |
| 命令语法 | PowerShell 原生命令，避免 bash 特定语法 |
| 路径分隔符 | 内部使用正斜杠（`/`），输出时适配 Windows |
| 文件操作 | 避免 `rm -rf`，使用安全的文件操作 |
| 环境变量 | 使用 `%VAR%` 格式而非 `$VAR` |
| Shell 类型 | 明确区分主机 shell 和容器 shell |

### 路径转换规则

```
主机端命令、输入路径、输出路径 → Windows 可访问路径
容器内路径、URL、API 路径 → 保持原生形式
JSON/config 中的路径 → 正确转义（如 `D:\\APP\\Tools\\...`）
```

### 风险模式检测

自动检测以下 Windows/Trae 不友好模式：
- ````bash``` 代码块（主机端指导）
- `export KEY=value`（Unix 特定）
- `cat <<'EOF'`（Heredoc）
- `sudo`、`chmod`（Unix 管理员命令）
- `rm -rf`（主机端风险操作）
- `/tmp/`、`~/`（Unix 路径）
- 未转义的 Windows 路径

## 文件清单

| 文件路径 | 类型 | 说明 |
|---|---|---|
| agent-blueprint-architect/SKILL.md | 必需 | Agent 蓝图设计完整规范 |
| creating-trae-rules/SKILL.md | 必需 | Trae 规则创建工作流 |
| creating-trae-rules/resources/trae-rules-reference.md | 参考 | 官方规则文档本地参考 |
| creating-trae-rules/templates/always-apply.md | 模板 | 全局规则模板 |
| creating-trae-rules/templates/git-message.md | 模板 | Git 提交规则模板 |
| creating-trae-rules/templates/intelligent-apply.md | 模板 | 智能触发规则模板 |
| creating-trae-rules/templates/manual-only.md | 模板 | 手动触发规则模板 |
| creating-trae-rules/templates/specific-files.md | 模板 | 文件匹配规则模板 |
| skill-creator/SKILL.md | 必需 | Skill 创建完整指南 |
| skill-creator/scripts/quick_validate.py | 脚本 | Skill 快速验证工具 |
| skill-stability-review/SKILL.md | 必需 | Skill 稳定性审查规范 |
| skill-stability-review/scripts/review_skills.py | 脚本 | 批量扫描和评分工具 |

## 使用建议

### 新用户入门路径

1. 从 **skill-creator** 开始，了解 Skill 的基本结构
2. 使用 **creating-trae-rules** 创建项目规则
3. 参考 **agent-blueprint-architect** 设计自定义 Agent
4. 用 **skill-stability-review** 验证和优化

### 进阶用户优化路径

1. 运行 `review_skills.py` 扫描现有 Skills
2. 根据评分报告修复 High/Blocking 问题
3. 验证脚本在 Windows 环境实际可执行
4. 更新触发条件提升自然语言匹配度

### 最佳实践

- 创建新 Skill 前先运行 quick_validate.py
- 批量部署前用 review_skills.py 扫描
- 保持触发描述的中英文平衡
- 优先使用 PowerShell 命令示例
- 避免在 Skill 中硬编码平台假设
