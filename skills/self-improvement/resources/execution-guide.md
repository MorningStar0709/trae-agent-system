# Execution Guide

Detailed instructions for the three storage paths referenced from SKILL.md.

## Path A: Core Memory (Default)

For concise rules, habits, or operational experiences.

1. Use the `manage_core_memory` tool
2. Set `action` to `ADD` (new) or `UPDATE` (merge with existing)
3. Set `scope`:
   - `project`: repo-specific facts and conventions
   - `user`: global personal habits and preferences
4. Write concise, bulleted `content` under 400 characters
5. Generate 3-5 `keywords` separated by `|`
6. Set a short descriptive `title`
7. Set `category` to `Experience`, `Rule`, or `Knowledge`
8. Set `via` to `discovery` or `request`

### Category Selection Guide

| Category | When to Use | Example |
|----------|-------------|---------|
| `Experience` | Workaround, troubleshooting path, operational rule | "If port 3000 is in use, check and kill it before retrying" |
| `Rule` | User preference or coding convention | "Always use pnpm instead of npm in this repo" |
| `Knowledge` | Stable fact about architecture or domain | "This project uses module-scoped fixtures for DB tests" |

## Path B: Project Rules

For complex conventions that need automatic triggering on specific files.

1. Create or update a markdown file in `.trae/rules/`
2. Use `creating-trae-rules` conventions:
   - `alwaysApply`: always loaded
   - `description`: when this rule applies
   - `globs`: file patterns to trigger on
3. Example: `.trae/rules/testing-conventions.md`
4. Real-world example in this workspace: [environment-resilience.md](file:///c:/Users/skyler/.trae/rules/environment-resilience.md) — a rule that was created from a series of recurring port conflict and MCP-failure experiences.

## Path C: Reusable Skill

For repeatable, multi-step workflows (e.g., deployment sequence).

1. Recommend creating a new Skill to the user
2. Only extract when ALL criteria are met:
   - **Verified**: solution is confirmed working
   - **Broadly applicable**: not a one-off fix
   - **Non-obvious**: required actual investigation
   - **Testable**: instructions are self-contained and actionable
3. If the user agrees, use `skill-creator` or `agent-blueprint-architect` to scaffold the new Skill
