---
name: memory-kernel
description: Manage and query persistent cross-session memory via MCP Knowledge Graph. Step 0 executor: query before ANY task for project/pattern/user context. Use when the task involves remembering, retrieving, or storing project knowledge, or when you need historical context, including Chinese requests such as “你还记得吗”“之前讨论过”“校准记忆”“同步记忆”. Does NOT replace Trae Core Memory — complements it.
---

# Memory Kernel

## Overview

This skill governs the dual memory system:

| Layer | Backend | Scope | Lifetime |
|:------|:--------|:------|:---------|
| **Trae Core Memory** | Trae native | Current session | Ephemeral |
| **MCP Memory** | Knowledge Graph (JSONL) | Cross-session | Persistent |

MCP Memory is the authoritative cross-session store. Check MCP Memory before scanning the project from scratch.

## Use This Skill

- "你还记得吗" / "之前我们讨论过" / 跨会话记忆召回
- "校准记忆" / "同步记忆"（触发 Calibration Mode）
- 新会话，需要项目上下文再开始
- 已知项目，需要查架构/约定/用户偏好
- 任务中需要持久化新知识到跨会话记忆

## Do Not Use

- 当前文件树可见的琐碎事实
- 用户刚在当前消息中提供的信息
- 会话级别的临时状态
- MCP 工具确认不可用且 Core Memory 可用时（直接用 Core Memory，不浪费调用）
- 一次性调试步骤
- 临时变量名或文件路径
- 用户明确说不要记住的信息

## Input Contract

**Required Inputs:**
- 用户的自然语言查询或任务指令（Step 0 自动触发）
- 或用户显式说出"校准记忆" / "同步记忆"
- 或用户显式说出"你还记得吗" / "之前我们讨论过"

**Optional Inputs:**
- 实体命名约定（默认 `snake_case`，项目实体无前缀，公共实体加 `public_` 前缀）
- 实体类型约定：`project` / `pattern` / `preference` / `profile`

**Missing input handling:**
- **查询太泛**：先缩小搜索范围再重试
- **未指定项目上下文**：从当前 git remote 或目录名推断
- **MCP 工具不可用**：按三级降级链处理，不阻塞

## When To Read

Query MCP Memory before ANY task as the universal first step:

- **Step 0**: Before T-Shirt sizing, file scanning, or any routing decision, check MCP Memory for existing project/pattern/user context. If sufficient context exists, skip project-wide scanning — only read specific files to verify version/state changes.
- Project architecture or conventions
- User preferences (tech stack, naming conventions, tools)
- Prior decisions or solutions
- User identity and context
- Cross-session context: starting a new session in a known project

## Execution Protocol

### Writing Standard

Every observation written to MCP Memory must pass these gates.

**Observation format:** `[YYYY-MM-DD] <content>`
- Timestamp is the date the observation was written or last verified.
- Content is a single, self-contained fact. One sentence per observation.

**Write-worthy (pass the gate):**
- Project architecture, tech stack, key design decisions
- Conventions (naming, patterns, workflows) that affect multiple files
- User preferences that persist across sessions
- Reusable solutions, recurring error patterns, root causes
- Entity relationships that structure the knowledge graph

**Not write-worthy (skip):**
- Current file tree structure (always re-scanable)
- Information the user just provided in the current message
- Session-only state (variable names, temp file paths)
- Trivial or self-evident facts ("this project uses Git")
- Secrets, tokens, passwords, API keys — NEVER

**Entity granularity:**
- One project entity per project. Add observations to it, do not create multiple project entities.
- One pattern entity per distinct solution. Merge related patterns — do not split a single concept across entities.
- One preference entity per user profile.
- Prefer growing existing entities over creating new ones.

**Update discipline:**
- Stale observation: `delete_observations` the old one, `add_observations` the corrected one (both with current timestamp).
- Entity relationship stale: `delete_relations` then `create_relations`.
- Entire entity invalid: only then `delete_entities`.

### Write Protocol

1. Check if the entity already exists via `mcp_memory_search_nodes`
2. If entity exists: use `mcp_memory_add_observations` to append new facts
3. If entity does not exist: use `mcp_memory_create_entities` with name, type, and initial observations
4. For relationships between entities, use `mcp_memory_create_relations`
5. Every observation must include a `[YYYY-MM-DD]` prefix. Same date for bulk updates.

Entity naming convention: use `snake_case`. Timestamps are in observations, not in entity names.
- **Project entities**: no prefix — named as the project name (e.g., `trae_agent_enhancements`)
- **Public entities**: prefix `public_` — reusable across projects (e.g., `public_chenxing`, `public_architecture_patterns`)

Entity type convention:
- `project` for project-level entities (tech stack, architecture, conventions) — project memory
- `pattern` for reusable solutions and decisions — public memory
- `preference` for user preferences — public memory
- `profile` for user identity — public memory

