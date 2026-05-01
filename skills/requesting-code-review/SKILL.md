---
name: requesting-code-review
description: Use when you need an independent code review before commit, merge, or task handoff, including Chinese requests such as “帮我 review”“合并前审一下”“看看这次改动有没有问题”. Do not use for from-scratch implementation work with no reviewable diff yet, or when the user only wants a code explanation instead of a risk-focused review.
---

# Requesting Code Review

## Overview

Use this skill to request an independent code review for the current changes before continuing development, committing, or merging. The goal is not just to follow a process, but to catch behavioral regressions, architectural risks, missed requirements, and testing gaps as early as possible.

**Core Principle:** The earlier the review, the cheaper the fix.

## Use This Skill

- After completing a major feature.
- After fixing a complex bug.
- Before merging or committing.
- After a subagent or batch task finishes, when you want an independent gate check.
- The user explicitly asks for a review, code review, or to check the changes.

## Do Not Use

- The current task is a from-scratch implementation with no reviewable diff yet.
- The user is asking how to handle received feedback; use `receiving-code-review` instead.
- The user only wants to understand the code, not review its quality and risks.
- The change is extremely small and involves no behavioral changes; a simple self-check is enough.

## Execution Protocol

### 1. Determine Review Scope

Provide a clear scope for the changes rather than a vague "please take a look".

Common scopes:
- Changes after a single task completes.
- The diff of a feature branch relative to the base branch.
- The most recent commit.
- A few specific key files.

### 2. Gather Review Context

Prepare at least the following information:
- What was changed.
- Why it was changed.
- The corresponding requirement, plan, or bug.
- The git scope to review.
- Which validations have already been run.

PowerShell example:
```powershell
# Detect default branch dynamically instead of hardcoding origin/main
$DEFAULT_BRANCH = git remote show origin | Select-String "HEAD branch" | ForEach-Object { $_ -replace '.*HEAD branch: ', '' }
if (-not $DEFAULT_BRANCH) { $DEFAULT_BRANCH = "main" }
$BASE_SHA = git merge-base HEAD "origin/$DEFAULT_BRANCH"
$HEAD_SHA = git rev-parse HEAD
git diff --stat $BASE_SHA..$HEAD_SHA
```
If `origin/$DEFAULT_BRANCH` does not exist, fall back to the last stable baseline or the commit from the previous task.

### 3. Initiate Independent Review

If using a subagent, provide the full context, not just "please review".

First, use `discovering-subagent-capabilities` to discover available subagents at runtime. Match the subagent whose description best fits code review. The subagent name is dynamic — do not assume a fixed value.

The `Task` call should follow this pattern:
```
Task(
  description="审查<模块名>",
  query="<完整审查指令>",
  subagent_type="<discovered dynamically>",
  response_language="zh-CN"
)
```

The subagent is stateless and returns exactly once — the query must contain everything needed.

The prompt should include:
- Implementation summary.
- Requirement or plan source.
- `BASE_SHA` / `HEAD_SHA`.
- Risk areas or specific aspects to focus on.
- Template: `requesting-code-review/code-reviewer.md`.

### Review Standards

When providing feedback to a Chinese-speaking user, adopt a constructive, polite, and inquiry-based tone:
- Use suggestions instead of commands (e.g., "建议考虑用 X，因为 Y" instead of "你必须改成 X").
- Use questions instead of negations when unsure of intent (e.g., "这里用 sync 是出于什么考虑？" instead of "不应该用 sync").

Always classify findings by severity:

- `[必须修复]` (Critical): Security vulnerabilities, data loss risks, logical errors. Fix first, then continue.
- `[建议修改]` (Important): Performance issues, maintainability, missing validation. Usually should be fixed before continuing.
- `[仅供参考]` (Minor): Naming improvements, style suggestions, alternative approaches. Record and fix when convenient.
- `[问题]` (Question): Unclear intent, need clarification from the author.
- If the review judgment is wrong: Provide evidence to refute it; do not argue emotionally.

## Trae / Windows Conventions

- Prefer using independent review capabilities available in the current environment; in this environment, use `discovering-subagent-capabilities` first to find the review-capable subagent, then dispatch with `Task`.
- If no suitable review subagent is available, perform a self-review in the current session using the same standards, maintaining a "findings-first" report structure.
- Use PowerShell-compatible commands when getting git information on a Windows host.
- Once review conclusions are ready, hand off to `receiving-code-review` if fixes need to be applied based on the feedback.

## Failure Handling

- **No git baseline**: Switch to file-level review and explicitly state the scope limits.
- **No independent subagent**: Self-review in the current session, but keep the findings-first output.
- **Review scope too large**: Break it into multiple independent scopes to avoid reviewing too much at once.
- **Unclear conclusions**: Return to `receiving-code-review` to clarify before implementing.

## Output Contract

The final output must include:
- The scope that was reviewed.
- The context provided to the reviewer.
- The review findings categorized by severity.
- Recommended next steps (e.g., fix critical issues, proceed to commit).
- If no issues found, explicitly route to `verification-before-completion` before proceeding to commit.

## Integration

- `verification-before-completion`: Upstream — review starts after verification evidence is collected.
- `receiving-code-review`: Downstream — how to validate, clarify, and apply feedback after receiving it.
- `verification-before-completion`: Downstream — final validation after review feedback is fixed.
- `code-reviewer.md`: The independent review prompt template.