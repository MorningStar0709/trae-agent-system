---
name: visual-brainstorming
description: Provide a browser-based prototyping companion for brainstorming sessions — show layouts, wireframes, architecture diagrams, and visual options, and collect the user's click choices. Use when the user has accepted the visual companion offer during brainstorming, or when you need to display visual content for user feedback, including Chinese requests such as “在浏览器里看原型”“展示布局对比”“让用户点击选择”. Requires node available and a local port accessible. Do not use for pure text discussions, concept clarification, or decisions that don't benefit from visual presentation.
---

# Visual Brainstorming

A browser-based companion for `brainstorming` that lets users see prototypes, layouts, and visual options in the browser and click to choose. This is an **optional enhancement** — only use when the environment supports a local server process and the user has agreed to try it.

When the user writes in Chinese, interact in Simplified Chinese. Keep tool names, script names, JSON keys, file paths, and technical identifiers in English.

## Use This Skill

- The user has accepted the visual companion offer during a brainstorming session.
- You need to show layouts, wireframes, comparison options, architecture diagrams, or other visual content.
- The current environment supports local services (node available, ports accessible, process can stay alive).
- The question is visual: "which layout looks better?" not conceptual: "what does X mean?"

## Do Not Use

- The user declined the visual companion offer or the topic is purely text-based.
- node is not available, local ports are blocked, or the environment cannot keep a background process alive.
- The task is concept clarification, technical decision-making, or requirements gathering — use `brainstorming` in text mode instead.
- The user only wants a single static chart or diagram — use `chart-visualization` instead.
- The user just wants an answer without interactive prototyping.

## Prior Conditions

Before using this skill, the user must have already agreed to try the browser companion. The agreement is obtained by `brainstorming`'s Visual Companion section, which sends a standalone offer message. Do not re-offer if the user already declined.

## Workflow

### 1. Start the Server

```powershell
python .\scripts\start-server.py --project-dir "C:\path\to\project"
```

The script returns a JSON response with `port`, `url`, and `screen_dir`. Save `screen_dir` — you need it for all subsequent file writes.

If the server is already running from a previous session, check `<screen_dir>/.server-info` for the current connection details instead of starting a new one.

**Dependency check:** `start-server.py` launches `scripts/server.cjs` via node. If node is missing or the port is blocked, report the failure and fallback to text-only brainstorming.

### 2. Write Content to Screen

Write HTML content fragments to files in `screen_dir`. Each file is one "screen" — one question or comparison.

**Content fragment vs full document:** If your HTML starts with `<!DOCTYPE` or `<html>`, the server serves it as-is (only injecting the interaction script). Otherwise, the server wraps your content in the frame template (CSS theme, choice indicators, all interaction infrastructure). **Default to writing fragments.** Write a full document only when you need complete control over the page.

**Naming:** Use semantic names: `platform.html`, `visual-style.html`, `layout.html`. **Never reuse a filename** — each screen needs a new file. Version with suffixes: `layout-v2.html`.

**Interaction classes available via the frame template:**

Options (single/multi-select):
```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content"><h3>Title</h3><p>Description</p></div>
  </div>
</div>
```

Multi-select: add `data-multiselect` to the container.

Cards (visual design):
```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- prototype content --></div>
    <div class="card-body"><h3>Name</h3><p>Description</p></div>
  </div>
</div>
```

Split view (side-by-side):
```html
<div class="split">
  <div class="mockup"><!-- left --></div>
  <div class="mockup"><!-- right --></div>
</div>
```

Other available classes: `.pros-cons`, `.mockup`, `.mock-nav`, `.mock-sidebar`, `.mock-content`, `.placeholder`, `.section`, `.subtitle`, `.label`.

### 3. Notify the User

Tell the user what to expect and end your turn:
- Remind them of the URL.
- Briefly describe what's on screen.
- Ask them to reply with their thoughts or click an option.

### 4. Read Events

On your next turn, check if `<screen_dir>/.events` exists. Each line is a JSON object:

```jsonl
{"type":"click","choice":"a","text":"Option A - Simple Layout","timestamp":1706000101}
{"type":"click","choice":"c","text":"Option C - Complex Grid","timestamp":1706000108}
```

Merge terminal feedback and click events for the full picture. If `.events` does not exist, the user did not interact with the browser — rely on their terminal reply.

### 5. Iterate or Advance

If feedback requires changes, write a new file (e.g. `layout-v2.html`). Only proceed to the next question when the current one is resolved.

### 6. Push a Waiting Screen When Leaving Visual Mode

When the next step does not need the browser, push a waiting screen:

```html
<!-- waiting.html -->
<div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
  <p class="subtitle">继续在终端中讨论...</p>
</div>
```

### 7. Clean Up

When the visual session is done:

```powershell
python .\scripts\stop-server.py "C:\path\to\project\.superpowers\brainstorm\<session-id>"
```

`stop-server.py` returns `{"status":"stopped"}` on success or `{"status":"not_running"}` if already stopped.

## Decision Rule: Browser vs Terminal

Decide per question, not per session. **Does the user understand it better by seeing it or reading it?**

| Use browser | Use terminal |
|---|---|
| UI prototypes, layouts, navigation structure | Requirements and scope questions |
| Architecture diagrams, component relationships | Conceptual A/B/C choices |
| Side-by-side visual comparisons | Trade-off lists, comparison tables |
| Design detail polishing (spacing, visual hierarchy) | Technical decisions (API design, data modeling) |
| State machines, flow diagrams, entity relationships | Clarifying questions |

## Output Contract

After each visual interaction, report:
- What was displayed.
- What the user chose (from `.events` or terminal).
- Whether to iterate, advance to the next question, or return to text-only brainstorming.

## Failure Handling

- **Server fails to start (node missing, port blocked):** Report the specific failure and fallback to text-only brainstorming. Do not retry more than once.
- **Browser inaccessible:** If the URL is unreachable in a remote/containerized environment, try binding to a non-loopback host: `--host "0.0.0.0" --url-host "localhost"`. If still failing, fallback to text.
- **No events file after user interaction:** The user probably replied via terminal only. Use their text as the primary feedback.
- **Server idle timeout:** The server auto-exits after 30 minutes of inactivity. If you detect the server is gone (no `.server-info`, or `.server-stopped` present), restart it before writing new content.
- **Environment cannot keep background processes alive:** Do not force the visual companion. Switch to pure text immediately.

## Integration

- `brainstorming`: Upstream — brainstorming offers the visual companion to the user. Once accepted, this skill takes over the visual interaction, then hands back to brainstorming for text-based clarification and next steps.
- `chart-visualization`: Adjacent — for single static chart images, use chart-visualization instead.
