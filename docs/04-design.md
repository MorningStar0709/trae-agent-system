# Design Philosophy and Highlights

> This document explains the core design philosophy, engineering trade-offs, and original mechanisms of this system. After reading, you should understand "why it was designed this way".
>
> Quick navigation: Quick intro → [01-intro.md](./01-intro.md) | Complete overview → [05-architecture.md](./05-architecture.md)

---

## 1. Design Manifesto: Three-Layer Separation

The core architectural decision of this system is the three-layer separation: **Rules make decisions, Skills perform actions, Trae native capabilities as the foundation**.

```
User Input
    │
    ▼
Rules Layer — Decides "which path to take"
    │  ║ Routing decisions (T-Shirt sizing → skill mapping)
    │  ║ Behavior constraints (question thresholds, escalation guardrails, change proposals)
    │  ║ Environment handling (terminal discipline, MCP degradation, port recovery)
    ▼
Skills Layer — Performs "how to do it"
    │  ║ Each skill focuses on a single responsibility
    │  ║ Upstream/downstream automatically assembled via Integration declarations
    │  ║ Design context refined and passed via Context Payload
    ▼
Trae Native (Foundation Layer) — Provides infrastructure
    │  ║ Rule Frontmatter controls loading
    │  ║ `Skill` tool matches description
    │  ║ `manage_core_memory` stores memory
    │  ║ `Task` subagent dispatch
    │  ║ IDE toolset (Read/Write/RunCommand...)
```

**Why separate this way?**
- A monolithic Agent does everything, but nothing well → Split into small skills, each focused
- Agent needs to know "what can be done" and "how to do it" are two different problems → Rules govern "what", skills govern "how"
- System will evolve, foundation will upgrade → This system only adds incremental value on top of native capabilities, does not replace or break them

---

## 2. Seven Design Highlights

### 2.1 Rule + Skill Dual-Wheel Collaboration, Upstream/Downstream Pipelined

**Core Idea**: Rules act like traffic police deciding "which path", Skills act like professional toolboxes handling "how". Each does its job without interfering.

**Pipeline Collaboration**: Skills are not isolated — each Skill's `Integration` field declares upstream and downstream, dynamically assembled by the Agent at runtime:

```
brainstorming → writing-plans → executing-plans → verification-before-completion → git-commit → finishing-a-development-branch → self-improvement
```

**Context Payload** is the "curated delivery package" between upstream and downstream — only passes Architecture / Key Interfaces / Conventions / Constraints / Uncertainties, not raw conversation logs. Downstream receives decision information, not chat history.

**Design Value**: Professionalism that a monolithic Agent can't achieve is realized through "small skill pipelines". Each skill focuses on a single responsibility, and together they cover the full workflow.

### 2.2 Deep Binding with Trae Native Capabilities, Complementary Without Conflict

**Core Idea**: Don't bypass or replace any Trae native mechanism, only add complementary enhancements on top.

| Trae Native | This System Enhancement | Relationship |
|:------------|:------------------------|:-------------|
| Core Memory (20-entry limit, auto-eviction) | `self-improvement` proactively manages memory quality | Complementary |
| `manage_core_memory` tool | Encapsulated as Knowledge/Rule/Experience three-tier | Enhanced |
| `Task` subagent | Pre-flight → dispatch → two-layer review complete loop | Enhanced |
| `Skill` auto-match | Bilingual description, 33 contract-based SKILL.md | Adapted |
| IDE toolset | Terminal discipline standards + MCP degradation | Standardized |
| Rule Frontmatter | 4 activation modes fully covered + quality standards | Compliant |

**Design Value**: Installing this system won't break any Trae native behavior. Native memory works normally, native rules load normally — this system is the second enhancement layer on top of native capabilities.

### 2.3 Follow Official Specs, Don't Invent Formats

**Core Idea**: Don't create custom configuration formats, write strictly according to Trae official specs. This means this system itself is a best practice example.

- Rule files: Standard YAML frontmatter + Markdown, 4 official activation modes
- SKILL.md: Strictly follows official recommended contract template
- Quality standards: description ≤ 250 characters, rules ≤ 50 lines, alwaysApply ≤ 30 lines — all from official docs
- Automated review: `skill-stability-review` built-in 16-dimension review script (review_skills.py, 888 lines), automatically checks each rule and skill compliance
- Three-tier meta-skill guarantee: `creating-trae-rules` guides rule writing, `skill-creator` guides Skill writing, `skill-language-policy` standardizes language

**Design Value**: 33 skills + 8 rules are themselves living textbooks on "how to create according to Trae specs". Users can directly reference when writing new rules.

### 2.4 Original Decision Mechanisms: T-Shirt Sizing + Question Thresholds

**Core Idea**: These two mechanisms are not in Trae native, derived from observing AI Agent daily usage pain points.

**T-Shirt 4-Dimension Matrix**:
```
File Scope × Change Type × Risk Level × Expected Pace → S / M / L
```
When dimensions conflict, the **largest T-Shirt size** prevails (not the "highest risk dimension"). When undecidable, default to the largest value for that dimension to ensure safety. Modules are defined by directory boundaries; test files count toward file count. Paired with Forced Escalation Guardrails (7 high-risk scenarios must not be treated as S) — Guardrails take precedence over Exception: score four dimensions first, then cross-check Guardrails, take the larger value. Supports dynamic reclassification during execution: upward reclassification (S→M, M→L) is mandatory when more complexity is found.

**Question Thresholds**: Five MUST Ask + Five MUST NOT Ask, precisely delineating "should ask users" vs "should not ask users". Trae's default behavior is "deduce and proceed", this system fills this gap.

