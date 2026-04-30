---
name: executing-plans
description: Use when you need to execute a written implementation plan in the current conversation with review checkpoints, including Chinese requests such as “按这个计划执行”“照计划做”“逐任务推进”. It is especially suitable after writing-plans or when the environment does not support implementation-capable subagents. Do not use when requirements are still unclear, no written plan exists, or subagent-driven-development is a better fit for mostly independent tasks.
---

# Executing Plans

## Overview

Load the plan, critically review it, execute all tasks sequentially, and report upon completion.

If the current environment supports implementation-capable subagents, tasks are mostly independent, and you are certain that `subagent-driven-development` can invoke a code-implementing subagent, that is usually a stronger choice. Otherwise, use this skill to execute the plan sequentially in the current conversation.

## Use This Skill

- A written implementation plan exists and needs to be executed sequentially in the current conversation.
- You want to maintain the rhythm of `TodoWrite`, staged reviews, and stopping for confirmation when blocked.
- The current environment lacks reliable implementation-capable subagents, or tasks are tightly coupled, making them unsuitable for independent subagents.

## Do Not Use

- Requirements are still unclear and solutions are undecided; use `brainstorming` first.
- No written plan exists yet; use `writing-plans` first or draft a plan in the current conversation.
- The current environment supports implementation-capable subagents and tasks are mostly independent; `subagent-driven-development` is a better fit.

## Input Contract

Required inputs:
- A readable written implementation plan that outlines tasks, steps, validation requirements, and completion criteria.

Optional but highly recommended inputs:
- Plan file path.
- Current branch or workspace context.
- Whether the user requires commits.
- Key dependencies, environment constraints, or external services involved in the plan.
- **Context Payload from upstream skill (e.g., `writing-plans`, `systematic-debugging`)**: When handed off from an upstream skill, read the `[Context Payload]` block from the conversation. It preserves architecture decisions, ruled-out paths, and residual risks that are not captured in the plan file itself. If present, treat it as supplementary context during the review phase — especially the `Ruled Out` and `Residual Risk` fields.

Missing input handling:
- **No written plan**: Do not start execution; suggest using `writing-plans` instead.
- **Plan readable but key info missing**: Point out the gaps first, then decide if partial progress is possible.
- **Environment better suited for subagent-driven-development**: Explicitly state the reason and suggest switching instead of proceeding blindly.

**Validation Assets:**
- evals: `evals/evals.json`
- examples: `examples/input.md`, `examples/output.md`

## Execution Protocol

Execute in the following order without skipping steps:

1. Confirm the current request is genuinely "execute existing plan".
2. Read the plan and perform a critical review.
3. If the plan is executable, create a `TodoWrite` list and advance task by task.
4. Validate and record results immediately after each task is executed.
5. Output a fixed execution report once all tasks are completed.

If any step is blocked, prioritize reporting the block reason and suggested actions. Do not pretend the execution succeeded.

### Step 1: Load and Review Plan

1. Read the plan file.
2. Critically review: identify any issues or concerns in the plan.
3. If there are concerns: raise them with your human partner before starting.
4. If there are no concerns: create a `TodoWrite` list and continue.

**Focus during review:**
- Are there missing dependencies between steps? (e.g., A depends on B, but B is scheduled after A)
- Are validation conditions clear? ("Confirm it works" is not enough; "Run `npm test` and all pass" is clear)
- Are there implicit environment assumptions? (Node version, database connection, API keys)

**Review Output Structure:**
```markdown
执行前审查已完成。

**计划路径:** `<plan-path>`
**审查结论:** `可执行` | `需澄清`
**发现的问题:**
- [若无问题，请写 "- 无"]
**建议的操作:**
- [若无问题，请写 "- 继续执行"]
```

### Step 2: Execute Tasks

For each task:
1. **Mark as In Progress**: Update `TodoWrite`.
2. **Understand Goal**: Re-read the task description and clarify completion criteria.
3. **Implement**: Strictly follow the plan steps (the plan already contains sub-steps).
4. **Validate**: Run required tests or checks.
5. **Commit**: If required, commit changes after each task, referencing the task number in the commit message.
6. **Mark as Completed**: Update `TodoWrite`.

