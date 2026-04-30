# Skill + Rule Workflow and Component Reference

> This document provides a concise introduction to all components (Rules / Skills) in this system — their responsibilities, trigger conditions, and positions in the workflow. Quick lookup for "who does what, when to use".
>
> For complete overview, see [05-architecture.md](./05-architecture.md).

---

## 1. Workflow Overview

### Feature Development Flow (M/L Level)

**Phase 1: Routing**
- `skill-routing-and-execution-path` performs T-Shirt sizing (S/M/L)
- `forced-escalation-guardrails` intercepts high-risk tasks misclassified as S
- Routes to corresponding skill based on task type

**Phase 2: Design Path**
- `brainstorming` → clarify fuzzy requirements into design solutions
- `writing-plans` → break stable solutions into executable task plans

**Phase 3: Execution Path**
- `executing-plans` → sequential execution in current session
- `subagent-driven-development` → subagent independent execution + two-layer review

**Phase 4: Quality Gates**
- `verification-before-completion` → verify before claiming completion
- `requesting-code-review` / `receiving-code-review` → independent review and feedback

**Phase 5: Completion Path**
- `git-commit` → commit with Conventional Commits
- `finishing-a-development-branch` → branch completion (merge/PR/keep/discard)
- `self-improvement` → store lessons in Core Memory

### Bug Fix Flow

1. Route to `systematic-debugging`
2. Read symptoms → stable reproduction → narrow scope → form hypothesis → verify → fix → confirm
3. Enter completion path
4. Non-obvious root cause → `self-improvement` stores memory

### Knowledge Accumulation Flow

Command failure / user correction / best practice discovery / knowledge gap → `self-improvement` → categorized storage (Knowledge / Rule / Experience) to Core Memory

---

## 2. Rules Layer

Rules are stored in `.trae/rules/`, controlled by YAML frontmatter.

### 2.1 Always Apply Rules (Loaded Every Conversation)

| Rule | One-Line Responsibility | Why Important |
|:-----|:------------------------|:--------------|
| **change-proposal-threshold** | Self-check "is it worth changing" before modifying rules/skills | Prevents Agent from casually proposing refactoring |
| **question-threshold** | Precisely define "must ask" and "must not ask" scenarios | Users are only interrupted when decisions are truly needed |
| **forced-escalation-guardrails** | 7 high-risk task categories must not be treated as small tasks | Protects core configs, security, CI/CD from careless handling |
| **terminal-execution-stability** | Use stable evidence instead of terminal guessing | Eliminates "looks successful" false passes |

### 2.2 Conditional Trigger Rules (Loaded on Smart Match)

| Rule | Trigger Condition | What It Does |
|:-----|:------------------|:-------------|
| **skill-routing-and-execution-path** | Non-trivial development tasks | T-Shirt sizing + route to correct skill, system's traffic hub |
| **review-and-completion-gates** | Task approaching completion | Orchestrate 5-step completion sequence |
| **environment-resilience** | MCP tool connection failure | Three-tier degradation: retry → PowerShell fallback → report limitation |
| **port-conflict-recovery** | Port conflict/zombie process | netstat PID → taskkill → verify release → retry |

---

## 3. Skills Layer

Skills are stored in `skills/<skill-name>/SKILL.md`, triggered by Agent automatically matching `description`.

### 3.1 Design & Planning Path

| Skill | Input | Output | One-Line Responsibility |
|:------|:------|:-------|:------------------------|
| **brainstorming** | Fuzzy requirements | Inline design summary / spec file | Transform "roughly want to do X" into "specifically do X" |
| **writing-plans** | Stable design/spec | Executable multi-task plan | Break "what to do" into "first edit A → then B → run verification → commit" |

### 3.2 Execution Path

| Skill | When to Use | How It Works |
|:------|:------------|:-------------|
| **executing-plans** | High task coupling / subagents not supported | Sequential execution, batch review point every 3 tasks |
| **subagent-driven-development** | Independent tasks / subagents supported | New subagent per task → spec review → code quality review, advance one at a time |

### 3.3 Debugging & Quality Path

| Skill | One-Line Responsibility | Core Principle |
|:------|:------------------------|:---------------|
| **systematic-debugging** | Find root cause with evidence chain before fixing | No fix proposal until root cause is confirmed |
| **test-driven-development** | Write tests first for behavior changes/regression risks | Red → Green → Refactor |
| **verification-before-completion** | Verify with fresh evidence before completion | No fresh evidence, no claim of completion |
| **requesting-code-review** | Request independent review | Earlier review, cheaper cost |
| **receiving-code-review** | Handle review feedback | Review comments are technical input, not dogma |

### 3.4 Completion & Evolution Path

