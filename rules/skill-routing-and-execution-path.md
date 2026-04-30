---
alwaysApply: false
description: Route non-trivial dev tasks to the right skill: brainstorming (ambiguous design), writing-plans (complex features), systematic-debugging (bugs), TDD (behavioral changes). See forced-escalation-guardrails.md for S→M escalation.
---

# Skill Routing And Execution Path

- Apply T-Shirt Sizing to bypass heavyweight processes for small tasks:

  | Dimension | **Small (S)** | **Medium (M)** | **Large (L/XL)** |
  |:----------|:--------------|:----------------|:------------------|
  | **File scope** | ≤3 files | 4–10 files | Cross-module / multi-system |
  | **Change nature** | Mechanical or well-known logic | Non-trivial but design is clear | Ambiguous requirements, architecture changes |
  | **Risk level** | No forced escalation triggers | Has triggers, but change nature is clear | Has triggers + architecture/scope uncertainty |
  | **Expected pace** | Single focused pass | Multiple iterations needed | Needs design → split → implement |

  When scores are inconsistent, the highest-risk dimension determines classification.
  **Small (S)** — Direct Path. Do NOT route to `brainstorming` or `writing-plans`.
  **Exception to Escalation**: Even if 4+ files or cross-module, if purely mechanical (copy tweaks, trivial renames, type fixes, one-line config, global path updates), still treat as S.
  **Medium (M)** — Route to `writing-plans` → `executing-plans`. If behavioral correctness is critical, use `test-driven-development` instead.
  **Large (L/XL)** — Must start with `brainstorming`.

- **Forced Escalation Guardrails**: See `forced-escalation-guardrails.md` for 7 scenarios never treatable as Small (S).
- Before routing generically, first check if a dedicated skill or subagent is a clearer match.

- **Skill Routing Table**:

  | If the task is... | Route to | Instead of |
  |:------------------|:---------|:-----------|
  | Exploratory, ambiguous, architecture/design | `brainstorming` | implementing directly |
  | Stable design, complex, needs task breakdown | `writing-plans` | coding ad-hoc |
  | Bug, test failure, build break, unclear behavior | `systematic-debugging` | guessing a fix |
  | Behavioral change with regression risk | `test-driven-development` | untested implementation |
  | Multi-role orchestration or YAML workflow | `workflow-runner` | single-skill execution |
  | Configuring Git for domestic platforms | `chinese-git-workflow` | manual remote setup |
  | Git commit | `git-commit` | raw `git commit -m` |
  | 2+ independent read-only analysis tasks | `dispatching-parallel-agents` | sequential execution |
  | Command/tool failure, user correction, new insight | `self-improvement` | ignoring the learning |
  | Code review feedback to apply | `receiving-code-review` | blindly accepting comments |

- **Flow Overview (by T-Shirt Size)** — consolidates the complete path from entry to branch wrap-up. The `review-and-completion-gates.md` rule controls gate skipping (S skips code review) and fast-path consolidation (S appends wrap-up guidance directly after verification).

  **S (Direct Path):**
  `implementation` → `verification-before-completion` → [`finishing-a-development-branch` appended directly]

  **M (Structured Path):**
  `writing-plans` → `executing-plans` or `subagent-driven-development` → `verification-before-completion` → `requesting-code-review` → (`receiving-code-review` if feedback) → `verification-before-completion` → `git-commit` → `finishing-a-development-branch`

  **L (Design-First Path):**
  `brainstorming` → [enter M path from `writing-plans` onward]

- **Alternative entry points**: The flow above is the default development path. The Skill Routing Table handles specialized scenarios (debugging, TDD, code review, git ops, self-improvement) that bypass or re-enter this main path at different points.

- **Subagent Dispatch**: When main agent is deep in context and an independent sub-task arises, consider dispatching to a subagent. See `dispatching-parallel-agents` skill for the full decision table and pre-flight protocol.
- **Skill inventory**: Use `skills/*/SKILL.md` as source of truth. Do not maintain a hardcoded list in this rule.

When proposing changes to rules, skills, or configuration, see `change-proposal-threshold.md`.
