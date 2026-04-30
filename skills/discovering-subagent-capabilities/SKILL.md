---
name: discovering-subagent-capabilities
description: Use this skill to discover available subagents and their capabilities by reading the system prompt's Task tool definition. Use when the user asks what agents are available, what a specific agent can do, how to find the right agent for a task, whether there is an agent for X, or how to understand agent capabilities, including Chinese requests such as “有哪些子代理可用”“这个 agent 能做什么”“怎么选择合适的 agent”. Do not use for Custom Agent discovery (encrypted database, no read access).
---

## Language Strategy

When the user writes in Chinese, report discovery results and summaries in Simplified Chinese. Keep subagent names, tool names (`Task`, `subagent_type`), file paths, database paths, and code identifiers in English or their original form.

## Purpose

This Skill tells you how to discover which subagents are available and what each one does. The information is **not** from memory or exploration — it is encoded in the system prompt itself.

## How It Works

Your system prompt contains tool definitions, including the **`Task` tool**. The `Task` tool has a parameter called `subagent_type` of type `string`. This parameter defines an **enum** of all available subagents. Each enum value has a `description` that explains:

1. The subagent's **core capability**
2. **When to use** it — typical triggering scenarios
3. **When not to use** it — boundary cases and exclusion rules
4. **Tools it has access to** — what it can do internally

## Execution Steps

### Step 1: Identify the Request Type

| If user asks about | Action |
|---|---|
| Available subagents (general) | Go to Step 2 |
| A specific subagent's capability | Go to Step 2, filter by name |
| Custom Agents created in UI | Report: "Cannot discover — Custom Agents are stored in an encrypted database with no tool-based read access. Use the Trae IDE UI to view them manually." |
| Which agent to use for task X | Go to Step 2, then match descriptions to the task |

### Step 2: Read the Task Tool Definition

In your system prompt, locate the `Task` tool definition. Focus on the `subagent_type` parameter's `enum` values. Each enum value has this structure:

```
"enum": ["name1", "name2", ...]
```

Each subagent name is accompanied by its `description` field inline in the parameter definition. Read all descriptions.

### Step 3: Extract Subagent Information

For each subagent found in the enum, extract:

- **Name**: the string identifier (e.g. `search` for the built-in generic agent)
- **Description**: the inline `description` text from the enum value definition
- **Capability summary**: derived from the description — what it's good at
- **Boundary summary**: derived from the description — what it should not be used for

### Task Tool Parameter Reference

The `Task` tool's complete parameter signature:
- `description` (string, required): 3-5 character label for the sub-task
- `query` (string, required): Detailed instruction for the subagent. Official recommendation ≤30 words, but can be longer for complex tasks
- `subagent_type` (string, required): Which subagent to use — read from enum
- `response_language` (string, required): Return language (e.g., "zh-CN", "en")

All 4 parameters are required. Concurrent dispatch is achieved by sending multiple `Task` calls in a single message — there is no dedicated `parallel` parameter.

### Dynamic Subagent Discovery (Not a Hardcoded Catalog)

**The subagent list is NOT fixed.** Only `search` is built-in; all other subagents are custom agents created by the user through Trae IDE UI. They can be added, removed, or renamed at any time.

This means: **never hardcode subagent names in skills, rules, or queries.** Always discover them dynamically by reading the `subagent_type` enum from the system prompt at runtime.

**Discovery pattern for any skill that needs to dispatch a subagent:**

```
1. Read the Task tool's subagent_type enum from the system prompt
2. For each enum value, read its inline description
3. Match the description against the task's requirements:
   - Which subagent's description best fits the work needed?
   - Does the description include the tools or capabilities required?
4. Use the matched subagent_type value in the Task call
```

This approach works regardless of how many subagents exist or what they are named. The only assumption is that subagent descriptions are accurate — which they should be since the user created them.

### Step 4: Respond to the User

**For general inquiry ("what agents are available?"):**

Report the list with each subagent's name and a one-line capability summary derived from its description.

**For specific inquiry ("what can agent X do?"):**

Report that subagent's full description and boundary information.

**For task-matching ("which agent for task X?"):**

Compare the task requirements against each subagent's description. Recommend the best match. If none match well, state that clearly and describe what the task requires so the user can consider other options.

## Key Distinction

| Can discover | Cannot discover |
|---|---|
| Subagents listed in the `Task` tool's `subagent_type` enum | Custom Agents created via Trae IDE UI |
| Information source: system prompt tool definitions | Stored in encrypted local database — no tool can read them |
| Method: read the enum descriptions | Method: user must view manually in Trae IDE Agent panel |

**Anti-Pattern: Probing the Local Database**

A previous attempt tried to discover custom agents by probing the local filesystem, following this wrong path:

1. Search for `agents/` folders or `.trae/` config files → Found nothing (Trae does not use plaintext config folders for custom agents).
2. Find the actual database at `%APPDATA%\trae\ModularData\ai-agent\database.db` → It is an **encrypted SQLite database** with no tool-based read access.
3. Also discover `sandbox/` runtime JSON files → These are tightly coupled to IDE runtime state, not agent configurations.
4. **Result**: All paths lead to a dead end. The only way to view custom agents is through the Trae IDE UI.

**Key lesson**: Do not repeat this exploration. Do not search for local files, probe databases, or attempt to reverse-engineer the storage layer. The `Task` tool's `subagent_type` enum is the only reliable source for discovering subagents. Custom Agents must be viewed in the Trae IDE Agent panel manually.

## Failure Handling

- **No subagent matches the user's task**: clearly state that no built-in subagent fits, describe what capabilities the task needs, and suggest the user create a Custom Agent or use a Skill-based workflow.
- **User asks about subagents but the context also mentions Custom Agents**: first answer the subagent part from system prompt data, then explain that Custom Agents cannot be discovered via tools and need manual UI inspection.
- **User asks for subagent capabilities but the Task tool definition is not visible in the current context**: report that the information is embedded in the system prompt tool definitions and cannot be re-queried mid-session, then provide a general explanation based on memory of the last available definition.
- **User asks to "find agent config files" or "read agent database"**: stop and explain that Trae does not use plaintext config files, and its local database at `%APPDATA%\trae\ModularData\ai-agent\database.db` is encrypted with no tool-based read access. The only valid discovery method is reading the `Task` tool's `subagent_type` enum (for subagents) or the Trae IDE Agent panel UI (for all custom agents). Do not attempt to probe, read, or reverse-engineer the database.

## Integration

- `dispatching-parallel-agents`: Downstream — after discovering what subagents are available, dispatch parallel analysis/review tasks using this skill.
- `subagent-driven-development`: Downstream — after discovering what implementation subagents are available, dispatch sequential implementation tasks using this skill.
- `skill-routing-and-execution-path.md`: Adjacent — the routing rule's Subagent Dispatch Decision Table determines when to dispatch; this skill determines which subagents exist to dispatch.
