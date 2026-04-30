---
name: memory-leak-debugging
description: Diagnose JavaScript, browser, and Node.js memory leaks in Trae with Chrome DevTools MCP and memlab-oriented workflows. Use when the user reports high memory usage, OOM errors, heap snapshots, detached DOM nodes, growing memory, or Chinese requests such as 内存泄漏, 内存占用高, 页面越用越卡, 分析 heapsnapshot, or 排查 Node 内存问题.
---

# Memory Leak Debugging

This skill provides expert guidance and workflows for finding, diagnosing, and fixing memory leaks in JavaScript and Node.js applications.

When the user writes in Chinese, report diagnosis, evidence, and fixes in Simplified Chinese. Keep object names, constructor names, heap snapshot paths, and tool names in English or original form.

## Trae and Windows Notes

- Use Chrome DevTools MCP for browser-side capture and interaction when available in Trae.
- Save large `.heapsnapshot` files to Windows absolute paths such as `C:\Users\skyler\Desktop\heap-baseline.heapsnapshot`.
- Do not paste or read raw heap snapshot contents into the conversation. Use `memlab` or the bundled comparison script.
- On Windows, use PowerShell-compatible commands and quote paths that contain spaces.

## Do Not Use

Do not use this skill when:

- The issue is ordinary slow rendering, LCP/Core Web Vitals, layout jank, or Network latency without evidence of growing memory.
- The user asks for general Chrome DevTools automation, accessibility testing, or page interaction verification.
- The problem is native application memory, database memory, or operating-system memory pressure outside JavaScript, browser, or Node.js contexts.
- There are no heap snapshots, reproducible leak steps, memory growth symptoms, or OOM errors to investigate.

## Core Principles

- **Prefer `memlab`:** Do NOT attempt to read raw `.heapsnapshot` files directly, as they are extremely large and will consume too many tokens. Always recommend and use `memlab` to process snapshots and identify leak traces.
- **Isolate the Leak:** Determine if the leak is in the browser (client-side) or Node.js (server-side).
- **Common Culprits:** Look for detached DOM nodes, unhandled closures, global variables, event listeners not being removed, and caches growing unbounded. _Note: Detached DOM nodes are sometimes intentional caches; always ask the user before nulling them._

## Workflows

### 1. Capturing Snapshots

When investigating a frontend web application memory leak, utilize the `chrome-devtools-mcp` tools to interact with the application and take snapshots.

- Use tools like `click`, `navigate_page`, `fill`, etc., to manipulate the page into the desired state.
- Revert the page back to the original state after interactions to see if memory is released.
- Repeat the same user interactions 10 times to amplify the leak.
- Use `take_memory_snapshot` to save `.heapsnapshot` files to disk at baseline, target (after actions), and final (after reverting actions) states. Prefer explicit Windows absolute output paths.

### 2. Using Memlab to Find Leaks (Recommended)

Once you have generated `.heapsnapshot` files using `take_memory_snapshot`, use `memlab` to automatically find memory leaks.

- Read [references/memlab.md](references/memlab.md) for how to use `memlab` to analyze the generated heapsnapshots.
- Do **not** read raw `.heapsnapshot` files using `read_file` or `cat`.

### 3. Identifying Common Leaks

When you have found a leak trace (e.g., via `memlab` output), you must identify the root cause in the code.

- Read [references/common-leaks.md](references/common-leaks.md) for examples of common memory leaks and how to fix them.

### 4. Fallback: Comparing Snapshots Manually

If `memlab` is not available, you MUST use the fallback script in the references directory to compare two `.heapsnapshot` files and identify the top growing objects and common leak types.

Run the script using Node.js:

```powershell
node "C:\Users\skyler\.trae\skills\memory-leak-debugging\references\compare_snapshots.js" "C:\path\baseline.heapsnapshot" "C:\path\target.heapsnapshot"
```

The script will analyze and output the top growing objects by size and highlight the 3 most common types of memory leaks (e.g., Detached DOM nodes, closures, Contexts) if they are present.

## Failure Handling

- Chrome DevTools MCP memory tools unavailable -> explain the missing capability and ask for existing snapshot paths or a way to enable memory tools.
- Snapshot path missing or inaccessible -> ask for a Windows-accessible path and do not analyze guessed locations.
- `memlab` unavailable -> use the bundled `compare_snapshots.js` fallback instead of reading raw snapshots.
- Comparison script fails -> report the command failure and paths used, then ask for valid snapshot files or tool installation details.
