---
alwaysApply: true
description: Always-active task classification and process routing. Apply T-Shirt Sizing before any code change to determine the correct process path (S/M/L). Covers classification rules, Forced Escalation Guardrails, Skill Routing Table, and S/M/L execution flows. See also: forced-escalation-guardrails.md.
---

# Skill Routing And Execution Path

- Apply T-Shirt Sizing to bypass heavyweight processes for small tasks:

  | Dimension | **Small (S)** | **Medium (M)** | **Large (L/XL)** |
  |:----------|:--------------|:----------------|:------------------|
  | **File scope** | ≤3 files | 4–10 files | Cross-module / multi-system |
  | **Change nature** | Mechanical or well-known logic | Non-trivial but design is clear | Ambiguous requirements, architecture changes |
  | **Risk level** | No forced escalation triggers | Has triggers, but change nature is clear | Has triggers + architecture/scope uncertainty |
  | **Expected pace** | Single focused pass | Multiple iterations needed | Needs design → split → implement |

  When scores are inconsistent, the largest T-Shirt size across all four dimensions determines classification. (E.g., File scope=S, Change nature=M, Risk level=M, Expected pace=S → final=M.)
  **When undecidable**: If any dimension cannot be assessed with reasonable confidence, default to the largest possible size for that dimension. (E.g., unsure whether Change nature is M or L → assume L. Unsure about Risk level triggers → assume M.) This ensures safety by defaulting up rather than down.
  **Module definition for File scope**: A "module" is a functional unit with its own directory boundary (e.g., `src/auth/`, `src/api/`). Changes spanning multiple such directories count as cross-module. Test files in a co-located `__tests__/` or `test/` directory within the same module do not count as a separate module.
  **Test files in File scope**: Test files count toward the file count. E.g., 2 implementation files + 2 test files = 4 files → File scope is M.
  **Small (S)** — Direct Path. Do NOT route to `brainstorming` or `writing-plans`.
  **Exception to Escalation**: Even if 4+ files or cross-module, if purely mechanical (copy tweaks, trivial renames, type fixes, one-line config, global path updates), still treat as S.
  **Note — Exception vs Guardrails priority**: The Forced Escalation Guardrails (`forced-escalation-guardrails.md`) take precedence over the Exception to Escalation. If a change is purely mechanical but hits any Guardrails scenario (e.g., auth/security files), the minimum classification is M, not S.
  **Assessment order**: Score the four dimensions first. Then cross-check the result against the Forced Escalation Guardrails — if any Guardrails scenario is triggered, the minimum classification is M. The final classification is the larger value between the four-dimension result and the Guardrails-implied floor. (E.g., four-dimension result=S, but triggers Guardrails → final=M. Four-dimension result=M, also triggers Guardrails → final=M. Four-dimension result=L, triggers Guardrails → final=L.)
  **Medium (M)** — Route to `writing-plans` → `executing-plans`. If behavioral correctness is critical, use `test-driven-development` instead of the entire `writing-plans` → `executing-plans` chain.
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
  | New session, need project context before starting | `memory-kernel` | scanning the entire project from scratch |
  | "你还记得吗", cross-session memory recall | `memory-kernel` | guessing from current context |

- **Flow Overview (by T-Shirt Size)** — consolidates the complete path from entry to branch wrap-up. The `review-and-completion-gates.md` rule controls gate skipping (S skips code review) and fast-path consolidation (S appends wrap-up guidance directly after verification).

  Memory is embedded at three points in every path:
  - **Entry**: `memory-kernel` read — load cross-session context before starting
  - **Mid (M/L only)**: `memory-kernel` write — persist interim learnings during long tasks
  - **Exit**: `memory-kernel` write — persist key outcomes after verification

  **S (Direct Path):**
  `[memory-kernel: read]` → `implementation` → `verification-before-completion` → `[memory-kernel: write if anything cross-session worthy]` → [`finishing-a-development-branch` appended directly]
  > S path commits after `verification-before-completion` passes (plain `git commit` by default; route to `git-commit` skill if a conventional commit message is preferred).
  > If a debuggable bug is discovered during implementation, switch to `systematic-debugging` (see Skill Routing Table) — the S path is no longer appropriate.

  **M (Structured Path):**
  `[memory-kernel: read]` → `writing-plans` → `executing-plans` or `subagent-driven-development` → (with periodic `memory-kernel: write` during long-running execution) → `verification-before-completion` → `[memory-kernel: write — key outcomes]` → `requesting-code-review`
  > **Choice rule**: Prefer `executing-plans` when tasks are tightly coupled or the environment lacks reliable implementation subagents. Prefer `subagent-driven-development` when tasks are mostly independent and implementation subagents are available. (`writing-plans` already explains the choice in its execution recommendations.)
    ├── (no feedback) → [`self-improvement` Knowledge Promotion Gate (also writes to MCP Memory via `memory-kernel`)] → `[memory-kernel: write — promotion results]` → `finishing-a-development-branch`
    └── (feedback received) → (`receiving-code-review`) → `verification-before-completion` (if fixes applied) → (`git-commit` if fixes applied) → [`self-improvement` Knowledge Promotion Gate (also writes to MCP Memory)] → `[memory-kernel: write — promotion + fix outcomes]` → `finishing-a-development-branch`

  **L (Design-First Path):**
  `[memory-kernel: read]` → `brainstorming` (with `memory-kernel: write` for design decisions) → [enter M path from `writing-plans` onward]

- **Alternative entry points**: The flow above is the default development path. The Skill Routing Table handles specialized scenarios (debugging, TDD, code review, git ops, self-improvement) that bypass or re-enter this main path at different points.

- **Subagent Dispatch**: When main agent is deep in context and an independent sub-task arises, consider dispatching to a subagent. See `dispatching-parallel-agents` skill for the full decision table and pre-flight protocol. During M/L execution (e.g., inside `executing-plans` or `subagent-driven-development`), if 2+ independent read-only analysis tasks are identified, `dispatching-parallel-agents` can be inserted as an optimization — it is not part of the fixed flow.
- **Skill inventory**: Use `skills/*/SKILL.md` as source of truth. Do not maintain a hardcoded list in this rule.

When proposing changes to rules, skills, or configuration, see `change-proposal-threshold.md`.
