---
name: agent-blueprint-architect
description: Use when the user needs to design, create, optimize, split, or name a reusable Trae agent configuration for a concrete task, including Chinese implicit requests such as "需要一个能做 X 的专门助手/agent/智能体", "现有 agent 职责太宽或能力不够", "这个功能是否应该独立成 agent", or "想把某个工作流固定成可复用 agent". Do not use for ordinary prompt writing, Trae Skill/SKILL.md creation or review, software architecture, tool selection, general agent discussion, or requests without intent to produce a reusable Trae agent configuration.
---

# Agent Blueprint Architect

## Overview

Use this Skill to generate a final, ready-to-fill and fine-tune configuration for a new Trae agent.

The core goal is not to design a complete multi-agent system, nor to create a Trae Skill, but to help users define a new agent with clear boundaries, stable naming, accurate triggers, and restrained capability switches.

Every output must cover:
- Chinese name
- System prompt
- English identifier
- When to trigger
- Capability switch configuration
- Brief configuration validation

Default to providing the final usable version directly. Do not give a rough draft first and wait for the user to ask "does it need more optimization". Unless key information that would change the agent's core positioning is missing, generate the configuration based on existing info, perform a round of optimization yourself, and deliver only the optimized final version.

Default to restrained output. Do not append internal reference tables, design rationale, generic capability matrices, or the Agent Blueprint Architect's own configuration to every result, unless explicitly requested by the user.

## Use This Skill

- The user wants to create a new agent.
- The user wants to name a new agent (English identifier or Chinese name).
- The user wants to write a system prompt for a new agent.
- The user wants to define trigger conditions for a new agent.
- The user wants to split a broad agent idea into a new agent with specific responsibilities.
- The user has a draft agent configuration and wants to optimize it before adding it to Trae.
- The user asks if a certain MCP is suitable for an independent agent.
- The user wants to know which capabilities should be enabled or disabled for a certain agent.

Implicit triggers are supported, but you must be able to infer the intent to precipitate a reusable Trae agent configuration.

## Do Not Use

- The user wants to create, modify, or review a Trae Skill or `SKILL.md`.
- The user just wants to write a normal prompt without intending to make a reusable agent.
- The user is doing software architecture, product architecture, organizational structure, or business process design.
- The user is generally discussing agent concepts without intending to create a specific agent.
- The user is just selecting tools for the current task, rather than creating a new agent configuration.
- The user wants the agent to assume the role of SOLO Coder's main orchestrator, unless explicitly asking to review the necessity of a main controller agent.
- Do not attempt to create, discover, or modify Trae agents by searching for local `agents/` or `custom_agents/` folders, reading workspace `.trae` files as if they were agent configs, or probing encrypted local databases.

If the request is ambiguous, ask first: "你是想把这个做成一个可复用的 Trae agent 配置吗？" Do not default to designing all prompts or workflows as agents.

## Execution Protocol

### 1. Information Gathering

Extract known information from the user's input first. Only ask questions when key direction is missing.

You must identify:
- The agent's core responsibility.
- The scenarios the agent serves.
- The agent's inputs and outputs.
- Adjacent tasks the agent should NOT handle.
- Whether a dedicated MCP or special capability is needed.
- Whether Chinese-first, English-first, or bilingual output is required.

Only ask questions first if:
- Core responsibilities are completely unclear.
- Multiple responsibilities conflict and cannot be merged into a single agent.
- The domain is unknown and cannot be inferred from context.

### 2. Chinese Scenario Strategy

Default to Chinese users and Chinese workflows:
- Explanations, boundaries, workflows, failure handling, and output specs default to Simplified Chinese.
- English is used only for English identifiers, necessary technical keywords, tool names, or parts explicitly requested in English.
- Do not mechanically mix Chinese and English; only keep necessary technical anchors (e.g., `DOM`, `Console`, `Network/XHR`, `MCP`, `API`, `CLI`, `E2E`).
- Do not write the entire system prompt in English and just append "answer in Chinese".
- Trigger descriptions are Chinese-first, supplemented with a few necessary English keywords to ensure natural Chinese requests hit accurately while avoiding false triggers from English keywords.

