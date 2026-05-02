# Memory System — Dual-Track Persistent Memory

## Overview

This project implements a **dual-track memory system** that combines Trae's native Core Memory with a persistent Knowledge Graph via MCP Memory Server.

The system works as follows:

The routing rule defines **Step 0 (Memory-first inquiry)** as the universal entry gate for all tasks: query **MCP Memory** (authoritative source, knowledge graph) first for project/pattern/user context. Only fall back to full file scanning if memory is insufficient. Core Memory (Trae native, session-level cache) serves as a degraded fallback when MCP is unavailable.

Writes go to both tracks: Core Memory handles automatic session-level writes, while MCP Memory is explicitly written to via the `memory-kernel` skill for information that should survive across sessions.

| Aspect | Core Memory | MCP Memory |
|:-------|:------------|:-----------|
| **Backend** | Trae native | `@modelcontextprotocol/server-memory` |
| **Storage** | Managed by Trae | Local JSONL file |
| **Scope** | Current session | Cross-session |
| **Lifetime** | Ephemeral (ends with session) | Persistent (until deleted) |
| **Structure** | Key-value observations | Knowledge graph (entities + relations) |
| **Write trigger** | Automatic (Trae native) | Explicit via `memory-kernel` skill |
| **Capacity** | ~20 entries per scope | Unlimited |
| **Platform lock** | Trae-only | Any MCP-compatible IDE |

## Architecture

### Rule Layer

The `skill-routing-and-execution-path.md` rule defines **Step 0 (Memory-first inquiry)** as the universal entry gate for all tasks:

| Order | Action | Role |
|:------|:-------|:-----|
| **Step 0** | Auto-query MCP Memory (authoritative source) | Retrieve project/pattern/user context before any file scan or routing decision |
| Step 1+ | T-Shirt sizing → route to skill | Normal routing flow |

Additionally, these specific scenarios also route to the memory system:

| If the task is... | Route to | Instead of |
|:------------------|:---------|:-----------|
| New session, need project context before starting | `memory-kernel` | scanning the entire project from scratch |
| "还记得吗", cross-session memory recall | `memory-kernel` | guessing from current context |

### Skill Layer

| Skill | Role | Key Behaviors |
|:------|:-----|:--------------|
| [`memory-kernel`](../skills/memory-kernel/SKILL.md) | Memory execution | Read/write/update protocol for MCP Memory |
| [`self-improvement`](../skills/self-improvement/SKILL.md) | Learning promotion | Elevates session learnings to permanent rules or memory |

### Tool Layer (MCP)

The following tools are provided by the MCP Memory Server:

| Tool | Purpose |
|:-----|:--------|
| `mcp_memory_create_entities` | Create entities with name, type, and observations |
| `mcp_memory_create_relations` | Create directed relations between entities |
| `mcp_memory_add_observations` | Append observations to existing entities |
| `mcp_memory_delete_entities` | Remove entities and their relations |
| `mcp_memory_delete_observations` | Remove specific observations |
| `mcp_memory_delete_relations` | Remove specific relations |
| `mcp_memory_read_graph` | Read the entire knowledge graph |
| `mcp_memory_search_nodes` | Search entities by query |
| `mcp_memory_open_nodes` | Retrieve specific nodes by name |

## Usage

### Write Protocol

Only persist information that is cross-session useful:

1. **Search** existing entities via `mcp_memory_search_nodes`
2. **Create** new entity if it doesn't exist (via `mcp_memory_create_entities`)
3. **Append** observations to existing entities (via `mcp_memory_add_observations`)
4. **Relate** entities when a meaningful connection exists (via `mcp_memory_create_relations`)

**Entity naming**: `snake_case`, prefix with project name for project-specific entities.

**Entity types**:

| Type | Example |
|:-----|:--------|
| `project` | `trae_agent_enhancements` — tech stack, architecture, conventions |
| `pattern` | `known_solutions` — reusable solutions and decisions |
| `preference` | User preferences (naming style, tool preference) |
| `profile` | User identity (name, background, interests) |

### Read Protocol

As part of the **Step 0 universal pre-check**, execute at the start of ANY task (not just "known projects"):

1. Query via `mcp_memory_search_nodes` with broad keywords (project name, domain keywords, entity types)
2. Open matching nodes via `mcp_memory_open_nodes` for full observations
3. Assess whether context is sufficient:
   - **Sufficient**: Skip project-wide file scanning. Only read 1-2 key files to verify version/state changes.
   - **Insufficient or empty**: Proceed with normal task execution (which triggers T-Shirt sizing and file scanning). Write new findings back afterward.
4. If MCP tools are unavailable, fall back silently — do not block execution.

### Update Protocol

When information in memory is found to be outdated:

1. Remove stale observations via `mcp_memory_delete_observations`
2. Add corrected observations via `mcp_memory_add_observations`
3. Do NOT delete and recreate entities unless the entire node is invalid

## Initial Setup

### 1. Configure MCP Server

Add to Trae Settings → MCP Servers:

```json
{
  "mcpServers": {
    "memory": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "D:/AppData/Memory/memory.jsonl"
      }
    }
  }
}
```

### 2. Seed the Knowledge Graph

The `memory-kernel` skill supports initial seeding. The recommended seed entities for any project:

- **Project entity**: name, description, tech stack, architecture, conventions
- **Profile entity**: user identity and preferences
- **Pattern entities**: reusable solutions and architectural decisions
- **Known solutions entity**: recurring problem-solution pairs

### 3. Verify

Open a new session and ask a project-related question. The system should retrieve context from MCP Memory instead of scanning the entire project from scratch.

## Conflict Resolution & Degradation

| Scenario | Resolution |
|:---------|:-----------|
| Same info in both tracks | Allowed — Core Memory is session cache, MCP Memory is authoritative |
| Conflicting info | Trust MCP Memory (it is actively maintained) |
| Outdated info in MCP | Update immediately via delete_observations + add_observations |
| **MCP tools not registered** | Pre-flight check catches this; skip directly to Level 2 (no call wasted) |
| **MCP unavailable (runtime failure)** | Degrade to Level 1 (Core Memory); if Core Memory also unavailable, Level 2 |
| **Both unavailable** | Level 2: Choose the lightest fallback path by task type — single-file task reads current file only, overview reads docs/, implementation does full scan, ambiguous asks user, conversational responds directly. Never hardcode "full scan" for all cases. |

## Integration

- **`memory-kernel`**: Main execution skill for reading/writing MCP Memory
- **`self-improvement`**: Persistent learnings should also be written to MCP Memory
- **`discovering-subagent-capabilities`**: Adjacent — memory tools are platform-level, not subagent-level

## Relation to Existing Patterns

The dual-track memory system extends the existing Memory-Intent-Trigger architecture:

| Pattern | How It Works Now |
|:--------|:-----------------|
| Memory | Stored in both Core Memory (fast access) and MCP Memory (persistent graph) |
| Intent | Resolved via `memory-kernel` read protocol — query memory before inferring |
| Trigger | Routed through `skill-routing-and-execution-path.md` — new rows for memory operations |
