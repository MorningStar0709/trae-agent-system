# Trae AI Agent System Skills and Rules System: Product Overview

> **Document Version:** v1.1 | **Last Updated:** 2026-04-30 | **Author:** AI Agent Architecture Team
>
> This document introduces the Skill + Rule system architecture, workflows, core pain points solved, and evolution roadmap from a product manager perspective. All content is adapted for **Trae IDE platform features** and **Chinese team scenarios**.
>
> Companion documents:
> **Quick Intro** → [01-intro.md](./01-intro.md) (15-second overview)
>
> - **Getting Started** → [02-overview.md](./02-overview.md) (features & highlights)
> - **Component Reference** → [03-components.md](./03-components.md) (one-line responsibilities)

***

## 1. Background & Positioning

### 1.1 What This Project Is

This project is essentially a **"Cognitive Operating System for AI Agents"** — providing Trae IDE's AI Agent with:

- **Routing Decision Capability**: Knows which skill to use for which task
- **Behavior Constraint System**: Knows what can/cannot be done, when to ask users
- **Execution Protocol Standards**: Knows how to execute each step and what format to output
- **Continuous Evolution Mechanism**: Learns from every interaction, never repeats the same mistake

### 1.2 Platform Foundation: Trae IDE

This system is deeply integrated with Trae IDE's platform capabilities:

- **Rule Mechanism**: Markdown files in `.trae/rules/` with YAML frontmatter support four activation modes: alwaysApply (always loaded), description (smart scene matching), globs (file matching), scene: git\_message (commit messages). Rules support 3-level nesting with project-level and module-level overrides.
- **Skill Mechanism**: Defined via `skills/<skill-name>/SKILL.md` files. Each Skill contains frontmatter metadata (name/description), Input Contract, Execution Protocol, Failure Handling, and Integration. Skills are triggered via the Agent's `Skill` tool — the Agent compares SKILL.md descriptions against current intent and auto-loads matching skills.
- **Core Memory System**: Managed via `manage_core_memory` tool, supporting Knowledge / Rule / Experience memory types. XML static snapshots injected at new conversation start, user and project each max 20 entries.
- **Subagent System**: Dynamic dispatch via `Task` tool's `subagent_type` parameter. Each subagent returns structured results (DONE / DONE\_WITH\_CONCERNS / NEEDS\_CONTEXT / BLOCKED) after independent execution.
- **IDE Built-in Tools**: RunCommand (terminal), Read/Write/SearchReplace (file ops), Grep/Glob/SearchCodebase (code search), GetDiagnostics (language diagnostics), WebSearch/WebFetch (web retrieval), AskUserQuestion (user interaction), OpenPreview (preview service).
- **MCP Ecosystem**: Supports Chrome DevTools MCP (browser automation), Everything Search MCP (Windows file search), and other external tools.

All Rules and Skills in this project are stored in the project root `.trae/` folder in Trae-recognizable format.

### 1.3 Why This System Is Needed

AI Agents working in IDEs fundamentally face three contradictions:

| Contradiction                 | Manifestation                                                  | Consequence of Not Solving                              |
| :---------------------------- | :------------------------------------------------------------- | :------------------------------------------------------ |
| **General vs Specialized**    | Agent can do anything, but nothing well                        | Simple tasks over-complicated, complex tasks mishandled |
| **Proactive vs Controllable** | More proactive = more mistakes, more conservative = useless    | Either reckless operations or constant user questions   |
| **Single vs Continuous**      | Every conversation starts from scratch, no memory accumulation | Same pitfalls repeated, same knowledge re-learned       |

This system is designed to solve these three contradictions.

***

## 2. System Architecture Overview

The system is divided into four layers, passing top to bottom: User Input → Rules Layer (routing decisions) → Skills Layer (execution) → Memory Layer (learning).

**Layer 1: User Interaction Layer (User Input)**
User issues command, enters Rules Layer.

**Layer 2: Rules Layer** — Responsible for routing decisions

- **alwaysApply Rules** (`alwaysApply: true` in YAML frontmatter, auto-loaded every conversation):
  - Change proposal threshold, question threshold, forced escalation guardrails, terminal execution stability, skill routing and execution path
- **Conditional Trigger Rules** (`alwaysApply: false` + `description`, auto-loaded when Agent semantically matches relevant scene):
  - Review and completion gates, environment degradation (MCP failure handling), port conflict recovery
- **Manual Rules** (`alwaysApply: false` + no description, loaded only when user manually references via `#Rule rule-name`): For rarely-used specialized guidance

Rules stored in `.trae/rules/`, supporting project root and module-level subdirectories (max 3 levels nesting). Rules Layer makes routing decisions and dispatches to Skills Layer.

**Layer 3: Skills Layer** — Responsible for specific execution
Each Skill corresponds to a `skills/<skill-name>/SKILL.md` file. Agent triggers by comparing the file's `description` field against current user intent. Skills organized by path:

- **Design & Planning Path**: brainstorming → writing-plans → executing-plans / subagent-driven-development
- **Debugging & Quality Path**: systematic-debugging → test-driven-development → verification-before-completion
- **Completion & Evolution Path**: verification-before-completion → git-commit → finishing-a-development-branch → self-improvement
- **Orchestration & Tools Path**: dispatching-parallel-agents / workflow-runner / discovering-subagent-capabilities / find-docs
- **Browser & Frontend Path**: chrome-devtools / frontend-design / chart-visualization / a11y-debugging / memory-leak-debugging
- **Meta Skills Path** (skill management): skill-creator / skill-stability-review / skill-language-policy

After Skills Layer execution, storable lessons are passed to Memory Layer.

**Layer 4: Memory Layer (Core Memory)** — Responsible for learning accumulation
Managed via Trae's `manage_core_memory` tool, categorized by type:

- **Knowledge** (stable knowledge: architecture, domain info)
- **Rule** (user preferences: coding standards, personal habits)
- **Experience** (operational experience: troubleshooting paths, workarounds)

Two scopes: user (cross-project global) and project (current repo only), each max 20 entries. Exceeding limit triggers auto-eviction of least-used entries, requiring proactive maintenance.

**Technical Notes:**

- Rule and skill activation both depend on Trae's frontmatter mechanism — YAML metadata header controls loading strategy
- Agent behavior constraints and execution flows distributed across Rules and Skills layers with different focuses
- All decisions and execution happen in Trae IDE sessions, relying on IDE built-in tools rather than external scripts

### 2.1 Core Design Principles

**Principle 1: Routing rules decide who to point to, Skills decide if they can execute**

- Rules make decisions ("this bug should go to systematic-debugging")
- Skills perform actions ("execute these steps to locate the problem")
- Environment prerequisites go in Skill's Failure Handling, not elevated to Rules Layer

**Principle 2: Don't elevate Skill execution constraints to rules**