### 3. Platform Assumption Strategy

Default to designing agent configurations for Windows Trae users, but do not write all agents as command-execution agents.
- If the agent does not need a terminal, script, or local file path, do not force Windows/PowerShell rules into it.
- If the agent must run commands, read/write local files, call local tools, or save artifacts, the system prompt must specify Windows/Trae-friendly execution constraints.
- Command examples prioritize PowerShell; path examples prioritize Windows paths or `%userprofile%`.
- Do not assume the user environment has a Unix shell, macOS paths, Linux-only paths, or unconfirmed external CLIs.

### 4. Trae Agent Reality Check

- Trae custom agents are not managed through user-editable plaintext agent folders in `.trae/` or `%USERPROFILE%\.trae\`.
- Do not search for pseudo-config paths such as `agents/`, `custom_agents/`, or `agent.md` to discover or create Trae agents.
- Do not attempt to read or modify encrypted local databases, sandbox state files, or other reverse-engineered storage in order to create or inspect agents.
- The stable creation path is: generate the final blueprint, ask the user to copy it, and let the user paste it into the Trae UI manually.
- To discover existing subagents, use `discovering-subagent-capabilities` — it reads the `Task` tool's `subagent_type` enum from the system prompt. This covers all created custom agents.
- When designing a new agent, run `discovering-subagent-capabilities` first to identify potential overlap with existing subagents.

**Anti-Pattern: Automated Agent Creation via Scripts**

A previous attempt tried to automate Agent creation by writing a Python script, following this wrong path:

1. Search for local `agents/` folders or `.trae/` config files → Found **nothing**, because Trae does not use plaintext config folders for custom agents.
2. Probe deeper and discover the actual database at `%APPDATA%\trae\ModularData\ai-agent\database.db` — an **encrypted SQLite database**.
3. Realize that writing external scripts to inject data into `database.db` carries unacceptable risks:
   - **Data corruption**: Breaking the database integrity could destroy all existing agents.
   - **Lock conflicts**: Trae holds an exclusive lock on the database during runtime; external writes are intercepted or cause crashes.
4. Also find `sandbox` directory with runtime JSON state files — tightly coupled to IDE runtime, not suitable for direct manipulation.
5. **Result**: The script-based approach is abandoned. The only reliable path is **"blueprint delivery + manual paste"**.

**Key lesson**: Do not repeat this exploration. Do not write scripts to automate agent creation. Do not probe local databases. Do not generate agent config files and ask the user to place them in a filesystem path. The only correct final output is a Markdown blueprint that the user copies and pastes into the Trae UI.

## Design Rules

### English Identifier

- Use lowercase kebab-case.
- Contain only lowercase letters, numbers, and hyphens.
- Prefer 2 to 4 English words.
- Name by responsibility or domain.
- Avoid generic or versioned suffixes like `pro`, `expert`, `helper`, `v2`, unless explicitly requested.

### Chinese Name

- Use concise, professional, and easily recognizable Chinese names.
- The name must directly reflect the responsibility.
- Prefer 4 to 10 Chinese characters.
- Avoid over-promising words like "all-powerful", "ultimate", "strongest".

### When to Trigger

The trigger description determines when Trae selects this agent. It must be specific, not just a pile of keywords.

Must include:
- The core action the agent is responsible for.
- Natural Chinese expressions suitable for triggering.
- A few necessary English technical keywords.
- Adjacent scenarios that should NOT trigger it.

### System Prompt

The system prompt should make the agent capable of working, not just describe its personality.

Must include:
- Role: Exact responsibility of the agent.
- Scope: What it is suited to handle.
- Boundaries: What it is not suited to handle.
- Principles: Key judgment rules.
- Workflow: 4 to 7 specific steps.
- Tool Strategy: Described by capability, not hardcoding unconfirmed tool names.
- Output Spec: The structure of the final answer.
- Failure Handling: What to do when information is insufficient, out of scope, or capabilities are unavailable.
- If MCP is used, include MCP usage strategy and safety boundaries.

## Generation Flow

1. **Pre-check existing subagents**: Use `discovering-subagent-capabilities` to read current `Task` tool's `subagent_type` enum. For each existing subagent, compare its description against the new agent's intended capability. Classification:
   - **Exact match**: Recommend using the existing subagent. Do not create a duplicate.
   - **Partial overlap but different scope**: Document the differentiation boundary in the new agent's trigger and system prompt, so the two agents have clear separation.
   - **No overlap**: Proceed to step 2.
2. Extract requirements.
3. Judge form (should it be an agent, or a Skill/MCP/normal task).
4. Generate candidates.
5. Self-check and optimize.
6. Configure capabilities.
7. Compress boundaries.
8. Final delivery (output only the optimized final version and keep the creation workflow UI-manual rather than filesystem- or database-based).

## Capability Switch Rules

Output capability switch configurations for every new agent. Default to the most stable configuration: only enable capabilities strictly necessary for the core responsibility.

Fixed capability items:
| Capability | 默认状态 | 启用条件 |
|---|---:|---|
| Read | 开启 | 大多数 Agent 都需要读取输入、文件、日志或配置。 |
| Edit | 关闭 | 仅当核心职责包含创建或修改文件、代码或文档时开启。 |
| Terminal | 关闭 | 仅当该 Agent 必须运行命令、测试、构建、脚本或环境检查时开启。 |
| Preview/Browser | 关闭 | 仅当核心职责需要真实网页交互、UI 测试或 Chrome DevTools 时开启。 |
| Web Search | 关闭 | 仅当该 Agent 经常需要最新外部文档、论文或实时信息时开启。 |
| MCP | 按需 | 仅当某个 MCP 是该 Agent 完成核心职责的主要工具时才绑定。 |

## Output Contract

Always output the final version in this structure:

```markdown
## Agent Blueprint

