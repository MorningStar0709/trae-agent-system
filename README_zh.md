# Trae AI Agent System

[![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)](https://www.trae.ai/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

[English](./README.md) | [中文](./README_zh.md)

---

## 关于本项目

**Trae AI Agent System** 是一套为 [Trae IDE](https://www.trae.ai/) 打造的 AI Agent 增强系统。通过规则路由、专业技能和持久记忆三大层，让 AI Agent 从"什么都能干但什么都不稳"变成"该快的快、该稳的稳、该学的学"。

## 架构概览

```
用户输入 → 规则层（路由与约束）→ 技能层（执行）→ 记忆层（学习）
```

| 层级 | 数量 | 职责 |
|:-----|:-----|:-----|
| **规则（Rules）** | 8 条 | 路由决策、行为约束、环境处理 |
| **技能（Skills）** | 35 个 | 专业工具箱，覆盖设计→编码→调试→提交→收尾 |
| **记忆（Memory）** | 核心记忆 | 跨会话知识积累 |

## 核心亮点

- **T-Shirt 分档**：任务自动分级（S/M/L）—— 小任务快，大任务严
- **闭环质量**：每个技能输出可验证证据 —— 不接受"应该没问题"
- **自我进化**：教训沉淀到核心记忆 —— 同一个坑不踩第二次
- **中文团队适配**：全中文触发短语、国内 Git 平台支持、中英双语技能
- **Windows 原生**：PowerShell 命令、端口冲突恢复、路径规范

## 快速开始

### 安装

将 `.trae/` 目录复制到你的 Trae 项目根目录即可。无需插件，无需脚本。

### 试试这些指令

> "帮我排查这个报错"
> "先写计划再实现"
> "改好了没？验证一下"
> "帮我提交"
> "记住这个处理方式"

## 文档导航

| 文档 | 说明 |
|:-----|:-----|
| [docs/01-intro_zh.md](docs/01-intro_zh.md) | 15 秒极简介绍 |
| [docs/02-overview_zh.md](docs/02-overview_zh.md) | 功能亮点介绍（3 分钟）|
| [docs/03-components_zh.md](docs/03-components_zh.md) | 组件速查手册（5 分钟）|
| [docs/04-design_zh.md](docs/04-design_zh.md) | 设计思路与巧思（5 分钟）|
| [docs/05-architecture_zh.md](docs/05-architecture_zh.md) | 完整架构与工作流（15 分钟）|

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

## 贡献指南

欢迎贡献代码！请阅读 [CONTRIBUTING_zh.md](CONTRIBUTING_zh.md) 了解贡献指南。

英文版本请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。