- Constraints affecting only a single Skill → put inside that Skill
- Constraints affecting multiple paths → consider writing to Rules Layer

**Principle 3: Rules make decisions, Skills perform actions**

- Rule body mainly contains "if X, use Y" decision statements
- Operation details (commands, parameters, paths) belong to Skill content

### 2.2 Complete System Overview

#### Five-Layer Core Pipeline

| Layer                                | Components                                                                                                                                       | Responsibility                                                           |
| :----------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------- |
| **Infrastructure** (6 Metaskills)    | self-improvement / creating-trae-rules / skill-creator / skill-stability-review / skill-language-policy / discovering-subagent-capabilities      | Maintain the system itself — learning, rule management, Skill management |
| **Guardrails** (8 Rules)             | 5 alwaysApply + 3 conditional trigger                                                                                                            | Routing decisions, behavior constraints, environment handling            |
| **Design & Planning** (2 Skills)     | brainstorming → writing-plans                                                                                                                    | Clarify fuzzy requirements, break stable designs into executable plans   |
| **Execution** (7 Skills)             | executing-plans / subagent-driven-development / workflow-runner / TDD / systematic-debugging / dispatching-parallel-agents / using-git-worktrees | Plan execution, debugging, test-driven development                       |
| **Verification & Review** (3 Skills) | verification-before-completion → requesting-code-review → receiving-code-review                                                                  | Evidence-based verification, independent review, feedback processing     |
| **Completion** (2 Skills)            | git-commit → finishing-a-development-branch                                                                                                      | Standardized commits, branch wrap-up                                     |

#### Routing Flow (S/M/L Three-Tier Path)

| Tier           | Routing Path                                                                                    | Applicable Scenarios                                   |
| :------------- | :---------------------------------------------------------------------------------------------- | :----------------------------------------------------- |
| **S (Small)**  | Implement → verification → finishing-branch                                                     | ≤3 files, mechanical changes, no risk triggers         |
| **M (Medium)** | writing-plans → executing-plans/subagent-driven → verify → review → re-verify → commit → finish | 4-10 files, non-trivial but design clear               |
| **L (Large)**  | brainstorming → \[enter M path]                                                                 | Cross-module, fuzzy requirements, architecture changes |

#### Tools Layer / Specialized Skills (13 pluggable)

| Category               | Skills                                                                        |
| :--------------------- | :---------------------------------------------------------------------------- |
| **Browser Debugging**  | chrome-devtools / a11y-debugging / memory-leak-debugging / debug-optimize-lcp |
| **Frontend & Design**  | frontend-design / visual-brainstorming                                        |
| **Charts**             | chart-visualization                                                           |
| **Search & Docs**      | everything-search / find-docs                                                 |
| **Chinese / Domestic** | chinese-copywriting / chinese-git-workflow                                    |
| **Troubleshooting**    | troubleshooting                                                               |
| **Agent Architecture** | agent-blueprint-architect                                                     |

***

## 3. Rules Layer Deep Dive

### 3.0 How Rules Work in Trae IDE

All rule files in this project are stored in `.trae/rules/`, using YAML frontmatter to control loading behavior. Trae IDE supports four rule activation modes:

| Activation Mode       | Frontmatter Config                    | When Loaded                                              | Applicable Scenario                                                      |
| :-------------------- | :------------------------------------ | :------------------------------------------------------- | :----------------------------------------------------------------------- |
| **Always Apply**      | `alwaysApply: true`                   | Auto-loaded every new conversation                       | Global behavior constraints (question boundaries, escalation guardrails) |
| **Intelligent Apply** | `alwaysApply: false` + `description`  | When Agent semantically matches relevant scene           | Scene guidance (routing rules, completion gates)                         |
| **Specific File**     | `alwaysApply: false` + `globs`        | When user operates files matching glob pattern           | File-type-specific rules                                                 |
| **Manual Only**       | `alwaysApply: false` + no description | Only when user manually references via `#Rule rule-name` | Rarely-used specialized guides                                           |

**Rule Design Quality Standards** (see `creating-trae-rules` skill):

- description不超过 250 字符：过长会降低 Agent 匹配精度
- Rule files不超过 50 行：超出说明职责不聚焦，应考虑拆分
- alwaysApply files行数从严：建议不超过 30 行，只承载一个独立关注点
- 禁止为压缩行数而删除可操作内容

Trae also supports **module-level rules**: create `.trae/rules/` or `AGENTS.md` in sub-module directories, triggered only when user mentions that module's files. Max 3-level rule nesting.

### 3.1 alwaysApply Rules (Global Guardrails)

These five rule types are auto-loaded every conversation, ensuring Agent follows basic behavior standards and routing decisions in any scenario:

| Rule File                           | Responsibility                 | One-Line Summary                                         |
| :---------------------------------- | :----------------------------- | :------------------------------------------------------- |
| **change-proposal-threshold.md**    | Change proposal self-check     | Before changing rules/Skills, ask "is it worth changing" |
| **question-threshold.md**           | Question boundary control      | Defines when must ask users, when must not               |
| **forced-escalation-guardrails.md** | S-level task forced escalation | 7 high-risk scenarios must not be treated as small tasks |
| **terminal-execution-stability.md** | Terminal operation discipline  | Terminal is an evidence tool, not a guessing tool        |
| **skill-routing-and-execution-path.md** | Core routing             | T-Shirt sizing + route to correct skill, always loaded to ensure classification completeness |

#### 3.1.1 change-proposal-threshold: Change Proposal Threshold

> **Pain Point Solved:** Agent no longer casually suggests refactoring/changing rules/switching approaches.

This is a five-dimension self-check matrix:

| Dimension            | Self-Question                                              | Negative Conclusion                     |
| :------------------- | :--------------------------------------------------------- | :-------------------------------------- |
| **Problem Clarity**  | Is this a specific, recurring pain point?                  | No → Don't change                       |
| **Impact Scope**     | Affects multiple workflows or saves rounds of interaction? | No → Not worth it                       |
| **Maintenance Cost** | Maintenance cost of change > problem solved?               | Yes → Don't change                      |
| **Risk**             | Will it break existing workflows or create ambiguity?      | Yes → Only propose with risk mitigation |
| **Alternatives**     | Is there a simpler path?                                   | Yes → Take simpler path                 |

If net benefit is clear → propose directly; marginal → mention only as observation; negative → internalize, don't propose.

#### 3.1.2 question-threshold: Question Threshold

> **Pain Point Solved:** Agent no longer endlessly questions users, nor makes disastrous autonomous decisions.

**MUST Ask scenarios:**