**Batch Review Checkpoints:**
- Pause and review after every 3 tasks: Is the overall direction still correct? Have we deviated from the plan?
- If previous implementations have issues, fix them before continuing. Do not carry problems forward.

**Task Progression Rules:**
- Only one task can be `in_progress` at a time.
- Write actual validation results at the end of each task, not just "Validated".
- Do not mark a task as completed if it requires user confirmation to continue.
- If the plan conflicts with actual implementation conditions, stop and return to "Step 1: Load and Review Plan" if necessary.

### Step 3: Block and Fallback Rules

Stop current progress and report immediately (do not guess) when:
- Missing dependencies, environments, credentials, or external services.
- Tests fail and the cause is unconfirmed.
- Instructions or acceptance criteria are unclear.
- Plan conflicts with actual implementation conditions.
- The same validation fails more than twice consecutively.

**Handling:**
- **Implementation Bug**: Fix and re-run validation.
- **Test Issue**: Fix the test and explain the reason.
- **Plan Gap or Sequence Error**: Return to Step 1 to re-review the plan.
- **Missing Dependency**: Report the missing item, affected tasks, and suggested remedy.
- **Fundamental Deviation Required**: Explain the deviation, reason, and impact first. Do not adjust without permission.
- **Rollback Needed**: If a completed task introduced an issue, do not attempt to "fix forward" blindly. Reset to the last known-good checkpoint using git:
  ```powershell
  git log --oneline -5
  git reset --hard <last-known-good-commit>
  ```
  If no commits exist, use `git checkout .` to discard uncommitted changes, then re-verify the task scope before proceeding.

### Step 4: Complete Development

After all tasks are completed and validated:
- Summarize completion status, validation results, and any plan deviations.
- If the user requested commits, use available commit processes (prefer `git-commit` if available, else standard git).
- If the user did not request commits, do not arbitrarily add wrap-up processes.

## Failure Handling

- **Plan Missing/Unreadable**: Stop execution, report path issue.
- **Validation Conditions Missing**: Review and ask for clarification, do not assume.
- **Missing Dependency During Task**: Pause and explain missing item, affected tasks, suggested remedy.
- **Validation Fails >2 Times**: Enter blocked state, report attempted fixes.
- **Current Branch Unsuitable**: Explain risk, do not implement on `main`/`master` without permission.
- **User Did Not Request Commit**: Do not automatically upgrade "Execution Complete" to "Commit Complete".

## Output Contract

The final output must contain at least:
- Original Intent
- Plan path
- Review conclusion
- Task completion status
- Validation results
- Plan deviations
- Next step suggestions

Use this fixed skeleton:

```markdown
执行已完成。

**原始意图:** `<original-intent>`
**计划路径:** `<plan-path>`
**执行结论:** `全部完成` | `部分完成` | `遇到阻塞`
**任务进度:** `<已完成>/<总数>`

**已完成的任务:**
- [任务编号 + 结果]

**验证结果:**
- [测试 / 代码检查 / 构建 / 手动检查]

**计划偏离:**
- [若无偏离，请写 "- 无"]

**阻塞或风险:**
- [若无阻塞，请写 "- 无"]

**下一步:**
- [如果要求提交代码，说明提交路径；否则，等待指示]
```

如果执行未完全结束，请勿使用“执行已完成。”来掩饰状态；应使用 `部分完成` 或 `遇到阻塞`，并明确说明剩余任务和阻塞条件。

## Integration

- `writing-plans`: Upstream — the plan is generated by writing-plans before executing-plans begins.
- `brainstorming`: Upstream — when requirements are not yet clarified, brainstorming must precede plan generation.
- `subagent-driven-development`: Alternative downstream — when tasks are mostly independent and the environment supports implementation subagents, subagent-driven-development is preferred over sequential execution.
- `verification-before-completion`: Downstream — after execution, verify evidence before claiming done. Must run before `git-commit`.
- `git-commit`: Downstream — after validation passes through `verification-before-completion`, commit the completed work. Do not reverse the order.
