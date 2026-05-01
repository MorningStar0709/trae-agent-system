---
name: self-improvement
description: Captures learnings, errors, and corrections to enable continuous improvement. Use when a command fails unexpectedly, the user corrects a misunderstanding, an external tool breaks, or a better approach is discovered. 适用于“把这个报错记下来”、“记住我刚才说的规则”、“更新最佳实践”或“把这个教训沉淀下来”等需要自我进化的场景。
---

# Self-Improvement

Capture development insights, command failures, and user feedback into Trae's Core Memory or project-level rules. This ensures the agent learns from mistakes and avoids repeating errors.

## Use This Skill

- **Command/Tool Failure**: An operation fails unexpectedly (e.g., port conflict, missing dependency).
- **User Correction**: The user corrects your output, logic, or architectural approach.
- **Best Practice Discovery**: You find a more efficient or robust way to perform a recurring task.
- **Knowledge Gap**: You realize your understanding of the project or an API is outdated.
- **Task Wrap-up**: Before completing a major task, review if any persistent workarounds should be captured.

## Do Not Use

- Transient network glitch or environment fluke that won't recur.
- Non-technical chat without actionable feedback.
- Routine code change without any new learning involved.
- Task progress summarization (use standard output contracts for that).

## Quick Reference

| Situation | Action |
|-----------|--------|
| New learning discovered | `resources/execution-guide.md` → classify → store |
| Recurring pattern (3+ times) | `resources/promotion-guide.md` → consider Rule |
| Learning qualifies as reusable Skill | `resources/execution-guide.md` → use `skill-creator` |
| Memory is near limit or outdated | `resources/memory-maintenance.md` → audit → DELETE |
| User says "帮我整理记忆" | Ask scope → explain snapshot limit → user verifies total from settings → resources/memory-maintenance.md 用户触发流程 |
| Memory fragments seem to be growing | Ask user → if confirmed, use `resources/memory-maintenance.md` 整合审计 |
| Similar memory already exists | Use UPDATE on existing entry, don't duplicate |

## Output Format

When you finish logging a learning, report back using this format:

```markdown
**教训已记录 (Learning Captured)**
**分类:** `[Core Memory / Project Rule / New Skill]`
**摘要:** [一句话概括]
**应用场景:** [什么情况下会用]
```

After reporting, resume the original workflow that triggered the learning. Do not treat self-improvement as a terminal step — the caller's execution should continue after logging.

## Failure Strategy

- **Unclear Correction**: Ask for clarification before logging.
- **Redundant Memory**: Use UPDATE to merge with existing; don't create duplicates.
- **Sensitive Data**: NEVER log secrets, tokens, or private keys.
- **Low-Value Learning**: Skip trivial/obvious insights to avoid memory pollution.
- **Tool Unavailable**: If `manage_core_memory` fails, fall back to manual capture via `resources/execution-guide.md`; if any script fails, retry once before reporting failure.

## Integration

- `systematic-debugging`: Client — non-obvious root causes are logged via self-improvement as `knowledge_gap` or `insight`.
- `test-driven-development`: Client — false-green tests discovered during mutation testing are logged as anti-pattern experiences.
- `verification-before-completion`: Client — non-obvious validation failures are logged as `Experience`.
- `finishing-a-development-branch`: Client — during branch wrap-up, persistent workarounds and rule discoveries are promoted via self-improvement.
- `subagent-driven-development`: Client — repeated subagent failures are logged to prevent future mis-routing.
