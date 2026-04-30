# 角色目录约定

`workflow-runner` 默认把 YAML 中的 `role` 映射到 `<agents_dir>/<role>.md`。

## 规则

- `agents_dir` 是角色根目录，可以是相对路径。
- `role` 必须使用斜杠路径，例如 `analysis/researcher`。
- 实际角色文件路径应为 `sample-agents/analysis/researcher.md` 这种形式。
- 每个角色文件至少包含一段 frontmatter 和一段正文说明。

## 最小角色文件格式

```md
---
name: Researcher
---

你是一个负责澄清问题空间的角色。

工作目标：
- 提炼目标
- 识别约束

输出要求：
- 使用结构化要点
```

## 推荐约定

- frontmatter 中只保留稳定、可读的最小字段
- 正文明确角色目标、边界和输出要求
- 一个文件只定义一个角色
- 角色名用英文或原始技术命名，正文可用中文
