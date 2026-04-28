---
name: creating-trae-rules
description: Create, modify, review, or organize Trae IDE rules that live under .trae/rules, module-level .trae/rules folders, AGENTS.md, CLAUDE.md, or git message rule files. Use when the user asks to 创建 rule, 创建规则, 编写 Trae 规则, 适配 Trae rules, set alwaysApply/globs/description/scene, create commit message rules, split project rules by module, or convert team conventions into reusable Trae project rules.
---

# Creating Trae Rules

Use this Skill to produce rules that are valid for Trae IDE and easy for Trae to apply. Prefer creating or editing actual rule files when the target project path is known.

When the user writes in Chinese, discuss choices and final summaries in Simplified Chinese. Keep file names, frontmatter keys, glob patterns, and code identifiers in their original form.

## Inputs

Collect or infer:

- Target scope: whole project, specific module, specific file pattern, intelligent trigger, manual trigger, personal rule draft, or commit message generation.
- Target project or module path. If omitted, inspect the current workspace before asking.
- Rule purpose and constraints.
- Desired activation mode.
- Existing rule files that may conflict or overlap.

Ask one concise question only when the target path or rule purpose is impossible to infer safely.

## Workflow

1. Inspect existing Trae rule surfaces before editing:
   - Project rules: `<project>/.trae/rules/**/*.md`
   - Module rules: `<module>/.trae/rules/**/*.md`
   - Agent files: `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md`
   - Commit message rules: rules containing `scene: git_message`
2. Choose the smallest correct rule surface:
   - Use `.trae/rules/<name>.md` for project rules.
   - Use `<module>/.trae/rules/<name>.md` for module-only behavior.
   - Use `AGENTS.md` only when the user wants a lightweight project instruction file that can be reused by tools supporting AGENTS.md.
   - Draft personal rules as plain text for Trae settings; do not invent a filesystem location for personal rules.
3. Choose activation mode:
   - Always apply: set `alwaysApply: true`.
   - Specific files: set `alwaysApply: false` and `globs`.
   - Intelligent apply: set `alwaysApply: false` and `description`.
   - Manual only: set `alwaysApply: false` and omit `globs` and `description` unless the user explicitly wants metadata for clarity.
   - Commit message: add `scene: git_message`; this can coexist with `alwaysApply`, `description`, and `globs`.
4. Write the rule with YAML frontmatter followed by Markdown instructions.
5. Keep each rule focused. Split rules when one file mixes unrelated concerns such as UI style, API design, testing, and commit messages.
6. Validate:
   - Frontmatter is bounded by `---`.
   - Boolean fields are real booleans, not quoted strings.
   - `globs` uses project-root-relative patterns.
   - Rule files are no deeper than three nested levels under `.trae/rules/`.
   - No new rule contradicts an existing rule.
7. Summarize changed files, activation behavior, and any assumptions.

## Rule Templates

Use templates only when helpful:

- `templates/always-apply.md`: whole-project rule.
- `templates/specific-files.md`: file-pattern rule.
- `templates/intelligent-apply.md`: semantic trigger rule.
- `templates/manual-only.md`: #Rule-only rule.
- `templates/git-message.md`: commit message generation rule.

For exact Trae behavior and examples, read `resources/trae-rules-reference.md` when creating or reviewing non-trivial rules.

## Writing Rules

Use this structure:

```markdown
---
alwaysApply: false
description: Brief scenario where Trae should use this rule
---

# Rule Title

- Do this concrete thing.
- Avoid this concrete failure mode.
- Prefer this local convention when choices are otherwise equivalent.
```

Write instructions as actionable constraints, not explanations about why the rule exists. Prefer bullets that Trae can follow during execution.

Good rule content:

```markdown
- Use the existing repository test helper instead of introducing a new test runner.
- Keep generated files out of source changes unless the user explicitly asks for regenerated artifacts.
- When editing React components, follow the nearby component naming and import order.
```

Avoid vague content:

```markdown
- Make the code better.
- Follow best practices.
- Be careful.
```

## File Placement

Use forward slashes in examples and globs.

Examples:

```text
.trae/rules/general-style.md
.trae/rules/frontend/react-components.md
frontend-module/.trae/rules/react-best-practices.md
backend-module/.trae/rules/api-design.md
AGENTS.md
```

Do not create rules below the fourth nested level under `.trae/rules/`; Trae recognizes up to three levels of nesting.

## Failure Handling

- Missing target project: inspect the current directory. If no project root is clear, ask for the target folder.
- Existing conflicting rule: report the conflict and either update the existing rule or ask before creating a competing one.
- Personal rule request: provide the rule text and tell the user it belongs in Trae settings, not `.trae/rules`.
- Unknown activation mode: choose intelligent apply for scenario-specific guidance, specific-files for file-pattern guidance, always apply only for truly universal constraints, and manual only for rarely needed specialist guidance.
- Commit message rule already exists: update the existing `scene: git_message` rule instead of creating a duplicate unless the user asks for multiple commit rules.