- Ambiguous intent: request has two or more reasonable interpretations, codebase cannot distinguish
- Unknown external dependencies: involves technologies/tools/services not existing in project
- Unclear scope: lacks boundaries (e.g., "optimize performance" without target metrics)
- Out-of-project modifications: task involves files outside project not mentioned by user
- Business knowledge dependency: answer depends on domain knowledge not documented in codebase

**MUST NOT Ask scenarios:**

- Answer is in codebase
- Only one reasonable path
- Wrong choice can be one-click rolled back with no side effects
- Following project conventions is sufficient
- User already provided sufficient information

#### 3.1.3 forced-escalation-guardrails: Forced Escalation Guardrails

> **Pain Point Solved:** High-risk tasks like core configs/security/CI-CD won't be carelessly handled as "small changes".

The following 7 scenarios **must not be treated as S (Small) tasks**, minimum M (Medium):

1. Modifying core config files (package.json, database schema, global state management)
2. Modifying public APIs, shared components, interfaces depended on by other modules
3. "Simple" bug without evidence-confirmed root cause (must go through systematic-debugging first)
4. Foreseeable side effects or regression risks (must go through TDD first)
5. Auth/authz/security-sensitive logic
6. CI/CD pipelines, deployment scripts, Dockerfiles, infrastructure code
7. Destructive operations (data migration, batch deletion, filesystem operations, database schema changes)

#### 3.1.4 terminal-execution-stability: Terminal Execution Stability

> **Pain Point Solved:** Agent no longer concludes based on "looks successful", no longer uses complex shell tricks instead of stable evidence.

Core disciplines:

- Readable evidence > clever shell: prioritize simple commands + IDE tools
- Short checks use blocking mode, servers use non-blocking
- Long output written to file then checked, don't rely on terminal truncation
- IDE tools prioritized over terminal parsing (Read > Grep > terminal)
- Don't guess: when output is lost or ambiguous, narrow scope and re-run

### 3.2 Conditional Trigger Rules (Smart Matching)

| Rule File                               | Trigger Scenario              | Responsibility                                                  |
| :-------------------------------------- | :---------------------------- | :-------------------------------------------------------------- |
| **review-and-completion-gates.md**      | Task approaching completion   | Completion gate execution sequence orchestration                |
| **environment-resilience.md**           | MCP tool connection failure   | Graceful degradation chain (retry → terminal fallback → report) |
| **port-conflict-recovery.md**           | Port conflict/zombie process  | Windows port recovery process                                   |

#### 3.2.1 skill-routing-and-execution-path: Core Routing (alwaysApply)

> This rule has been upgraded from conditional trigger to `alwaysApply: true`, ensuring T-Shirt classification is performed before any code change to prevent incorrect routing due to missed classification.

This is the **traffic hub** of the entire system. It classifies tasks via T-Shirt Sizing, then routes to the correct skill based on task type:

**T-Shirt 4-Dimension Matrix:**

| Dimension     | S (Small)                     | M (Medium)                    | L/XL (Large)                             |
| :------------ | :---------------------------- | :---------------------------- | :--------------------------------------- |
| File Scope    | ≤3 files                      | 4-10 files                    | Cross-module/multi-system                |
| Change Nature | Mechanical/known logic        | Non-trivial but design clear  | Fuzzy requirements/architecture changes  |
| Risk Level    | No forced escalation triggers | Has triggers but change clear | Has triggers + architectural uncertainty |
| Expected Pace | Single focused pass           | Requires multiple iterations  | Design → split → implement               |

**Judgment Rules (core fixes from this round):**
- **When dimensions conflict**: Take the largest T-Shirt size across ALL four dimensions (not the "highest risk"). E.g., File=S, Change=M, Risk=M, Pace=S → final=M.
- **When undecidable**: If any dimension cannot be assessed with reasonable confidence, default to the largest possible size for that dimension to ensure safety.
- **Module definition**: A "module" is a functional unit with its own directory boundary (e.g., `src/auth/`, `src/api/`). Test files in a co-located `__tests__/` or `test/` directory within the same module do not count as a separate module.
- **Test files counting**: Test files count toward the file count. E.g., 2 impl files + 2 test files = 4 files → File scope is M.
- **Guardrails priority**: Forced Escalation Guardrails take precedence over Exception to Escalation. Assessment order: score four dimensions first → cross-check Guardrails → final classification is the larger value.

**Exception Mechanism**: Even with 4+ files or cross-module, if purely mechanical operations (copy tweaks, trivial renames, type fixes, global path updates), still treat as S. However, if any Guardrails scenario is triggered, minimum classification is M.

**Reclassification during execution**: Classification can be re-evaluated mid-execution. Upward reclassification (S→M, M→L) is **mandatory** — switch immediately when more complexity is found. Downward reclassification is **optional** — stability preferred over optimization.

**Skill Routing Table (Core Mapping):**

| Task Type                              | Route Target                | Alternative (Not Recommended)                      |
| :------------------------------------- | :-------------------------- | :------------------------------------------------- |
| Fuzzy requirements/architecture design | brainstorming               | Direct implementation (will rework)                |
| Bug/test failure/build failure         | systematic-debugging        | Guessing fixes (makes it worse)                    |
| Behavior change/regression risk        | test-driven-development     | Implementation without tests (uncontrollable risk) |
| Clear design/need task splitting       | writing-plans               | Ad-hoc coding (misses boundaries)                  |
| User corrections/new discoveries       | self-improvement            | Ignoring lessons (will repeat)                     |
| Multi-role orchestration               | workflow-runner             | Single skill brute force                           |
| Parallel read-only analysis            | dispatching-parallel-agents | Sequential execution (inefficient)                 |

#### 3.2.2 review-and-completion-gates: Review & Completion Gates

> **Pain Point Solved:** Large task completion won't be skipped, but small tasks won't be crushed by process.

Fixed execution sequence (M/L tasks):

```
1. verification-before-completion      ← Self-verification
2. requesting-code-review              ← Request independent review
3. receiving-code-review               ← Handle review feedback (if any)
4. verification-before-completion      ← Re-verify after fixes (if any)
5. git-commit                          ← Commit fixes (if any)
6. finishing-a-development-branch      ← Branch completion
```

S tasks skip steps 2-5 (directly from step 1 to step 6), taking fast lane. On the S path, commit directly after verification passes and append wrap-up guidance.

Two built-in gates:

- **Knowledge Promotion Gate**: During completion, auto-check for storable lessons. "Persistent" means ≥2 occurrences during this branch, or a single non-trivial discovery (e.g., an undocumented environment quirk). If triggered, invoke self-improvement to write to Core Memory.
- **Proactive Review Gate**: During M/L task completion, quickly scan system state, discover optimizable rule/skill coverage gaps

#### 3.2.3 Environment Degradation & Port Recovery

