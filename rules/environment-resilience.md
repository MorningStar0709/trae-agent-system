---
alwaysApply: false
description: Use when an MCP tool fails due to connection error, timeout, or server unavailability. Covers graceful MCP degradation with terminal fallback chain on Windows.
---

# Environment Resilience: MCP Graceful Degradation

When an MCP tool fails due to connection error, timeout, or server unavailability, follow this fallback chain. **Exception**: MCP Memory Server (`mcp_memory_*` tools) has its own dedicated degradation chain defined in `memory-kernel/SKILL.md` (Pre-flight → Level 0 MCP → Level 1 Core Memory → Level 2 skip memory). Do not apply this generic chain to memory tools — use the memory-kernel protocol instead.

1. **Retry once** — The failure may be transient.
2. **Fall back to native terminal** — Replace the MCP call with an equivalent PowerShell or CLI command:
   - File search: use `Get-ChildItem -Recurse`, `Select-String`, or `dir /s`
   - Web search: use `mcp_MiniMax_web_search` retry or ask user for alternative
   - Code search: use `Grep`, `Glob`, or `SearchCodebase` tools (IDE-native, not MCP-dependent)
3. **Report the limitation** — If no equivalent terminal command exists, state clearly which tool failed.

Do NOT:
- Silently skip the operation and pretend it succeeded.
- Keep retrying an MCP call more than twice.
- Abandon the task entirely without attempting a terminal fallback.
