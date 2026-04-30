---
name: troubleshooting
description: Troubleshoot Chrome DevTools MCP connection, startup, target selection, navigation, and missing-tool issues in Trae on Windows. Use when Chrome DevTools MCP tools such as list_pages, new_page, navigate_page, take_snapshot, click, lighthouse_audit, or performance tools fail, or for Chinese requests such as MCP 启动失败, 浏览器连不上, 工具缺失, 页面打不开, or Chrome DevTools 报错.
---

# Chrome DevTools MCP Troubleshooting

Use this Skill only for Chrome DevTools MCP problems inside Trae. Keep the diagnosis concrete: identify the failed tool, the exact error, the current MCP configuration, and the smallest configuration or environment change likely to fix it.

## Do Not Use

Do not use this skill when:

- The failure is unrelated to Chrome DevTools MCP startup, connection, tools, target selection, navigation, or browser capabilities.
- The user is debugging application code, CSS, Network requests, accessibility, LCP, or memory behavior after Chrome DevTools MCP is already working.
- The user asks for general Trae IDE usage, package installation help, Git problems, or Context7 documentation lookup.
- The issue belongs to a non-Chrome-DevTools browser automation stack.
- No MCP error, missing tool, startup log, or browser connection symptom is present.
- **The MCP failure is generic (connection error, timeout, server unavailability) and NOT specific to Chrome DevTools tools**: use the `environment-resilience.md` rule instead for the MCP graceful degradation fallback chain.

## Workflow

### 1. Identify the Failure

Capture:

- The failed MCP tool, such as `list_pages`, `new_page`, `navigate_page`, `take_snapshot`, `click`, `lighthouse_audit`, or `performance_start_trace`.
- The exact error message or initialization log.
- Whether Chrome starts, attaches to an existing Chrome instance, or no browser appears.
- Whether the issue affects all tools or only interaction, performance, extension, or memory tools.

### 2. Read Trae MCP Configuration

Ask for or inspect the Trae MCP server JSON configuration. Look for:

- Incorrect arguments or flags.
- Missing environment variables.
- Usage of `--autoConnect` in incompatible environments.
- A browser profile path or Chrome executable path that does not exist.
- A disabled tool category, slim mode, or read-only capability setting.

If the configuration is not available, ask the user for the current Chrome DevTools MCP server JSON snippet.

### 3. Triage Common Errors

Match the error before suggesting changes.

#### Error: `Could not find DevToolsActivePort`

This usually means the MCP server cannot find or attach to a debuggable Chrome instance.

Check in order:

1. Confirm the intended Chrome version is running if the config attaches to an existing browser.
2. Confirm remote debugging is enabled when using an attach mode.
3. Prefer a fresh `list_pages` check after configuration changes.
4. If attach mode remains unstable, recommend launching Chrome through the MCP server or using an explicit browser URL with remote debugging.

#### Symptom: Server starts but creates a new empty profile

Check whether the configuration is launching a new managed Chrome profile instead of attaching to the user profile. This may be expected. If the user needs an existing session, adjust the attach mode or profile settings explicitly.

Also check for flag typos, stale paths, and incorrect argument casing.

#### Symptom: Missing tools or read-only behavior

If navigation, click, fill, emulation, trace, or extension tools are missing, check whether Trae is limiting tool categories or read/write tool access.

Explain the difference between read-only tools and state-changing browser tools. Recommend enabling the specific Chrome DevTools MCP capabilities needed for the task rather than broadly enabling unrelated MCP servers.

#### Symptom: Extension tools are missing or extensions fail to load

If the tools related to extensions (like `install_extension`) are not available, or if the extensions you load are not functioning:

1. Check whether extension-category tools are enabled in the MCP server configuration.
2. Prefer launching Chrome through the MCP server for extension testing.
3. Confirm the extension path is an unpacked extension directory.

#### Other common errors

Identify other error messages from the failed tool call or the MCP initialization logs:

- `Target closed`
- "Tool not found" (check if they are using `--slim` which only enables navigation and screenshot tools).
- `ProtocolError: Network.enable timed out` or `The socket connection was closed unexpectedly`
- `Error [ERR_MODULE_NOT_FOUND]: Cannot find module`
- Any sandboxing or host validation errors.

### 4. Check Current Documentation

If the issue is not obvious, consult current Chrome DevTools MCP documentation or the official troubleshooting page:

- https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/troubleshooting.md
- https://github.com/ChromeDevTools/chrome-devtools-mcp

Pay attention to version-specific flags, startup behavior, tool categories, attach modes, and platform limitations.

### 5. Propose a Minimal Fix

Give the smallest change that matches the evidence. Common fixes include:

- Correcting a misspelled or outdated flag.
- Switching from attach mode to MCP-launched Chrome, or from MCP-launched Chrome to an explicit browser URL.
- Enabling remote debugging when attaching to an existing browser.
- Adding a log file path for diagnosis.
- Increasing startup timeout on slow Windows systems.
- Enabling the needed Chrome DevTools MCP tool category.

### 6. Verify

After any change, verify in this order:

1. `list_pages`
2. `new_page` or `navigate_page`
3. `take_snapshot`
4. One task-specific tool, such as `click`, `list_console_messages`, `list_network_requests`, `lighthouse_audit`, `performance_start_trace`, or `take_memory_snapshot`

## Output Format

Respond in Simplified Chinese and include:

- 问题判断
- 证据
- 推荐修改
- 验证步骤
- 如果仍失败，下一步需要的日志或配置片段
