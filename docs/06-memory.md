# Memory System — Dual-Track Persistent Memory

## Overview

This project implements a **dual-track memory system** that combines Trae's native Core Memory with a persistent Knowledge Graph via MCP Memory Server.

The system works as follows:

When the user or agent triggers a query, **Core Memory** (Trae native, session-level cache) is checked first for fast access. If the needed context is not found there, or if cross-session recall is required, the request falls through to **MCP Memory** (knowledge graph, persistent store). Writes go to both tracks: Core Memory handles automatic session-level writes, while MCP Memory is explicitly written to via the `memory-kernel` skill for information that should survive across sessions.

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

The `skill-routing-and-execution-path.md` rule controls when to route to the memory system:

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

Before starting a task in a known project, or when asked about prior context:

1. Query via `mcp_memory_search_nodes` with a broad keyword relevant to the task
2. Open matching nodes via `mcp_memory_open_nodes`
3. If no relevant results, proceed normally and consider writing context afterward

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

## Conflict Resolution

| Conflict Scenario | Resolution |
|:------------------|:-----------|
| Same info in both tracks | Allowed — Core Memory is session cache, MCP Memory is authoritative |
| Conflicting info | Trust MCP Memory (it is actively maintained) |
| Outdated info in MCP | Update immediately via delete_observations + add_observations |
| MCP unavailable | Fall back to Core Memory only; do not block execution |

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