| Mechanism                  | Problem                             | Solution                                              |
| :------------------------- | :---------------------------------- | :---------------------------------------------------- |
| **environment-resilience** | MCP tool connection timeout/failure | Retry 1x → PowerShell fallback → report limitation    |
| **port-conflict-recovery** | EADDRINUSE/port occupied            | netstat PID → taskkill → verify port released → retry |

***

## 4. Skills Layer Deep Dive

### 4.0 How Skills Work in Trae IDE

Each skill corresponds to a `skills/<skill-name>/SKILL.md` file, using YAML frontmatter for metadata, body defines execution protocol. Skills triggered via:

**Auto-trigger (recommended)**: Agent receives user request, iterates all available Skills' `description` fields, auto-loads complete skill instructions on match. Most common trigger method.

**Manual trigger**: User or upstream flow explicitly calls specific Skill via `Skill` tool.

**Chinese Trigger Phrase Design**: Each Skill's `description` in this project contains bilingual trigger phrases, ensuring Chinese users can match precisely with natural language. For example:

- `systematic-debugging`: description includes "逐步排查" "为什么失败" "先定位原因" "不要先猜修复"
- `writing-plans`: description includes "写实现计划" "拆任务" "先规划再写代码"
- `git-commit`: description includes "帮我提交" "生成提交信息" "提交当前修改" "按规范提交"
- `verification-before-completion`: description includes "确认真的修好了" "提交前再验证一下" "不要没跑就说完成"

This design strategy is called **Agent-First Principle**: description optimizes for Agent semantic matching, ensuring machine readability and trigger stability, while retaining Chinese natural language entry points.

Each SKILL.md follows fixed template structure: name/description → Do Not Use → Input Contract → Execution Protocol → Failure Handling → Output Contract → Integration. This **contract-based design** ensures each skill's behavior is predictable, verifiable, and composable.

### 4.1 Design & Planning Pipeline

Complete pipeline from **fuzzy idea to executable plan**, advancing through these stages:

1. **Fuzzy idea** → Enter brainstorming
2. **brainstorming** → Output design conclusion (inline summary or spec file)
3. **Design conclusion** → Enter writing-plans
4. **writing-plans** → Output execution plan
5. **Execution plan** splits into two exits:
   - **executing-plans** (current session sequential execution, batch review point every 3 tasks)
   - **subagent-driven-development** (subagent independent execution + two-layer review)

- Applicable conditions: executing-plans when environment doesn't support subagents or tasks are highly coupled; subagent-driven-development when environment supports subagents and tasks are independent

#### brainstorming: Brainstorming

- **Responsibility**: Clarify fuzzy requirements into executable design solutions
- **Key design**: Ask one question at a time + prefer multiple choice + show visual prototypes + strict YAGNI scope control
- **Output**: Inline design summary (default) or spec file (complex scenarios)
- **Downstream**: writing-plans / direct implementation / end at design conclusion

#### writing-plans: Plan Writing

- **Responsibility**: Transform stable design into step-by-step execution plan
- **Key design**: Assume downstream executor has zero context, explicitly write file paths, verification commands, expected results
- **Prohibited items**: TBD/TODO/"similar to task N" placeholders
- **Context Payload**: Collect architecture decisions, excluded paths, residual risks from upstream, pass to downstream

#### executing-plans: Sequential Plan Execution

- **Responsibility**: Execute plan tasks sequentially in current session + batch review point every 3 tasks
- **Applicable conditions**: Environment doesn't support reliable subagent implementation, or tasks are highly coupled

#### subagent-driven-development: Subagent-Driven Development

- **Responsibility**: Each independent task dispatched to a fresh subagent, with spec review + code quality review two-layer checkpoints
- **Core principles**: Advance only one task at a time + no shared context between tasks + no progress without passing review
- **Failure degradation**: When subagent conditions not met, fall back to executing-plans

### 4.2 Debugging & Quality Pipeline

Advance sequentially after discovering problems:

1. **Problem discovered** → Enter systematic-debugging
2. **systematic-debugging** → Output root cause confirmation
3. **Root cause confirmed** → Implement fix
4. **Fix complete** → Enter verification-before-completion
5. **Verification passed**, M/L tasks optional branch: requesting-code-review → receiving-code-review (return to step 4 after handling feedback)

#### systematic-debugging: Systematic Debugging

- **Core principle**: No fix proposals until root cause investigation is complete
- **Execution protocol**: Read symptoms → stable reproduction → narrow scope → form hypothesis → verify → fix → confirm
- **Prohibited patterns**: Seeing error, directly guessing fix; skipping evidence collection based on experience

#### test-driven-development: Test-Driven Development

- **Responsibility**: For behavior changes + regression risk scenarios, write tests first then implement
- **Applicable scenarios**: Behavior changes, bug fixes, insufficient existing test coverage

#### verification-before-completion: Verification Before Completion

- **Core principle**: Without fresh evidence, cannot claim completion
- **Execution protocol**: First define "what to prove" → run corresponding verification → read complete results → conclude based on evidence
- **Red line list**: "should be fine", "probably no bug", "I'm confident" — all unverified assertions

#### requesting-code-review / receiving-code-review: Code Review

- Request review → handle feedback, forming complete closed loop
- receiving-code-review core attitude: Review comments are technical input, not directives to blindly follow

### 4.3 Completion & Evolution Pipeline

Advance sequentially through stages:

1. **Task complete** → Enter verification-before-completion
2. **verification-before-completion** → After verification passed, enter git-commit
3. **git-commit** → After commit complete, enter finishing-a-development-branch
4. **finishing-a-development-branch** → self-improvement triggered during completion
5. **self-improvement** → Store lessons as persistent knowledge (Core Memory / Project Rule / New Skill)

#### git-commit: Commit Management

- Supports Conventional Commits format
- **Hybrid format**: type English + scope/body Chinese (for Chinese teams), e.g., `fix(路由规则): 修正 T-Shirt Size 矩阵的 3 个结构缺陷`
  - type stays English for tool compatibility (semantic-release, auto changelog, etc.)
  - scope, description, body use Chinese to reduce team communication cost
- **Granularity standard**: Single atomic change = one commit; multi-file related changes list changes in body; loose combination changes list items individually in body
- **Security protocol**: Don't modify git config, no --no-verify, no force push, don't commit credentials

#### finishing-a-development-branch: Branch Completion

- Provides 4 options: local merge / create PR / keep as-is / discard
- Must confirm verification results first, then give options
- Non-GitHub platforms (Gitee/GitLab/Coding) follow `chinese-git-workflow` for remote config and PR/MR creation
- Domestic Git platform support: `finishing-a-development-branch` detects remote address via `git remote -v` and auto-routes (github.com uses `gh` CLI, others use web UI)

#### self-improvement: Self-Evolution

