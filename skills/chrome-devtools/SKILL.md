---
name: chrome-devtools
description: Uses Chrome DevTools MCP in Trae for real browser automation, webpage debugging, Console/Network/DOM inspection, performance analysis, and UI flow verification. Use for Chinese or English requests such as 调用浏览器, 打开网页操作, 自动点击填写提交, 检查网页报错, 分析 Network 请求, 页面性能分析, or Chrome DevTools debugging. This skill does not apply to slim MCP mode.
---

## Core Concepts

**Browser lifecycle**: Browser starts automatically on first tool call using a persistent Chrome profile. Configure via CLI args in the MCP server configuration: `npx chrome-devtools-mcp@latest --help`. To enable extensions, use `--categoryExtensions`.
**Page selection**: Tools operate on the currently selected page. Use `list_pages` to see available pages, then `select_page` to switch context.

**Element interaction**: Use `take_snapshot` to get page structure with element `uid`s. Each element has a unique `uid` for interaction. If an element isn't found, take a fresh snapshot - the element may have been removed or the page changed.

## Trae and Windows Notes

- In Trae, prefer Chrome DevTools MCP tools over terminal browser automation.
- Keep tool names, API names, selectors, URLs, request paths, and file paths in their original form.
- On Windows, use absolute paths such as `C:\Users\skyler\Desktop\trace.json` when saving screenshots, snapshots, Lighthouse reports, or traces.
- When the user writes in Chinese, summarize results in Simplified Chinese unless they request another language.

## Do Not Use

Do not use this skill when:

- The task does not involve a real browser page, webpage state, extension, Console, Network, DOM, Performance, or UI flow.
- The user only asks for static code review, backend debugging, general product advice, or documentation lookup.
- Trae is running in slim MCP mode and the required Chrome DevTools tools are unavailable.
- The user explicitly asks for a non-Chrome-DevTools automation stack.
- A simpler local file or terminal inspection can answer the question without opening or controlling a browser.

## Workflow Patterns

### Before interacting with a page

1. Navigate: `navigate_page` or `new_page`
2. Wait: `wait_for` to ensure content is loaded if you know what you look for.
3. Snapshot: `take_snapshot` to understand page structure
4. Interact: Use element `uid`s from snapshot for `click`, `fill`, etc.

### Efficient data retrieval

- Use `filePath` parameter for large outputs (screenshots, snapshots, traces)
- Use pagination (`pageIdx`, `pageSize`) and filtering (`types`) to minimize data
- Set `includeSnapshot: false` on input actions unless you need updated page state

### Tool selection

- **Automation/interaction**: `take_snapshot` (text-based, faster, better for automation)
- **Visual inspection**: `take_screenshot` (when user needs to see visual state)
- **Additional details**: `evaluate_script` for data not in accessibility tree

### Parallel execution

You can send multiple tool calls in parallel, but maintain correct order: navigate → wait → snapshot → interact.

### Testing an extension

1. **Install**: Use `install_extension` with the path to the unpacked extension.
2. **Identify**: Get the extension ID from the response or by calling `list_extensions`.
3. **Trigger Action**: Use `trigger_extension_action` to open the popup or side panel if applicable.
4. **Verify Service Worker**: Use `evaluate_script` with `serviceWorkerId` to check extension state or trigger background actions.
5. **Verify Page Behavior**: Navigate to a page where the extension operates and use `take_snapshot` to check if content scripts injected elements or modified the page correctly.

## Troubleshooting

If `chrome-devtools-mcp` is insufficient, guide users to use Chrome DevTools UI:

- https://developer.chrome.com/docs/devtools
- https://developer.chrome.com/docs/devtools/ai-assistance

If there are errors launching `chrome-devtools-mcp` or Chrome, refer to https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/troubleshooting.md.
