---
name: memory-kernel
description: Manage and query persistent cross-session memory via MCP Knowledge Graph. Use when the task explicitly involves remembering, retrieving, or storing project knowledge, or when you need historical context about the project before starting a new task. Does NOT replace Trae Core Memory — complements it.
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

Before starting a task in a project you have worked on before, or when the user asks a question that suggests prior knowledge, query MCP Memory first:

- "你还记得吗" / "之前我们讨论过"
- Project architecture or conventions
- User preferences (tech stack, naming conventions, tools)
- Prior decisions or solutions
- User identity and context

Do NOT query MCP Memory for:
- Trivial facts visible in the current file tree
- Information the user just provided in this message
- Session-scoped temporary state

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

### Read Protocol

1. Start with `mcp_memory_search_nodes` with a broad query relevant to the task
2. If results are returned, open specific nodes with `mcp_memory_open_nodes`
3. If no relevant results found, proceed with normal task execution and consider writing the new context afterward

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

When using MCP Memory, include in your response:
- Whether you queried MCP Memory for context
- What relevant information was found (if any)
- What new information was persisted (if any)

## Integration

- `discovering-subagent-capabilities`: Adjacent — MCP Memory tools are platform-level, not subagent-level
- `self-improvement`: Downstream — persistent learnings from self-improvement should also be written to MCP Memory

## Failure Handling

- **MCP tools unavailable**: Fall back to Trae Core Memory only. Do not block task execution.
- **Search returns no results**: Proceed normally; treat this as a cold start.
- **Write fails**: Log the failed write and continue. The information can be re-captured later.
- **Duplicate entity**: The tools handle duplicates silently — no action needed.