| Skill | One-Line Responsibility | Key Behavior |
|:------|:------------------------|:-------------|
| **git-commit** | Commit with Conventional Commits | type English + scope/body Chinese |
| **finishing-a-development-branch** | Branch completion decisions | Verify first → then options (merge/PR/keep/discard) |
| **self-improvement** | Store lessons as persistent knowledge | Classify → dedupe → capacity check → write to Core Memory/Rule/Skill |

### 3.5 Orchestration & Tools Path

| Skill | When to Use |
|:------|:------------|
| **dispatching-parallel-agents** | 2+ independent read-only/analysis tasks needing parallel execution |
| **workflow-runner** | Multi-role (PM/architect/QA) collaboration YAML orchestration |
| **discovering-subagent-capabilities** | Need to confirm available subagent types in current environment |
| **find-docs** | Need to query latest official docs for frameworks/libs/SDKs |
| **chinese-git-workflow** | Project hosted on Gitee/GitLab/Coding instead of GitHub |
| **chinese-copywriting** | Need to format Chinese technical docs (mixed Chinese/English, punctuation rules) |

### 3.6 Browser & Frontend Path

| Skill | When to Use |
|:------|:------------|
| **chrome-devtools** | Need browser automation, debugging, Console/Network/DOM inspection |
| **frontend-design** | Need to build or beautify frontend UI |
| **chart-visualization** | Need to generate data charts (line/bar/pie/word cloud, etc.) |
| **a11y-debugging** | Need accessibility checks (ARIA labels, keyboard navigation, color contrast) |
| **debug-optimize-lcp** | LCP / Core Web Vitals optimization |
| **memory-leak-debugging** | JS / browser memory leak investigation |

### 3.7 Meta Skills (Skill Management)

| Skill | When to Use |
|:------|:------------|
| **skill-creator** | Create or modify SKILL.md |
| **skill-stability-review** | Review skill package stability (16 review dimensions) |
| **skill-language-policy** | Define repo-level language policy (machine English / user Chinese) |
| **creating-trae-rules** | Create or modify `.trae/rules/` rule files |

---

## 4. Routing Decision Quick Reference

### T-Shirt Sizing Summary

```
S (Small) → Go direct, skip design/plan skills
  ├─ ≤3 files
  ├─ Mechanical changes (copy, rename, type fix)
  └─ No forced escalation triggers

M (Medium) → writing-plans → executing-plans
  ├─ 4-10 files
  ├─ Non-trivial but design is clear
  └─ Optional TDD

L/XL (Large) → brainstorming required first
  ├─ Cross-module/multi-system
  ├─ Fuzzy requirements/architecture changes
  └─ Design → split → implement
```

### Skill Routing Quick Reference

| If the task is... | Use this skill |
|:------------------|:---------------|
| Fuzzy requirements, don't know what to do | brainstorming |
| Design is clear, need to split tasks | writing-plans |
| Has Bug / test failure / build failure | systematic-debugging |
| Behavior change needs regression prevention | test-driven-development |
| Need to commit code | git-commit |
| Need branch completion | finishing-a-development-branch |
| Need to stop repeating mistakes | self-improvement |

---

## 5. Platform Adaptation Points

### Trae IDE Mechanisms

- **Rule Activation**: alwaysApply (auto-load) / description (smart match) / globs (file match) / `#Rule` (manual reference)
- **Skill Trigger**: Agent automatically matches SKILL.md `description` against user intent
- **Memory Management**: `manage_core_memory` tool, user + project up to 20 entries each
- **Subagents**: `Task` tool with `subagent_type` parameter for dynamic dispatch

### Windows Environment

- Unified PowerShell syntax (`Select-String` instead of `grep`, etc.)
- Port conflicts use `netstat` + `taskkill`
- `globs` use forward slashes

### Chinese Teams

- Skill description embeds Chinese trigger phrases ("帮我提交", "逐步排查", etc.)
- Commit message format: `type` English + `scope/body` Chinese
- Domestic Git platforms: `finishing-a-development-branch` detects remote via `git remote -v` and routes accordingly
- Skill files: machine layer (frontmatter) English + user layer (process description) Chinese

---

> This document is for quick reference. For complete definitions, execution protocols, input/output contracts, and failure handling of each component (Rule / Skill), see the corresponding source files (`.trae/rules/` or `skills/<name>/SKILL.md`).
>
> **Design Philosophy (one-liner)**: Rules make decisions (who to point to), Skills perform actions (how to do it), Trae native capabilities as foundation (don't break or replace), original mechanisms add value (T-Shirt sizing, question thresholds), Chinese adaptation enhances experience (layered Chinese/English strategy).
>
> More resources:
> - **Quick intro** → [01-intro.md](./01-intro.md)
> - **Design philosophy** → [04-design.md](./04-design.md)
> - **Features highlight** → [02-overview.md](./02-overview.md)
> - **Complete overview** → [05-architecture.md](./05-architecture.md)
