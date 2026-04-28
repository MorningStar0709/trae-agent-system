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