**中文显示名:**
\```text
[Chinese Display Name]
\```

**System Prompt:**
\```markdown
# Role
...
# Scope
...
# Working Principles
...
# Workflow
...
# Tool Strategy
...
# Output Contract
...
# Failure Handling
...
\```

**英文标识:**
\```text
[kebab-case-id]
\```

**触发说明:**
\```text
[Trigger Description in Chinese]
\```

**能力配置:**
| Capability | 状态 | 原因 |
|---|---:|---|
| Read | [Enabled/Disabled] | ... |
| Edit | [Enabled/Disabled] | ... |
| Terminal | [Enabled/Disabled] | ... |
| Preview/Browser | [Enabled/Disabled] | ... |
| Web Search | [Enabled/Disabled] | ... |
| MCP / Specialized Capability | [Bound/Unbound] | ... |

**校验清单:**
- Trigger 边界: ...
- Capability 最小化: ...
- Overlap 风险: 与 `discovering-subagent-capabilities` 发现的现有子代理对比，确认职责边界已明确区分，不存在模糊地带
- 生成关闭: 明确告知用户通过 Trae UI 粘贴配置，不走文件系统或数据库路径
```

Only write 2 to 3 high-value conclusions in `Validation Checklist`. Avoid outputting long explanations, generic reference tables, or internal design rationale. Do not ask "does it need more optimization" unless there are pending issues that would change the agent's direction.

## Integration

- `discovering-subagent-capabilities`: Upstream — before designing a new agent, use this skill to discover existing subagents and check for overlap.
- `skill-creator`: Adjacent — agent-blueprint-architect creates Trae **agents**; skill-creator creates Trae **Skills** (SKILL.md). Ensure the user's intent matches the right output type.
