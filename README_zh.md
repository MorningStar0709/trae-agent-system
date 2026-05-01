# Trae AI Agent Enhancements

[![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)](https://www.trae.ai/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![npm](https://img.shields.io/npm/v/trae-agent-enhancements?style=flat-square)](https://www.npmjs.com/package/trae-agent-enhancements)

[English](./README.md) | [中文](./README_zh.md)

---

## 关于本项目

**Trae AI Agent Enhancements** 是一套为 [Trae IDE](https://www.trae.ai/) 打造的 AI Agent 规则与技能集。通过规则路由、专业技能和持久记忆三大层，让 AI Agent 从"什么都能干但什么都不稳"变成"该快的快、该稳的稳、该学的学"。

## 架构概览

```
用户输入 → 规则层（路由与约束）→ 技能层（执行）→ 记忆层（学习）
```

| 层级 | 数量 | 职责 |
|:-----|:-----|:-----|
| **规则（Rules）** | 8 条 | 路由决策、行为约束、环境处理 |
| **技能（Skills）** | 33 个 | 专业工具箱，覆盖设计→编码→调试→提交→收尾 |
| **记忆（Memory）** | 核心记忆 | 跨会话知识积累 |

## 核心亮点

- **T-Shirt 分档**：任务自动分级（S/M/L）—— 小任务快，大任务严
- **闭环质量**：每个技能输出可验证证据 —— 不接受"应该没问题"
- **自我进化**：教训沉淀到核心记忆 —— 同一个坑不踩第二次
- **中文团队适配**：全中文触发短语、国内 Git 平台支持、中英双语技能
- **Windows 原生**：PowerShell 命令、端口冲突恢复、路径规范

## 快速开始

### 方式一：npm 安装（推荐）

在任何目录下运行即可（全局安装到用户主目录，所有项目可用）：

```
npx trae-agent-enhancements
```

根据提示选择你的 Trae 版本即可完成安装：

| 版本 | 安装位置 | 说明 |
|:-----|:---------|:-----|
| 国内版（trae.cn） | `~/.trae-cn/rules/` + `~/.trae-cn/skills/` | 全局生效，所有项目可用 |
| 国际版（trae.ai） | `~/.trae/rules/` + `~/.trae/skills/` | 全局生效，所有项目可用 |

你也可以通过 `--edition` 参数直接指定版本：

```
npx trae-agent-enhancements --edition cn       # 国内版
npx trae-agent-enhancements --edition intl     # 国际版
npx trae-agent-enhancements --help             # 查看帮助
```

### 前置依赖（MCP）

部分技能需要以下 MCP Server 才能完整体验：

| MCP Server | 用途 | 安装方式 |
|:-----------|:-----|:---------|
| **Everything Search** | Windows 本地文件快速搜索 | 在 Trae 设置 → MCP 中添加，配置参考 everything-search skill |
| **Chrome DevTools MCP** | 浏览器自动化、Console/Network/DOM 调试、性能分析 | 在 Trae 设置 → MCP 中添加 `npx chrome-devtools-mcp` |

> 这两个 MCP 使能 `everything-search` 和 `chrome-devtools` 等技能的核心功能。如不安装，相关技能将无法使用。

### 方式二：手动安装

```
# 克隆仓库
git clone https://github.com/MorningStar0709/trae-agent-enhancements.git

# 选择你的版本，复制到对应目录

# 国内版（trae.cn）
cp -r trae-agent-enhancements/rules  ~/.trae-cn/rules
cp -r trae-agent-enhancements/skills ~/.trae-cn/skills

# 国际版（trae.ai）
cp -r trae-agent-enhancements/rules  ~/.trae/rules
cp -r trae-agent-enhancements/skills ~/.trae/skills
```

### 试试这些指令

> "帮我排查这个报错"
> "先写计划再实现"
> "改好了没？验证一下"
> "帮我提交"
> "记住这个处理方式"

## 文档导航

| 文档 | 说明 | 也可在博客阅读 |
|:-----|:-----|:--------------|
| [docs/01-intro_zh.md](docs/01-intro_zh.md) | 15 秒极简介绍 | [博客](https://www.iiisle.com/archives/889anRKF)（支持评论互动）|
| [docs/02-overview_zh.md](docs/02-overview_zh.md) | 功能亮点介绍（3 分钟）| [博客](https://www.iiisle.com/archives/Gzp3OH5P)（支持评论互动）|
| [docs/03-components_zh.md](docs/03-components_zh.md) | 组件速查手册（5 分钟）| [博客](https://www.iiisle.com/archives/Mx3JgdpO)（支持评论互动）|
| [docs/04-design_zh.md](docs/04-design_zh.md) | 设计思路与巧思（5 分钟）| [博客](https://www.iiisle.com/archives/D43Cn9z2)（支持评论互动）|
| [docs/05-architecture_zh.md](docs/05-architecture_zh.md) | 完整架构与工作流（15 分钟）| [博客](https://www.iiisle.com/archives/ESHdkuJL)（支持评论互动）|

### 开发者参考

| 文章 | 链接 |
|:-----|:-----|
| LLM 中文使用者在 Skill / Rule / Agent 脚本中的语言权衡 | [博客](https://www.iiisle.com/archives/pugANGT1) |
| Trae 原生记忆系统：Skill 使用现状与局限性 | [博客](https://www.iiisle.com/archives/itAAwZ0I) |

## 技能路径

| 路径 | 包含的技能 |
|:-----|:-----------|
| **设计/规划** | brainstorming → writing-plans → executing-plans / subagent-driven-development |
| **调试/质量** | systematic-debugging → test-driven-development → verification-before-completion |
| **收尾/进化** | git-commit → finishing-a-development-branch → self-improvement |
| **编排/工具** | dispatching-parallel-agents, workflow-runner, find-docs |
| **浏览器/前端** | chrome-devtools, frontend-design, chart-visualization, a11y-debugging |
| **元技能** | skill-creator, skill-stability-review, skill-language-policy, creating-trae-rules |

## Windows/Trae 适配

- **PowerShell 命令**：Windows 环境优先语法
- **端口恢复**：netstat → taskkill → 确认 → 重试
- **路径规范**：globs 使用正斜杠，绝对路径用反斜杠
- **核心记忆**：每范围 20 条上限，自动淘汰旧条目

## 致谢

本项目参考自 [superpowers-zh](https://github.com/jnMetaCode/superpowers-zh)（AI 编程超能力 · 中文增强版）的 npx 安装模式与项目结构设计思路。感谢 [@jnMetaCode](https://github.com/jnMetaCode) 的杰出工作。

## 贡献指南

欢迎贡献代码！请阅读 [CONTRIBUTING_zh.md](CONTRIBUTING_zh.md) 了解贡献指南。

英文版本请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。