- **Responsibility**: Store lessons, corrections, and best practices discovered during development as persistent knowledge
- **Four trigger types**: Command failure / user correction / best practice discovery / knowledge gap
- **Three output paths**: Core Memory (Knowledge/Rule/Experience) → Project Rule → New Skill
- **Memory maintenance**: Provides complete integrated audit five-step process (enumerate → categorize → merge → delete → verify)

### 4.4 Orchestration & Tools Path

| Skill                                 | Responsibility                                            | Highlights                                                                                 |
| :------------------------------------ | :-------------------------------------------------------- | :----------------------------------------------------------------------------------------- |
| **dispatching-parallel-agents**       | Parallel dispatch of read-only/analysis tasks             | Pre-detect available subagent types, result aggregation cross-validation                   |
| **workflow-runner**                   | YAML multi-role orchestration simulation                  | Supports DAG dependencies, role directories, multi-round collaboration                     |
| **discovering-subagent-capabilities** | Dynamically discover available subagents                  | Don't hardcode agent names, read system prompt enum                                        |
| **find-docs**                         | Query official technical docs                             | Query framework/lib/SDK docs via Context7                                                  |
| **chinese-git-workflow**              | Domestic Git platform (Gitee/GitLab/Coding) remote config | On-demand manual invocation, provides platform-specific URLs, SSH and mirror sync commands |
| **chinese-copywriting**               | Chinese technical doc formatting & writing standards      | Auto-handle mixed Chinese/English, full-width/half-width, punctuation standards            |

### 4.5 Browser & Frontend Path

| Skill                     | Responsibility                       | Toolchain                        |
| :------------------------ | :----------------------------------- | :------------------------------- |
| **chrome-devtools**       | Browser automation/debugging         | Chrome DevTools MCP              |
| **frontend-design**       | Frontend UI design/beautification    | React/Vue/HTML/CSS               |
| **chart-visualization**   | Data visualization chart generation  | Local JS script generates images |
| **a11y-debugging**        | Accessibility auditing               | Chrome DevTools a11y tools       |
| **debug-optimize-lcp**    | LCP/Core Web Vitals optimization     | Performance trace                |
| **memory-leak-debugging** | JS/browser memory leak investigation | Heap snapshot + memlab           |

### 4.6 Meta Skills Path (Skill Management)

| Skill                      | Responsibility                    | Key Tools                                           |
| :------------------------- | :-------------------------------- | :-------------------------------------------------- |
| **skill-creator**          | Create/modify/review Skills       | quick\_validate.py                                  |
| **skill-stability-review** | Review Skill package stability    | review\_skills.py (888 lines, 16 review dimensions) |
| **skill-language-policy**  | Define repo-level language policy | English-Required / Chinese-Retained layering        |

**skill-language-policy core decision framework**: Skill files in repo adopt "machine layer English + user layer Chinese" layered strategy:

- **English-Required layer**: frontmatter metadata (name/description), tool call parameters, contract interfaces, code examples — these fields are machine-parsed, English enforced
- **Chinese-Retained layer**: process descriptions, failure handling, usage scenario examples, output contract body — these fields are for Chinese user comprehension, Chinese retained
- Don't go to extremes of "all English looks professional" or "all Chinese is easier to read", decide by audience

***

## 5. Complete Workflows: From Requirements to Deployment

### 5.1 Feature Development Complete Flow (M/L Level)

**Phase 1: Routing Dispatch (Step 0 → Step 1)**

After user proposes requirement, `skill-routing-and-execution-path` performs T-Shirt Size matching and routing:

- If involves 7 high-risk categories → `forced-escalation-guardrails` intercepts, S→M
- If requirements are fuzzy → route to brainstorming
- If involves behavior changes → route to test-driven-development
- If involves bug → route to systematic-debugging
- If requirements clear and complex → route to writing-plans

**Phase 2: Design Path**

1. **brainstorming**: Explore project context → provide visual companion (optional) → ask clarifying questions (one at a time) → propose 2-3 options + recommendation → output design conclusion/spec file
2. **writing-plans**: Determine file structure and responsibility boundaries → output tasks one by one (file, steps, verification commands) → self-check (spec coverage, placeholders, type consistency)

**Phase 3: Execution Path**

Choose one of two:

- **executing-plans**: Load and review plan → execute tasks sequentially (TodoWrite tracking) → batch review point every 3 tasks
- **subagent-driven-development**: Dispatch subagent for each independent task → two-layer review (spec review + code quality review)

**Phase 4: Quality Gates**

1. **verification-before-completion**: Re-run tests/build/reproduction path → read complete results, conclude based on evidence
2. **requesting-code-review** (M/L tasks only): Independent review → receiving-code-review (handle feedback)
3. **verification-before-completion** (again): Re-verify after fixes

**Phase 5: Completion Path**

1. **git-commit**: Analyze diff → generate Conventional Commit → execute commit
2. **finishing-a-development-branch**:
   - Knowledge Promotion Gate → self-improvement (store lessons)
   - Proactive Review Gate (scan system gaps)
   - Provide 4 options: local merge / create PR / keep as-is / discard

### 5.2 Bug Fix Flow

1. User reports BUG → `skill-routing` routes to `systematic-debugging`
2. **systematic-debugging executes seven-step process**:
   - Step 1: Read symptoms (error message, stack trace, reproduction conditions)
   - Step 2: Stable reproduction
   - Step 3: Narrow scope (binary search, isolation, comparison)
   - Step 4: Form hypothesis
   - Step 5: Verify hypothesis
   - Step 6: Implement fix
   - Step 7: Confirm (via `verification-before-completion` standard verification)
3. Enter completion path: git-commit → finishing-a-development-branch
4. If non-obvious root cause discovered → invoke `self-improvement` to store as Experience memory

### 5.3 Knowledge Accumulation Flow

Four trigger scenarios may occur during development:

- Command failure (port conflict, missing dependency)
- User corrected wrong understanding
- Discovered better practice approach
- Discovered knowledge gap

Any of the above triggers `self-improvement`, executing:

1. **Classify**: Determine if it's Knowledge (stable facts), Rule (user preferences), or Experience (operational experience)
2. **Dedupe**: Check if similar entry exists → if yes UPDATE, don't create duplicate
3. **Capacity check**: If current scope memory count approaches 20-entry limit → clean up first, then add
4. **Choose persistence path**:
   - Core Memory (via `manage_core_memory` tool)
   - Project Rule (`.trae/rules/` files)
   - New Skill (via `skill-creator`)
5. **Output format**:
   - Classification: Core Memory / Project Rule / New Skill
   - Summary: One-line summary
   - Applicable scenarios: When this would be used

***

## 6. Core Pain Points & Solutions

### Pain Point 1: "Starts coding before requirements are clear"

