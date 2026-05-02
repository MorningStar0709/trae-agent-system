---
alwaysApply: false
description: Use this rule when a software change is already reviewable or near completion and you need to decide final review, evidence-based verification, feedback-handling, or branch wrap-up before commit, PR, merge, or cleanup.
---

# Review And Completion Gates

- **Completion Gates Execution Order**: When multiple completion gates are involved, execute them in this fixed order:

  1. `verification-before-completion` — Verify your own work with fresh evidence first.
  2. `requesting-code-review` (M/L tasks only; skip for S) — Request independent review after self-verification.
  3. `receiving-code-review` (only if review feedback exists) — Process and apply feedback.
  4. `verification-before-completion` (only if fixes were made in step 3) — Re-verify after applying fixes.
  5. `git-commit` (only if fixes were made in step 3) — Commit fixes before proceeding to branch wrap-up.
  6. `finishing-a-development-branch` — Wrap up the branch last.

  For Small (S) tasks, skip steps 2-5 and go directly from step 1 to step 6.
- **Fast-Path Completion for Small Tasks**: For tasks that were categorized as Small (S) and do not involve core architecture or high-risk regressions, consolidate the completion phase. When concluding `verification-before-completion` successfully, **present validation results first, then append branch wrap-up guidance** (e.g., commit commands or merge suggestions) in the same response, rather than splitting it into multiple fragmented skill invocations.
- Before claiming "done", "fixed", "tests passed", "ready to commit", or "ready to merge", use `verification-before-completion` and base the conclusion on fresh evidence from the relevant checks.
- Do not route to `verification-before-completion` while still in the middle of implementation or troubleshooting with no conclusion yet, or when you are only discussing ideas, risks, or blockers.
- When an independent gate check is useful before handoff, commit, or merge, use `requesting-code-review`.
- Do not route to `requesting-code-review` for from-scratch implementation with no reviewable diff yet, or for extremely small changes where a simple self-check is enough.
- When review feedback already exists and needs to be evaluated or applied, use `receiving-code-review`.
- Do not route to `receiving-code-review` when no actual review feedback exists yet; in that case use `requesting-code-review` or normal implementation flow instead.
- After implementation and validation are complete, use `finishing-a-development-branch` when the task is to decide merge, PR, cleanup, or branch wrap-up actions.
- Do not route to `finishing-a-development-branch` while implementation or verification is still in progress, or when the user only wants a normal commit rather than branch-level wrap-up guidance.
- **Knowledge Promotion Gate**: During branch wrap-up or before completing a major task, check if any persistent workarounds, rule discoveries, or recurring errors occurred. ("Persistent" means ≥2 occurrences during this branch, or a single non-trivial discovery — e.g., an undocumented environment quirk that would cause repeat failures.) If so, invoke `self-improvement` to promote these findings to project-level rules or core memory before closing the task. After `self-improvement` completes, also invoke `memory-kernel` to write the promoted knowledge to MCP Memory for cross-session persistence.
- **Proactive Review Gate (M/L tasks only)**: When completing a Medium or Large task, before closing, do a quick scan of the current system state:
  1. Are there any obvious gaps in the skill coverage or routing rules encountered during this task?
  2. Are there any recurring friction points (manual steps, ambiguous decisions) worth surfacing?
  3. Does the current task's experience suggest any rule or skill needs updating?
  
  Keep this scan brief (3 sentences max). Only flag issues that are concrete and actionable. Do not invent hypothetical problems. If nothing stands out, say nothing.