### Read Protocol (Step 0 Execution)

1. **Pre-flight check**: Verify whether `mcp_memory_search_nodes` is in the available tool list. If the tool is not registered, skip to Fallback Level 2 immediately — do not attempt the call.
2. **Level 0 (MCP available)**: Start with `mcp_memory_search_nodes` — use broad queries relevant to the task/project context. Search for project name, domain keywords, entity types (`project`, `pattern`, `profile`, `preference`).
   - If results are returned, open specific nodes with `mcp_memory_open_nodes` to get full observations
   - Assess whether the context is sufficient by checking both criteria:

     | Check | Question | Sufficient if... |
     |:------|:---------|:-----------------|
     | **Answer check** | Can the user's question be answered from MCP observations alone? | Yes |
     | **Task check** | Does MCP data provide enough project structure/convention/pattern context to proceed without project-wide discovery? | Yes |

     - **Both checks negative or empty**: Insufficient — proceed with normal task execution. Write new findings back afterward.
     - **At least one check positive**: Sufficient — skip project-wide file scanning. Only read 1-2 key files (e.g., `package.json`) to verify version/state changes.
   - If MCP call fails (timeout/error), fall back to Level 1.
3. **Level 1 (MCP unavailable, Core Memory available)**: Check if `manage_core_memory` tool is available. If yes, use Core Memory as a degraded context source.
4. **Level 2 (both unavailable)**: Skip all memory lookups. Choose fallback behavior based on task type:

   | Task type | Fallback |
   |:----------|:---------|
   | Single-file question, code explanation | Read current file(s) only |
   | Project overview, "what is this project" | Ask user briefly or read `docs/` / `README.md` |
   | Feature implementation, refactoring, bug fix | Full file scan + T-Shirt sizing |
   | Ambiguous request, "help me with..." | Ask user for context |
   | Conversational, greeting, meta | Respond directly |

   No memory write-back expected at Level 2.

### Update Protocol

When information in MCP Memory is found to be outdated:
1. Use `mcp_memory_delete_observations` to remove stale facts (identified by their timestamp prefix `[YYYY-MM-DD]`)
2. Use `mcp_memory_add_observations` to add corrected facts with the current date `[YYYY-MM-DD]`
3. Do NOT delete and recreate the entity unless the entire entity is invalid

### Calibration Mode (Manual Trigger)

When the user says "校准记忆" or "同步记忆", perform a targeted refresh:

1. Read key project files: `package.json`, `rules/` directory listing, `skills/` directory listing, `docs/` directory listing
2. Read the current project entity via `mcp_memory_open_nodes`
3. If entity does not exist (search returned empty):
   - Summarize what was found: project name from `package.json`, skill count, rule count, docs count
   - Ask user: "项目记忆为空，是否基于当前文件状态初始化？"
   - If confirmed: use `mcp_memory_create_entities` to create the project entity with initial observations from step 1
   - Then proceed to step 4 to confirm the diff
4. Compare observations (check timestamp prefix `[YYYY-MM-DD]` for staleness) against actual file state (or against the just-created entity):
   - Missing skills or rules → append via `mcp_memory_add_observations`
   - Outdated version numbers or descriptions → `mcp_memory_delete_observations` + `mcp_memory_add_observations`
   - Renamed or removed items → `mcp_memory_delete_observations`
5. Report the diff to the user before writing: "发现 X 处差异，是否更新？（列出差异明细）"
6. Only write changes after user confirmation

## Failure Handling

- **MCP tools unavailable (tool not registered)**: Pre-flight check catches this. Skip MCP entirely, attempt Level 1 or Level 2 (task-type-based fallback). Do not waste a call.
- **MCP tools unavailable (runtime failure)**: Fall back to Level 1 (Core Memory). If Core Memory also unavailable, Level 2 (task-type-based fallback). Do not block task execution.
- **Search returns no results**: Proceed with Level 0 insufficient path (normal execution). Write new findings back afterward.
- **Write fails**: Log the failed write and continue. The information can be re-captured later.
- **Duplicate entity**: The tools handle duplicates silently — no action needed.
- **Both Core Memory and MCP unavailable**: Level 2 — choose fallback based on task type (see Read Protocol table).

## Output Contract

When using MCP Memory (including Step 0 pre-check), include in your response:
- Whether Step 0 MCP Memory query was performed
- Whether context was sufficient (skipping file scan) or insufficient (triggering fallback)
- What relevant information was found (if any)
- What new information was persisted (if any)

## Integration

- `discovering-subagent-capabilities`: Adjacent — MCP Memory tools are platform-level, not subagent-level
- `self-improvement`: Downstream — persistent learnings from self-improvement should also be written to MCP Memory