- **Phenomenon**: User says "help me build a feature", Agent starts coding directly, discovers misunderstanding after finishing, rework cost extremely high.
- **Solution**: `brainstorming` skill intercepts at front end — when requirements are fuzzy, doesn't enter implementation. Through "ask one question at a time" + "show 2-3 options" + "present design section by section and get approval per section", ensures requirements converge before entering implementation.
- **Effect**: Rework rate significantly reduced, user confirms direction at design stage.

### Pain Point 2: "Agent sees Bug, guesses fix"

- **Phenomenon**: After seeing error message, Agent directly gives "looks reasonable" fix code, actually masking the real problem.
- **Solution**: `systematic-debugging` enforces "no fix proposals until root cause investigation complete" — must first stable reproduction → narrow scope → form hypothesis → verify hypothesis, only then fix.
- **Effect**: Fixes no longer guessed, every fix backed by evidence chain.

### Pain Point 3: "Same process for big and small tasks"

- **Phenomenon**: Editing a paragraph goes through full review process, refactoring core modules skipped because process is too long.
- **Solution**: T-Shirt Sizing (S/M/L) three-tier routing. S tasks take fast lane (skip brainstorming/writing-plans, completion skips independent review), M/L tasks take full process. Forced Escalation ensures high-risk tasks aren't treated as S.
- **Effect**: Simple tasks delivered quickly, complex tasks with complete process.

### Pain Point 4: "Done means done"

- **Phenomenon**: Agent says "it's fixed", but didn't run tests or check build, starts debugging only after failure.
- **Solution**: `verification-before-completion` enforces — without fresh evidence cannot claim completion. Must be verifiable conclusions like "tests that just ran all green", "build exit 0", "original bug reproduction path now passes".
- **Effect**: "Should be fine" deleted from vocabulary.

### Pain Point 5: "Same pitfall repeated"

- **Phenomenon**: Port conflict resolution searched once, forgotten next time, stuck again.
- **Solution**: `self-improvement` stores each lesson as persistent knowledge. Non-obvious root cause → stored as Experience; user-corrected preferences → stored as Rule; architecture/domain knowledge → stored as Knowledge. Subsequent conversations auto-injected with these memories.
- **Effect**: When encountering same problem, Agent can "no need to search, solved it last time".

### Pain Point 6: "Agent asks too much or too little"

- **Phenomenon**: Either asks user every step "is this naming okay", or autonomously decides on security-sensitive operations.
- **Solution**: `question-threshold` rule precisely delineates MUST Ask (ambiguity, unknown dependencies, out-of-project operations) and MUST NOT Ask (answer in codebase, single path, rollbackable, follows conventions, user provided sufficient info) boundaries.
- **Effect**: User only interrupted when truly needing decisions, Agent otherwise deduces independently.

### Pain Point 7: "Agent proposes rewriting at the drop of a hat"

- **Phenomenon**: User says "look at this file", Agent replies "suggest refactoring to XXX pattern" — user just wants a small change.
- **Solution**: `change-proposal-threshold` rule enforces self-check — five-dimension matrix (problem clarity / impact scope / maintenance cost / risk / alternatives) evaluation before deciding to propose.
- **Effect**: Agent no longer proactively proposes unevaluated change proposals.

### Pain Point 8: "Knowledge disappears with session"

- **Phenomenon**: New conversation, Agent knows nothing about previous pitfalls and agreements, starts from scratch.
- **Solution**: Core Memory system + `self-improvement` pipeline. At new conversation start, IDE auto-injects user\_scope (global preferences) + project\_scope (repo-specific) memories. Also provides memory maintenance process to prevent auto-eviction.
- **Effect**: Knowledge continuously accumulates cross-session, Agent increasingly "understands" project.

### Pain Point 9: "Subagent context bloat out of control"

- **Phenomenon**: Task dispatched to subagent, subagent context ends up with entire repo, output quality degrades.
- **Solution**: `subagent-driven-development` requires each subagent receive only current task's complete context + `writing-plans` Context Payload curated info. Large tasks pre-split by main Agent into independent small tasks, each subagent focuses on one piece.
- **Effect**: Subagent output quality stable, task boundaries clear.

### Pain Point 10: "MCP tool hangs, task deadlocks"

- **Phenomenon**: Chrome DevTools connection fails → Agent doesn't know what to do → task hangs.
- **Solution**: `environment-resilience` provides three-tier degradation: retry 1x → PowerShell/CLI fallback → report limitation. `port-conflict-recovery` covers port conflict scenarios.
- **Effect**: Tool failure doesn't mean task failure, always an alternative.

### Pain Point 11: "Domestic Git platform adaptation difficult"

- **Phenomenon**: Project uses Gitee or private GitLab, but Agent defaults to GitHub `gh` CLI workflow, push fails, PR can't be created.
- **Solution**: `finishing-a-development-branch` detects remote address via `git remote -v` during completion — github.com uses GitHub standard flow (`git push` + `gh pr create`), gitee.com/gitlab.com/coding.net or other self-hosted platforms only push then guide user to create PR/MR in web UI. `chinese-git-workflow` serves as on-demand remote config knowledge base, providing SSH/HTTPS address formats and mirror sync commands for each platform.
- **Effect**: Regardless of which domestic platform hosts the project, Agent correctly completes remote push and PR creation.

### Pain Point 12: "Trae Rules activation mechanism not intuitive"

- **Phenomenon**: New user writes a rule, but Agent never triggers as expected — possibly forgot to set frontmatter, description too long for accurate matching, or placed in wrong directory level.
- **Solution**: System built-in `creating-trae-rules` skill precisely guides four activation modes (alwaysApply / Intelligent Apply / Specific File / Manual Only) frontmatter config and path standards. Also `skill-stability-review` provides 16-dimension automated review, catching description too long, frontmatter format errors, path over-nesting during rule creation stage.
- **Effect**: Rule correctness changes from "try by feel" to "verifiable", description matching precision guaranteed by 250-character limit constraint.

***

## 7. Design Highlights & Best Practices

> **This document focuses on "why designed this way". For complete design philosophy and engineering trade-offs, see standalone document** **[04-design.md](./04-design.md).**

This system has undergone continuous iteration from scratch, forming the following **7 core design highlights**. Only outlines here, detailed content (including lessons learned and why these decisions) expanded in standalone document:

**7.1 Rule + Skill dual-wheel collaboration, upstream/downstream pipelined**
Rules make decisions (who to point to), Skills perform actions (how to do). Skills declare upstream/downstream via `Integration` field, dynamically assembled at runtime. Context Payload refines and passes design context, preventing downstream info loss.

**7.2 Deep binding with Trae native capabilities, complementary without conflict**
Don't bypass or replace any Trae native mechanism. Core Memory / `manage_core_memory` / `Task` subagent / `Skill` tool / IDE toolset / Rule Frontmatter — each item enhances and standardizes on top of native, not replacing.

