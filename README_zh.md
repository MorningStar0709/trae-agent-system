# Trae Skills 工具集

[![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)](https://www.trae.ai/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

## 关于本项目

**Trae Skills** 是一套专为 Windows 平台 [Trae IDE](https://www.trae.ai/) 设计的 Skills 工具集，帮助开发者自动化重复性任务、规范开发流程，并确保在 Windows 环境下的稳定运行。

## 核心特性

- **Windows 优先设计**：所有 Skills 均经过严格的 Windows 环境测试和优化
- **中文用户适配**：原生支持简体中文，平衡英文技术锚点
- **稳定执行保障**：完整的验证脚本确保智能体行为可靠
- **生产级质量**：内置稳定性审查工具和验证工作流

## 包含的技能

| 技能 | 说明 |
|---|---|
| **agent-blueprint-architect** | 创建和优化 Trae Agent 配置，包含清晰的边界和触发条件 |
| **creating-trae-rules** | 定义和组织 Trae 项目规则，支持多种激活模式 |
| **skill-creator** | 脚手架搭建、审查和迭代新的 Trae 技能 |
| **skill-stability-review** | 审计 Skills 的 Windows/Trae 兼容性和执行稳定性 |

## 快速开始

### 安装

```powershell
# 克隆仓库
git clone https://github.com/MorningStar0709/trae-skills.git
cd trae-skills

# 导入到 Trae
# 打开 Trae IDE → 设置 → Skills 管理 → 从 skills/ 目录导入
```

### 验证

```powershell
# 验证单个 Skill
python skills/skill-creator/scripts/quick_validate.py skills/<skill-name>

# 扫描 Windows 兼容性
python skills/skill-stability-review/scripts/review_skills.py --skill skills/<skill-name> --markdown
```

## 详细文档

详细的使用说明和技术文档请参阅 [docs/SKILLS_INTRO_zh.md](docs/SKILLS_INTRO_zh.md)。

如需英文文档，请参阅 [docs/SKILLS_INTRO.md](docs/SKILLS_INTRO.md)。

## Windows/Trae 适配原则

所有 Skills 均遵循以下原则：

- **PowerShell 命令**：主要命令语法适配 Windows 环境
- **Windows 路径**：使用 `%userprofile%` 和绝对路径
- **风险检测**：自动检测 Unix 特定模式
- **路径转换**：清晰的主机/容器/URL 路径转换规则

## 贡献指南

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南。

## 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。
