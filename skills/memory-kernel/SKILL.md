---
name: memory-kernel
description: Manage and query persistent cross-session memory via MCP Knowledge Graph. Step 0 executor: query before ANY task for project/pattern/user context. Use when the task involves remembering, retrieving, or storing project knowledge, or when you need historical context. Does NOT replace Trae Core Memory — complements it.
---

# Memory Kernel

## Overview

This skill governs the dual memory system:

| Layer | Backend | Scope | Lifetime |
|:------|:--------|:------|:---------|
| **Trae Core Memory** | Trae native | Current session | Ephemeral |
| **MCP Memory** | Knowledge Graph (JSONL) | Cross-session | Persistent |

MCP Memory is the authoritative cross-session store. When you start a new session or encounter a familiar topic, check MCP Memory before scanning the project from scratch.

## When To Read

Query MCP Memory before ANY task as the universal first step:

- **Step 0**: Before T-Shirt sizing, file scanning, or any routing decision, check MCP Memory for existing project/pattern/user context. If sufficient context exists, skip project-wide scanning — only read specific files to verify version/state changes.
- "你还记得吗" / "之前我们讨论过"
- Project architecture or conventions
- User preferences (tech stack, naming conventions, tools)
- Prior decisions or solutions
- User identity and context
- Cross-session context: starting a new session in a known project

Do NOT query MCP Memory for:
- Trivial facts visible in the current file tree
- Information the user just provided in this message
- Session-scoped temporary state
- When MCP tools are confirmed unavailable AND Core Memory is the fallback (use Core Memory instead; do not waste a failed call)

## When To Write

Persist to MCP Memory when any of these is true:

- **New project context learned**: tech stack, architecture decision, project convention
- **Problem-solution pair**: a bug was fixed or a configuration solved a recurring issue
- **User preference revealed**: naming style, tool preference, workflow habit
- **Cross-session boundary**: information you want future sessions to remember

Do NOT write for:
- One-time debugging steps
- Temporary variable names or file paths
- Information the user explicitly said not to remember

## Execution Protocol

### Write Protocol

1. Check if the entity already exists via `mcp_memory_search_nodes`
2. If entity exists: use `mcp_memory_add_observations` to append new facts
3. If entity does not exist: use `mcp_memory_create_entities` with name, type, and initial observations
4. For relationships between entities, use `mcp_memory_create_relations`

Entity naming convention: use `snake_case`.
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
   - Assess whether the context is sufficient:
     - **Sufficient**: Skip project-wide file scanning. Only read 1-2 key files (e.g., `package.json`) to verify version/state changes.
     - **Insufficient or empty**: Proceed with normal task execution. Write new findings back afterward.
   - If MCP call fails (timeout/error), fall back to Level 1.
3. **Level 1 (MCP unavailable, Core Memory available)**: Check if `manage_core_memory` tool is available. If yes, use Core Memory as context source. Note: Core Memory is a subset snapshot (20-entry cap per scope) — treat as a degraded context, not a replacement for MCP.)
4. **Level 2 (both unavailable)**: Skip all memory lookups. Choose fallback behavior based on task type — scanning is not the only option:

   | Task type | Fallback | Rationale |
   |:----------|:---------|:----------|
   | Single-file question, code explanation | Read current file(s) only | No project-wide context needed |
   | Project overview, "what is this project" | Ask user briefly or read `docs/` / `README.md` | Lighter than full scan |
   | Feature implementation, refactoring, bug fix | Full file scan + T-Shirt sizing | Task inherently needs project context |
   | Ambiguous request, "help me with..." | Ask user for context ("哪个模块/什么方向？") | Let user narrow scope, avoid blind scan |
   | Conversational, greeting, meta | Respond directly | No context needed at all |

   No memory write-back expected at Level 2.

### Update Protocol

When information in MCP Memory is found to be outdated:
1. Use `mcp_memory_delete_observations` to remove stale facts
2. Use `mcp_memory_add_observations` to add corrected facts
3. Do NOT delete and recreate the entity unless the entire entity is invalid

### Calibration Mode (Manual Trigger)

When the user says "校准记忆" or "同步记忆", perform a targeted refresh:

1. Read key project files: `package.json`, `rules/` directory listing, `skills/` directory listing, `docs/` directory listing
2. Read the current `trae_agent_enhancements` entity via `mcp_memory_open_nodes`
3. Compare observations against actual file state:
   - Missing skills or rules → append via `mcp_memory_add_observations`
   - Outdated version numbers or descriptions → `mcp_memory_delete_observations` + `mcp_memory_add_observations`
   - Renamed or removed items → `mcp_memory_delete_observations`
4. Report the diff to the user before writing: "发现 X 处差异，是否更新？（列出差异明细）"
5. Only write changes after user confirmation

## Output Contract

When using MCP Memory (including Step 0 pre-check), include in your response:
- Whether Step 0 MCP Memory query was performed
- Whether context was sufficient (skipping file scan) or insufficient (triggering fallback)
- What relevant information was found (if any)
- What new information was persisted (if any)

## Integration

- `discovering-subagent-capabilities`: Adjacent — MCP Memory tools are platform-level, not subagent-level
- `self-improvement`: Downstream — persistent learnings from self-improvement should also be written to MCP Memory

## Failure Handling

- **MCP tools unavailable (tool not registered)**: Pre-flight check catches this. Skip MCP entirely, attempt Level 1 or Level 2 (task-type-based fallback). Do not waste a call.
- **MCP tools unavailable (runtime failure)**: Fall back to Level 1 (Core Memory). If Core Memory also unavailable, Level 2 (task-type-based fallback). Do not block task execution.
- **Search returns no results**: Proceed with Level 0 insufficient path (normal execution). Write new findings back afterward.
- **Write fails**: Log the failed write and continue. The information can be re-captured later.
- **Duplicate entity**: The tools handle duplicates silently — no action needed.
- **Both Core Memory and MCP unavailable**: Level 2 — choose fallback based on task type (see Read Protocol table). Never hardcode "full scan" for all cases.