**7.3 Follow official specs, don't invent formats**
Don't create custom config formats. Rule files use standard YAML frontmatter, SKILL.md uses official contract template, quality standards from Trae official docs. This system itself is the best practice example of "how to create according to Trae specs".

**7.4 Original decision mechanisms: T-Shirt sizing + question thresholds**
Mechanisms not in Trae native, derived from observing AI Agent daily usage pain points. T-Shirt four-dimension matrix (file scope × change type × risk level × expected pace) and five MUST Ask / five MUST NOT Ask, filling gap in Trae's default "deduce and proceed".

**7.5 agent-blueprint-architect: stability over flashiness**
Don't try to automate Agent creation, output Markdown blueprints users can directly copy-paste. After early attempts to write Python scripts manipulating Trae's encrypted database failed, adjusted to "blueprint delivery + manual paste" mode.

**7.6 Highly optimized Skill internal logic, not one-off prompts**
Each Skill contains Input Contract / Output Contract / Do Not Use / Failure Handling / Integration five-layer structure + red/green line lists. Average 3-5 rounds iteration, git-traceable history.

**7.7 Chinese and Windows layered adaptation, Python for portability**
LLM reasoning uses English for stability, user interaction uses Chinese for experience. Layered Chinese/English isolation strategy + unified PowerShell syntax + Python script cross-platform architecture.

See → [04-design.md](./04-design.md) (design philosophy, including lessons learned and decision trees)

### 7.9 Stability Verification

This system's correctness and stability continuously verified via:

| Verification Dimension       | Method                                                                                                                                                                      | Status                                                                                                                                                        |
| :--------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Name Consistency**         | Item-by-item comparison: 33 Skills' directory names ↔ `name` field ↔ routing table references ↔ cross-skill cross-references                                                | 33/33 consistent, 50+ references unbroken                                                                                                                     |
| **Routing Completeness**     | Verify each routing table reference's skill name → corresponding SKILL.md `name` field → no ambiguity in `description`                                                      | 10 routing paths all reachable, 3 high-risk combinations (executing/subagent, requesting/receiving review, brainstorming/writing-plans) have clear boundaries |
| **Context Payload Matching** | Verify producers (writing-plans, systematic-debugging) output fields correctly consumed by consumers (executing-plans, subagent-driven-development, TDD)                    | Field-to-field complete match, no orphaned output/input fields                                                                                                |
| **Rule Format Compliance**   | Check frontmatter, description, alwaysApply boolean, line limits against creating-trae-rules standards                                                                      | 8 rules all compliant, 4 alwaysApply all ≤30 lines                                                                                                            |
| **Eval Regression Cases**    | Core path Skills (brainstorming, writing-plans, executing-plans, subagent-driven-development, workflow-runner) provide golden path + boundary + regression three-type evals | 5 Skills × several cases, covering correct triggers and reject triggers                                                                                       |
| **Failure Mode Coverage**    | Each Skill's Failure Handling section covers 3-8 failure scenarios with clear degradation paths defined                                                                     | \~150+ failure scenarios defined across 33 Skills                                                                                                             |
| **Git Traceability**         | Track rule iteration and boundary calibration via git commit history                                                                                                        | Multi-round optimization traceable (routing rules 5 rounds, completion gates 3 rounds, guardrail red lines 4 rounds)                                          |

> **Note**: Eval cases stored as JSON files in each Skill's `evals/evals.json`, format `prompt → expected_output`, for manual regression review not CI auto-execution. Can be upgraded to gate if auto-execution environment available.

***

## 8. Evolution Roadmap & Future Direction

### ✅ Completed

- Rule three-layer system established (routing/execution/decision boundaries)
- Complete skill library covering 33 skills
- Core Memory management system
- Agent self-evolution mechanism
- **Trae IDE platform adaptation**: 4 Rule activation modes fully covered, SKILL.md contract template, Windows PowerShell command standards, MCP degradation chain, IDE built-in toolset integration
- **Chinese team adaptation**: Skill Chinese trigger phrases covering all skills, hybrid Conventional Commit format (type English + body Chinese), domestic Git platform auto-routing (Gitee/GitLab/Coding), skill language layering strategy (English-Required/Chinese-Retained), Chinese technical doc formatting standards

### 🔄 Ongoing Optimization

- Rule deduplication and simplification (multiple rounds completed)
- Skill boundary calibration (check if existing skill classifications accurate)
- Memory management automation

### 🔭 Future Outlook

- Smarter task splitting (from T-Shirt to adaptive granularity)
- Skill evaluation and retirement mechanism (which skills truly used frequently)
- Agent workflow visualization (observability of current process)
- Cross-project knowledge sharing (currently requires manual user confirmation for user scope)

***

## 9. Trae IDE & Chinese Team Adaptation Points

### 9.1 Trae IDE Platform Feature Adaptation Summary

