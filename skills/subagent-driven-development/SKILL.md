---
name: subagent-driven-development
description: Use when you need to execute a written implementation plan in the current conversation by assigning mostly independent tasks to fresh implementation-capable subagents with two-stage reviews, including Chinese requests such as “每个任务派子代理做”“子代理驱动开发”“按任务拆给子代理实现”. Do not use when the environment lacks real implementation-capable subagents, the tasks are tightly coupled, or executing-plans is the safer path.
---

# Subagent-Driven Development

## Overview

Execute a plan by assigning a fresh implementation-capable subagent for each task, enforcing a two-stage review after every task: first checking spec compliance, then code quality.

Three core principles:
- Use a fresh subagent for each task to avoid context pollution.
- Advance only one task at a time; do not dispatch implementation work in parallel.
- If any review fails, the implementation subagent must fix the issue before re-review.

Use this skill only if the current environment genuinely supports implementation-capable subagents (can read context, edit code, run validations, and return results). Otherwise, fallback to `executing-plans`.

## Use This Skill

- A written implementation plan exists, and tasks are mostly independent.
- The current environment supports subagents capable of implementing code safely through an "implement -> review -> fix" loop.
- You want to reduce cross-task pollution via context isolation and enforce two-stage review gates.

## Do Not Use

- Requirements are still fuzzy or no written plan exists; use `brainstorming` or `writing-plans` first.
- The current environment only has search/review subagents, lacking true implementation subagents.
- Tasks are tightly coupled and require continuous shared context; inline sequential execution is safer, so switch to `executing-plans`.

## Input Contract

Required inputs:
- A readable written implementation plan.
- A task list clear enough to judge boundaries and independence.
- Confirmation that implementation-capable subagents exist in the current environment.

Optional but highly recommended inputs:
- Plan file path.
- Current branch or workspace context.
- Architectural context, dependencies, and constraints relevant to each task.
- Whether the user requires commits after tasks are completed.
- **Context Payload from upstream skill (e.g., `writing-plans`, `systematic-debugging`)**: When handed off from an upstream skill, read the `[Context Payload]` block from the conversation. Distribute relevant fields (e.g., `Affected Components`, `Residual Risk`, `Fix Guidance`) into each task's context before dispatching to subagents.

Missing input handling:
- **No written plan**: Do not schedule subagents; switch to `writing-plans`.
- **Cannot confirm implementation subagents exist**: Use `discovering-subagent-capabilities` to check the `subagent_type` enum. If no implementation-capable subagent is listed, do not risk it; fallback to `executing-plans`.
- **Tasks lack independence**: Stop the subagent approach, explain why, and fallback to `executing-plans`.
- **Missing local context but tasks are fixable**: Supply the context first, then dispatch. Do not force the implementer to blindly read the entire plan file.

## Execution Protocol

Execute in the following order without skipping steps:

1. **Pre-flight: Discover Available Subagents**: Use `discovering-subagent-capabilities` to read the Task tool's `subagent_type` enum. Read each subagent's description and match against the implementation needs (e.g., code writing, code review, MATLAB execution). The enum is dynamic — do not assume a fixed set of agent names. If no implementation-capable subagent is available, fallback to `executing-plans` immediately.
2. Confirm the environment supports implementation subagents and tasks are mostly independent.
3. Read the plan, extracting the full task text, dependencies, and local context for each task.
4. Create a `TodoWrite` list, advancing only one task at a time.
5. For the current task, run the fixed loop: implement -> spec review -> code quality review.
6. If any step fails, return to the corresponding fix step. Do not carry unresolved issues into the next task.
7. After all tasks are completed, run `verification-before-completion` to independently verify the delivery before summarizing and wrapping up. The verification must include re-running tests and reviewing the actual diff — do not solely rely on the subagent's verbal report.

If the environment requirements are not met during execution or task independence was misjudged, stop the subagent path immediately and fallback to `executing-plans`.

## Single Task Loop

Every task must follow this fixed loop. **Each iteration dispatches a fresh `Task` call** — subagents are stateless and cannot be re-queried mid-conversation. The full instruction must be in the `query` parameter each time.

**Fast-Track Assessment (T-Shirt Sizing):**
- **Low Risk (S):** Pure documentation, simple style tweaks, or single-line isolated fixes.
  - *Fast-Track Flow:* Implementer works -> Controller does a combined quick self-review -> Validate -> Done. (Skip independent Spec/Quality reviewer agents).
- **Normal Risk (M/L):** Feature logic, cross-file changes, or architectural updates.
  - *Standard Flow:* Implementer -> Controller self-review (spec compliance first, then code quality) -> Validate -> Done.

