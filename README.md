# Trae AI Agent 操作系统

[![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)](https://www.trae.ai/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

[English](./README.md) | [中文](./README_zh.md)

---

## About This Project

**Trae AI Agent OS** is an AI Agent enhancement system for [Trae IDE](https://www.trae.ai/). It provides Rule-based routing, professional Skills, and persistent Memory capabilities — transforming your Agent from "can do anything but unstable" to "fast when simple, rigorous when complex, always learning".

## Architecture

```
User Input → Rules (Routing & Constraints) → Skills (Execution) → Memory (Learning)
```

| Layer | Count | Responsibility |
|:------|:------|:---------------|
| **Rules** | 8 | Routing decisions, behavior constraints, environment handling |
| **Skills** | 35 | Professional toolboxes covering design → coding → debugging → commit → completion |
| **Memory** | Core Memory | Cross-session knowledge accumulation |

## Core Features

- **T-Shirt Sizing**: Automatic task classification (S/M/L) — small tasks are fast, large tasks are thorough
- **Closed-Loop Quality**: Every skill produces verifiable evidence — no "should be fine" allowed
- **Self-Improvement**: Lessons learned are stored in Core Memory — never repeat the same mistake
- **Chinese Team Ready**: Native Chinese triggers, domestic Git platform support, bilingual skill files
- **Windows Native**: PowerShell commands, port conflict recovery, path conventions

## Quick Start

### Installation

Copy the `.trae/` directory to your Trae project root. No plugins or scripts required.

### Try These Commands

> "帮我排查这个报错" (Help me debug this error)
> "先写计划再实现" (Write a plan first, then implement)
> "改好了没？验证一下" (Is it fixed? Verify it)
> "帮我提交" (Help me commit)
> "记住这个处理方式" (Remember this approach)

## Documentation

| Doc | Description |
|:----|:------------|
| [docs/01-intro.md](docs/01-intro.md) | 15-second overview |
| [docs/02-overview.md](docs/02-overview.md) | Features & highlights (3 min) |
| [docs/03-components.md](docs/03-components.md) | Component quick reference (5 min) |
| [docs/04-design.md](docs/04-design.md) | Design decisions & rationale (5 min) |
| [docs/05-architecture.md](docs/05-architecture.md) | Complete architecture & workflows (15 min) |

## Skill Paths

| Path | Skills |
|:-----|:-------|
| **Design & Planning** | brainstorming → writing-plans → executing-plans / subagent-driven-development |
| **Debugging & Quality** | systematic-debugging → test-driven-development → verification-before-completion |
| **Completion & Evolution** | git-commit → finishing-a-development-branch → self-improvement |
| **Orchestration** | dispatching-parallel-agents, workflow-runner, find-docs |
| **Browser & Frontend** | chrome-devtools, frontend-design, chart-visualization, a11y-debugging |
| **Meta Skills** | skill-creator, skill-stability-review, skill-language-policy, creating-trae-rules |

## Windows/Trae Adaptation

- **PowerShell Commands**: Primary syntax for Windows environments
- **Port Recovery**: netstat → taskkill → verify → retry
- **Path Conventions**: Forward slashes in globs, absolute paths with backslashes
- **Core Memory**: 20-entry limit per scope, auto-eviction for stale entries

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

For Chinese version, see [CONTRIBUTING_zh.md](CONTRIBUTING_zh.md).

## License

This project is licensed under the [MIT License](LICENSE).