| Platform Feature                                       | Adaptation in This System                                                                              | Corresponding Component                                   |
| :----------------------------------------------------- | :----------------------------------------------------------------------------------------------------- | :-------------------------------------------------------- |
| **Rule Frontmatter**                                   | Four activation modes precisely control rule loading                                                   | All 8 rule files                                          |
| **SKILL.md Contract**                                  | Standardized SKILL.md template (name/description → Input → Execution → Failure → Output → Integration) | All 33 skills                                             |
| **`manage_core_memory`** **tool**                      | Knowledge / Rule / Experience categorized storage + capacity management                                | self-improvement skill                                    |
| **`Task`** **subagent**                                | Pre-flight → dispatch → four-state return                                                              | subagent-driven-development / dispatching-parallel-agents |
| **`Skill`** **tool**                                   | Agent auto-matches description to trigger skills                                                       | All skills                                                |
| **`RunCommand`** **/ PowerShell**                      | Windows native terminal execution, unified PowerShell syntax                                           | terminal-execution-stability rule                         |
| **`Read`** **/** **`Write`** **/** **`SearchReplace`** | IDE built-in file ops, superior to external scripts                                                    | All skills                                                |
| **`SearchCodebase`** **/** **`Grep`** **/** **`Glob`** | Codebase semantic search and file matching                                                             | systematic-debugging / general                            |
| **MCP tools**                                          | Graceful degradation: retry → terminal fallback → report limitation                                    | environment-resilience rule                               |
| **`WebSearch`** **/** **`WebFetch`**                   | Web info retrieval, Chinese search optimization                                                        | find-docs / general                                       |
| **`OpenPreview`**                                      | Dev server preview                                                                                     | visual-brainstorming                                      |
| **`GetDiagnostics`**                                   | Language error diagnostics                                                                             | verification-before-completion / general                  |

### 9.2 Windows Development Environment Adaptation

This system runs in Windows environment (Trae IDE for Windows), following adaptations贯穿 all components:

- **Unified PowerShell syntax**: All commands use PowerShell-compatible syntax (`Select-String` instead of `grep`, `Get-ChildItem` instead of `ls`, `Write-Output` instead of `echo`), Unix-only shell constructs prohibited
- **Port management**: `netstat -ano | Select-String` to check port usage, `taskkill /PID /F` to kill processes — encapsulated as `port-conflict-recovery` rule
- **Path standards**: Use backslashes and absolute paths, support Windows long paths (`\\?\` prefix), quote file paths in PowerShell to avoid space truncation
- **Filesystem**: `Get-ChildItem -Recurse` instead of `find`, `Select-String` instead of `grep -r`
- **Git adaptation**: `chinese-git-workflow` skill handles Git for Windows installation detection, SSH config paths (`%USERPROFILE%\.ssh\`) on Windows

### 9.3 Chinese Team Scenario Adaptation

This system makes the following specialized designs for Chinese development teams:

| Scenario                      | Adaptation Design                                                                                                                                                                 | Corresponding Component                              |
| :---------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------- |
| **Natural language triggers** | Skill description embeds Chinese trigger phrases ("帮我提交" "逐步排查" "按规范提交")                                                                                                          | All 33 skills                                        |
| **Commit message format**     | Hybrid Conventional Commit: `type` English + `scope/body` Chinese                                                                                                                 | git-commit skill                                     |
| **Domestic Git platforms**    | `finishing-a-development-branch` detects remote type via `git remote -v` and routes (GitHub CLI, others web UI); `chinese-git-workflow` provides config command library on-demand | finishing-a-development-branch, chinese-git-workflow |
| **Mixed Chinese/English**     | Docs written in Chinese, technical identifiers in English, auto-handle spaces and punctuation                                                                                     | chinese-copywriting skill, this doc                  |
| **Skill language layering**   | Machine-facing layer (frontmatter) English + human-facing layer (process description) Chinese                                                                                     | skill-language-policy                                |
| **Chinese user questions**    | `question-threshold` rule has Chinese trigger scenario descriptions, `AskUserQuestion` supports Chinese options                                                                   | question-threshold rule                              |
| **Workspace organization**    | `using-git-worktrees` skill has Windows path adaptation                                                                                                                           | using-git-worktrees skill                            |
| **Chrome browser automation** | `chrome-devtools` skill adapts element location under Chrome Chinese UI                                                                                                           | chrome-devtools skill                                |
| **Full Chinese interaction**  | Core skills like `brainstorming` / `verification-before-completion` / `writing-plans` / `executing-plans` output contracts and user interaction default to Chinese                | All user-facing skills                               |

### 9.4 Common Adaptation Pitfalls

**Pitfall 1: description exceeds 250 characters**

- Manifestation: Wrote detailed rule scenario description, but Agent never triggers
- Cause: Trae recommends description ≤ 250 characters, too long reduces matching precision
- Solution: Trim to ≤250 characters, put core trigger words at beginning

**Pitfall 2: Windows path backslashes not escaped**

- Manifestation: Wrote `globs: src\components\**\*.tsx` in YAML frontmatter, rule doesn't work
- Cause: Backslashes need escaping in YAML or use forward slashes
- Solution: globs uniformly use forward slashes (`src/components/**/*.tsx`)

**Pitfall 3: Chinese description truncated in skill description**

- Manifestation: Chinese trigger words display fine in IDE but Agent can't match
- Cause: Chinese characters take more bytes, actually counting may exceed 250
- Solution: description primarily in English, Chinese only as supplementary trigger phrases at end

**Pitfall 4:** **`alwaysApply: true`** **file bloat**

- Manifestation: Every conversation loading slows, Agent responses include unrelated rule content
- Cause: alwaysApply file exceeds 30 lines and carries multiple responsibilities
- Solution: Split into multiple independent rules, keep core logic as alwaysApply, demote sub-scenarios to conditional triggers

**Pitfall 5: Skill and Rule content duplication**

- Manifestation: Same process description appears in both rule and skill, need to sync both places when modifying
- Cause: Violated "rules make decisions, skills perform actions" principle
- Solution: rule only retains decision statements and pointer references, operation details in skill

***

## 10. Quick Reference

### Rule Files Inventory

| File                                | alwaysApply | Lines | Responsibility      |
| :---------------------------------- | :---------- | :---- | :------------------ |
| change-proposal-threshold.md        | ✅           | \~27  | Change self-check   |
| question-threshold.md               | ✅           | \~28  | Question boundaries |
| forced-escalation-guardrails.md     | ✅           | \~18  | Risk escalation     |
| terminal-execution-stability.md     | ✅           | \~13  | Terminal discipline |
| skill-routing-and-execution-path.md | ✅           | \~44+ | Core routing        |
| review-and-completion-gates.md      | ❌           | \~32  | Completion gates    |
| environment-resilience.md           | ❌           | \~20  | MCP degradation     |
| port-conflict-recovery.md           | ❌           | \~44  | Port recovery       |

### Skills Quick Reference

| Path       | Skill                          | Upstream Dependency            | Downstream                     | Alternative                              |
| :--------- | :----------------------------- | :----------------------------- | :----------------------------- | :--------------------------------------- |
| Design     | brainstorming                  | Fuzzy requirements             | writing-plans                  | Direct implementation (needs evaluation) |
| Design     | writing-plans                  | Stable design/spec             | executing-plans                | Direct ad-hoc coding                     |
| Execution  | executing-plans                | Execution plan                 | verification-xxx               | subagent-driven-dev                      |
| Execution  | subagent-driven-dev            | Execution plan                 | verification-xxx               | executing-plans                          |
| Debug      | systematic-debugging           | Abnormal symptoms              | verification-xxx               | Guessing fixes (not recommended)         |
| Quality    | test-driven-development        | Behavior change requirements   | verification-xxx               | Implementation without tests (high risk) |
| Quality    | verification-before-completion | Pending verification           | git-commit                     | Verbal claims (prohibited)               |
| Completion | git-commit                     | Verification passed            | finishing-a-development-branch | raw git (no standard)                    |
| Completion | finishing-a-development-branch | Implementation complete        | None                           | Not handling branch                      |
| Evolution  | self-improvement               | Errors/corrections/discoveries | Continue original flow         | Ignoring lessons (not recommended)       |

***

> *This document is generated based on source code and git commit history analysis of the project's* *`.trae/`* *directory. For detailed information on individual skills or rules, see corresponding source files directly.*
>
> ***
>
> - **Quick intro**: 15-second overview → [01-intro.md](./01-intro.md)
> - **Getting started**: Brief highlights → [02-overview.md](./02-overview.md)
> - **Component reference**: Each Rule/Skill one-line responsibility → [03-components.md](./03-components.md)
> - **Complete overview**: This document — architecture, workflows, pain points, adaptation guide