**Standard Flow Steps:**
1. **Dispatch implementer**: Fire a single `Task` call with `subagent_type` matching the implementation need. The `description` should be a short label (3-5 chars), the `query` must contain the full task text and all necessary context. The subagent returns exactly **once** — you cannot follow up with additional questions.
2. **Receive result**: The implementation subagent returns a structured state (`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED`).
3. If `NEEDS_CONTEXT` -> gather the missing context and fire a new `Task` with the original task + supplementary context.
4. If the implementation phase is ready, the controller performs a two-stage self-review: **spec compliance first, then code quality**.
5. Spec compliance and code quality are reviewed sequentially by the same controller — these are two distinct review **passes**, not two independent reviewers.
6. Only after both passes pass can the task be marked completed in `TodoWrite`.

Sequential constraints:
- Only one task can be `in_progress` at a time.
- Only one implementation subagent handles the current task at a time.
- Code quality review cannot start before spec review passes.
- Cannot advance to the next task if any review has unresolved issues.

## State and Block Rules

The implementer is only allowed to return four states:
- `DONE`: Implementation complete, ready for spec review.
- `DONE_WITH_CONCERNS`: Implementation complete but with concerns. Read the concerns before deciding whether to proceed to spec review.
- `NEEDS_CONTEXT`: Missing context. Gather the context and re-dispatch the current task.
- `BLOCKED`: Task cannot continue. Must alter context, split the task, upgrade capabilities, or fallback.

Handling rules:
- Do not ignore `NEEDS_CONTEXT` or `BLOCKED`.
- Do not blindly retry the same task without changes.
- If the issue is missing context, supply it and re-dispatch.
- If the task is too large or the plan has gaps, split or fix the plan before continuing.
- If the task repeatedly fails, context bloats endlessly, or the loop cannot close stably, stop this skill and switch to `executing-plans`.

## Red Lines

- Starting implementation on `main`/`master` without explicit user permission.
- Dispatching multiple implementation subagents in parallel.
- Skipping spec compliance or code quality reviews.
- Using implementer self-review as a substitute for formal review.
- Starting code quality review before spec compliance passes.
- Forcing the implementer to read the plan file instead of providing the full task text.
- Ignoring issues raised by the implementer or reviewer.
- Marking a task complete when any review loop remains open.

## Output Contract

After each task, the controller must hold this structured information:
- Original Intent.
- Task number and name.
- Implementer state.
- Spec review conclusion.
- Code quality review conclusion.
- Test/validation results.
- Modified files.
- Unresolved issues or accepted risks.

The final reply must use this fixed skeleton:

```markdown
子代理驱动执行已完成。

**Plan:** `<plan-path>`
**Original Intent:** `<intent-summary>`
**Execution Conclusion:** `Fully Completed` | `Partially Completed` | `Blocked`
**Task Progress:** `<completed>/<total>`

**Task Results:**
- Task N: `Passed` | `Blocked` | `Needs Fix`

**Review Results:**
- Spec Compliance: [Passed / Issue Summary]
- Code Quality: [Passed / Issue Summary]

**Validation Results:**
- [Tests / lint / build / manual checks]

**Blocks or Risks:**
- [If none, write `- None`]

**Next Steps:**
- [Continue fixing / Switch to executing-plans / Await user decision / Run verification-before-completion, then proceed to commit or branch wrap-up]
```

If execution is incomplete, do not use "子代理驱动执行已完成。" to mask the state. Explicitly state which task is stuck, at which phase, and why.

## Failure Handling

- **Implementer returns `NEEDS_CONTEXT`**: Supply context and re-dispatch the same task. Do not enter review.
- **Implementer returns `BLOCKED`**: Determine if it is a context, capability, or plan defect. Do not retry without changes.
- **Spec Review Fails**: After the implementer fixes it, it must undergo spec review again. Do not jump to code quality review.
- **Code Quality Review Fails**: After the implementer fixes it, it must undergo code quality review again.
- **Repeated Task Failures or Context Bloat**: Stop the subagent path, explain the situation to the user, invoke `self-improvement` to record why subagent-driven-development failed for this task type (e.g., task too large, insufficient context isolation, capability gap), and suggest switching to `executing-plans`.
- **Environment Cannot Support Loop**: Fallback immediately. Do not pretend subagents are viable.

## Integration

- `writing-plans`: Upstream — the plan is generated by writing-plans before subagent execution begins.
- `executing-plans`: Downstream fallback — when subagent-driven-development fails repeatedly or tasks are too tightly coupled, fall back to sequential execution.
- `verification-before-completion`: Downstream — after all tasks are completed, verify evidence before claiming done.
- `using-git-worktrees`: Adjacent — subagent tasks can run inside isolated worktrees for context separation.
- `discovering-subagent-capabilities`: Upstream — before dispatching, use this skill to verify which implementation-capable subagent types are available.
