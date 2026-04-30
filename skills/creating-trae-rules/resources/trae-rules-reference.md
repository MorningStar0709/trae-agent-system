# Trae Rules Reference

This reference summarizes Trae IDE rule behavior from the official Trae rules documentation at https://docs.trae.ai/ide/rules?_lang=zh.

## Rule Types

- Personal rules reflect the user's own habits and apply across all projects. They are created in Trae settings. Draft them as plain text unless the user provides an export/import format.
- Project rules are Markdown files that apply only to the current project or module. They live under `.trae/rules/`.

## Project Rule Format

Project rules use YAML frontmatter followed by Markdown content:

```markdown
---
alwaysApply: false
description: Use this rule when writing React component tests
---

# React Component Tests

- Use the existing test helpers.
- Prefer user-visible queries.
```

Supported frontmatter keys documented by Trae:

- `alwaysApply`: boolean. `true` means the rule applies in every AI conversation for the current project scope.
- `globs`: file patterns used by specific-file rules.
- `description`: scenario text used by intelligent rules.
- `scene`: special scene marker. `scene: git_message` applies when Trae generates commit messages.

## Activation Modes

Always apply:

```yaml
---
alwaysApply: true
---
```

Specific files:

```yaml
---
alwaysApply: false
globs: src/**/*.ts,src/**/*.tsx
---
```

Intelligent apply:

```yaml
---
alwaysApply: false
description: Use this rule when editing API route handlers
---
```

Manual only:

```yaml
---
alwaysApply: false
---
```

Manual rules apply when the user references them with `#Rule`. `#Rule` has the highest priority and can also force use of specific-file or intelligent rules in the current conversation.

## Paths and Nesting

Project root rules:

```text
.trae/rules/general-rules.md
.trae/rules/frontend/react-best-practices.md
.trae/rules/backend/api-design.md
```

Trae reads nested folders under `.trae/rules/` recursively up to three nested levels. A fourth level is not recognized.

Module-level rules:

```text
my-project/
├── .trae/rules/global-style.md
├── frontend-module/
│   ├── AGENTS.md
│   └── .trae/rules/react-best-practices.md
└── backend-module/
    └── .trae/rules/api-design.md
```

Module-level `.trae/rules/` and `AGENTS.md` apply when the user mentions files under that module or Trae reads files under that module during a task.

## AGENTS.md and Claude Files

Trae can read project `AGENTS.md`, `CLAUDE.md`, and `CLAUDE.local.md` when the relevant settings are enabled. Use `AGENTS.md` for lightweight Markdown instructions that should be reusable by tools supporting AGENTS.md. Use `.trae/rules/` when frontmatter-controlled activation is needed.

## Commit Message Rules

Trae supports commit message generation rules with:

```yaml
---
scene: git_message
---
```

If multiple rule files include `scene: git_message`, Trae follows all of them when generating commit messages. The `scene` field is compatible with `alwaysApply`, `description`, and `globs`, but any rule containing `scene: git_message` applies to commit message generation regardless of those activation settings.

Recommended filename:

```text
.trae/rules/git-commit-message.md
```

## Best Practices

- Keep each rule small, focused, and non-conflicting.
- Use project-root-relative paths in `globs`.
- Prefer module-level rules for module-specific technology stacks or business domains.
- Prefer intelligent apply for scenario-based guidance.
- Prefer specific-file rules for file-extension or directory constraints.
- Prefer always apply only for universal project constraints.
- Start a fresh conversation after creating or changing rules when testing behavior, so old context does not compete with new rules.

### Design Principles

- **路由规则管"指向谁"，skill 管"能不能执行"**：规则决定任务该路由到哪个 skill（"这个 bug 该走 systematic-debugging"），但环境前置条件（Git 是否安装、网络是否可用、工具是否存在）应放在 skill 自己的 Failure Handling 中。规则不检测 skill 的运行时环境。违反此原则会导致规则膨胀且规则不加载时检测失效。
- **不把 skill 的执行约束提升为规则**：如果一个约束只影响某个 skill 而非整个流程，把它放在该 skill 的 Do Not Use 或 Failure Handling 中。只有当约束影响多条路线时（如"没有 Git 时不路由到任何 git 相关 skill"），才考虑放入规则。
- **规则做决策，skill 做操作**：规则的文件体应该以"如果 X，使用 Y"的决策语句为主。操作细节（具体命令、参数、路径示例）属于 skill 的内容。如果规则的某条语句超过 2 行且包含具体命令，考虑将其移至对应的 skill。

### Quality Gates

- **description 不超过 250 字符**: Trae 官方推荐值。description 是规则触发的关键匹配字段，过长会降低匹配精度。如果无法精简，说明规则职责不够聚焦，应考虑拆分。
- **规则文件不超过 50 行**: 超出 50 行时，说明该规则承担了过多职责，应按维度拆分为多个独立规则文件（例如: 将路由逻辑与强制升级护栏拆分为两个文件）。
- **alwaysApply 文件行数从严**: `alwaysApply: true` 的文件每次对话都会加载，行数应比 `alwaysApply: false` 更严格。建议 `alwaysApply: true` 文件不超过 30 行。

### Line Limit Decision Strategy

行数标准是**手段**而非**目的**。目的是确保每个 alwaysApply 文件只承载一个独立关注点。达到或超过上限时按此判断：

1. **识别文件是否包含多个独立关注点** — 即去掉一个 section 后剩余内容仍可独立运行，且两个 section 解决不同类的问题（例如：MCP 工具降级 vs 端口冲突恢复）
2. **包含多个独立关注点 → 拆分** — 每个关注点拆为独立的规则文件，各自有清晰的 `description`
3. **单一连贯关注点 → 保留** — 即使自然行数超过标准，也不应为数字而压缩内容或切碎逻辑。在文件顶部用注释说明为何超限
4. **禁止为压行数而删除可操作内容** — 规则的价值在于指导行为，删内容满足标准是本末倒置