**Design Value**: Completely original. Not following an official standard, but discovering problems through usage and deriving solutions independently.

### 2.5 agent-blueprint-architect: Stability Over Flashiness

**Core Idea**: Don't try to automate Agent creation, instead output Markdown blueprints that users can directly copy and paste.

**Lessons Learned**: Early attempts to write Python scripts that automatically write to Trae's encrypted SQLite database (`%APPDATA%\trae\ModularData\ai-agent\database.db`) revealed:
1. Database is IDE-exclusive locked, external writes cause crashes
2. Encryption format is opaque, reverse engineering is risky
3. Worked once then broke due to version updates

**Final Solution**: Abandon automation, switch to "blueprint delivery + manual paste":

```
Chinese display name → Copy to Trae UI's display name input
System Prompt → Copy to Trae UI's system prompt input
English identifier → Copy to Trae UI's identifier input
Trigger description → Copy to Trae UI's trigger condition input
Capability config → Guide users to check/uncheck switches in UI
```

**Design Value**: Honestly adapt to platform limits. The cost of users manually pasting is far lower than the risk of script crashes.

### 2.6 Highly Optimized Skill Internal Logic, Not One-Off Prompts

**Core Idea**: Each Skill is not a one-time prompt, but an "execution contract" that went through 3-5 rounds of iteration with git-traceable history.

Each SKILL.md contains five-layer structure:
- **Input Contract**: Precisely declares what input is needed
- **Output Contract**: Guarantees what format to output
- **Do Not Use**: Boundary declarations, prevents mis-trigger
- **Failure Handling**: Degradation paths for 5-8 failure scenarios
- **Integration**: Upstream/downstream declarations, forming DAG dependency graph

Additionally, there are **Red/Green Line Lists** — setting "red lines" (absolutely prohibited) and "green lines" (must execute). For example, `verification-before-completion`'s 6 red lines include "should be fine", "probably no bug", and other verbal commitment expressions.

**Design Value**: Each skill is ongoing engineering investment, not one-off output.

### 2.7 Chinese and Windows Layered Adaptation, Python for Portability

**Core Idea**: English is best for LLM reasoning (stability), but Chinese users need Chinese interaction. This system's solution is layered isolation, not one-size-fits-all.

**Layered Chinese/English Strategy**:

| Scenario | English | Chinese | Reason |
|:---------|:--------|:--------|:-------|
| Skill description | Core description (machine matching) | Trigger phrases (user expression) | Matching precision + natural entry |
| Conventional Commit | type field | scope + body | Tool compatibility + team communication |
| SKILL.md | frontmatter, code examples | Process description, failure handling | Machine stability + human readability |
| Agent reasoning | Internal reasoning chain | Final user interaction | Reasoning quality + interaction experience |

**Windows Adaptation**: All commands use PowerShell syntax, port conflict recovery encapsulated as independent rules, paths and file search written according to Windows conventions.

**Python Script Portable Architecture**: Platform-independent tool logic (review_skills.py, quick_validate.py) uniformly implemented in Python. Python is naturally cross-platform, `Path.resolve()` + `subprocess.run()` avoids Windows encoding and path pitfalls.

**Design Value**: For Chinese users, not just "[reply in Chinese]", but system's layered Chinese/English isolation. For Windows, not just "add a few PowerShell commands", but consistent execution experience guaranteed at the architectural level.

---

## 3. Lessons Learned (Failed Decisions)

> Records key failed attempts during design to prevent others from repeating mistakes.

### Automated Agent Creation (predecessor of agent-blueprint-architect)

**Attempt**: Write Python script to directly manipulate Trae's local `database.db`, automatically write Agent config.
**Failure reasons**: Database IDE-exclusive locked? Encryption format opaque? Version updates invalidate immediately?
**Final solution**: Blueprint delivery + manual paste.
**Lesson**: Don't automate around platform constraints. For capabilities platforms don't expose, manual is the most stable solution.

### Skill and Rule Content Overlap

**Attempt**: Same process description written in both rule and skill, "users can see it twice, doesn't matter".
**Problem**: Forget to update one place when modifying the other, content gradually becomes inconsistent.
**Correction**: Established "rules make decisions, skills perform actions" principle — rules only retain decision statements and pointer references, all operation details go to skills.
**Lesson**: Every redundant copy adds synchronization debt.

### alwaysApply Bloat

**Attempt**: Set port conflict recovery, MCP degradation, etc. as `alwaysApply: true`, "they're all commonly used anyway".
**Problem**: Every conversation loading slows down, Agent context filled with irrelevant content.
**Correction**: Demoted to conditional trigger (`alwaysApply: false` + `description`), only loaded in relevant scenarios.
**Lesson**: Every extra line in alwaysApply adds cost to every conversation. The 30-line limit is not formalism.

---

## 4. Core Design Principles (Cheat Sheet)

### Deduplication

```
Content already in Rule → Don't repeat in Skill
Content already in Skill → Rule only retains pointer references
Memory already has coverage → Check update first, don't create duplicates
```

### alwaysApply Simplification

- One alwaysApply rule carries only one independent concern
- If exceeding 30 lines, first judge: single concern (keep) or multiple concerns (split)
- Prohibiting deletion of actionable content to compress lines

### Routing rules decide who to point to, Skills decide if they can execute

- Rules make decisions, skills perform actions
- Environment prerequisites go in skill's Failure Handling
- Don't elevate skill's execution constraints to rules

---

> This document is an extracted standalone version of [05-architecture.md](./05-architecture.md) Chapter 7, with consistent content for convenient individual reference.
