---
name: a11y-debugging
description: Uses Chrome DevTools MCP for accessibility debugging and auditing in Trae. Use when testing semantic HTML, ARIA labels, accessible names, focus states, keyboard navigation, tap targets, color contrast, Lighthouse a11y, or Chinese requests such as 可访问性检查, 无障碍审计, 键盘导航测试, 表单标签检查, 按钮没有名称, or 颜色对比度检查.
---

## Core Concepts

**Accessibility Tree vs DOM**: Visually hiding an element (e.g., `CSS opacity: 0`) behaves differently for screen readers than `display: none` or `aria-hidden="true"`. The `take_snapshot` tool returns the accessibility tree of the page, which represents what assistive technologies "see", making it the most reliable source of truth for semantic structure.

**Reading web.dev documentation**: If you need to research specific accessibility guidelines (like `https://web.dev/articles/accessible-tap-targets`), you can append `.md.txt` to the URL (e.g., `https://web.dev/articles/accessible-tap-targets.md.txt`) to fetch the clean, raw markdown version.

## Trae and Windows Notes

- Use Chrome DevTools MCP as the browser/audit path. Do not switch to another browser automation stack.
- Save large Lighthouse or snapshot outputs to Windows absolute paths when possible.
- Keep technical evidence such as role, accessible name, selector, DOM snippet, and audit ID in English or original form.
- When the user writes in Chinese, report findings and fixes in Simplified Chinese.
- Use PowerShell-friendly commands for any local report parsing. Prefer Node.js one-liners over Unix-only tools.

## Do Not Use

Do not use this skill when:

- The task is general browser automation, Network debugging, LCP performance work, or memory leak diagnosis without an accessibility concern.
- The user only asks for visual design polish and does not mention accessibility, semantics, keyboard use, labels, contrast, or assistive technology.
- The page cannot be opened or Chrome DevTools MCP itself is failing; use the MCP troubleshooting workflow first.
- The user wants a conceptual accessibility explanation without auditing or fixing a concrete page or component.

## Workflow Patterns

### 1. Automated Audit (Lighthouse)

Start by running a Lighthouse accessibility audit to get a comprehensive baseline. This tool provides a high-level score and lists specific failing elements with remediation advice.

1.  Run the audit:
    - Set `mode` to `"navigation"` to refresh the page and capture load issues.
    - Set `outputDirPath` to a Windows absolute path such as `C:\Users\skyler\Desktop\lh-report` when running in the user's Windows Trae environment.
2.  **Analyze the Summary**:
    - Check `scores` (0-1 scale). A score < 1 indicates violations.
    - Review `audits.failed` count.
3.  **Review the Report (CRITICAL)**:
    - **Parsing**: Do not read the entire file line-by-line. Use a Node.js one-liner to filter for failures:
      ```powershell
      # Extract failing audits with their details
      node -e "const r=require('./report.json'); Object.values(r.audits).filter(a=>a.score!==null && a.score<1).forEach(a=>console.log(JSON.stringify({id:a.id, title:a.title, items:a.details?.items})))"
      ```
    - This extracts the `selector` and `snippet` of failing elements.

### 2. Browser Issues & Audits

Chrome automatically checks for common accessibility problems. Use `list_console_messages` to check for these native audits:

- `types`: `["issue"]`
- `includePreservedMessages`: `true` (to catch issues that occurred during page load)

### 3. Semantics & Structure

The accessibility tree exposes the heading hierarchy and semantic landmarks.

1.  Navigate to the page.
2.  Use `take_snapshot` to capture the accessibility tree.
3.  **Check Heading Levels**: Ensure heading levels (`h1`, `h2`, `h3`, etc.) are logical and do not skip levels. The snapshot will include heading roles.
4.  **Content Reordering**: Verify that the DOM order (which drives the accessibility tree) matches the visual reading order. Use `take_screenshot` to inspect the visual layout and compare it against the snapshot structure to catch CSS floats or absolute positioning that jumbles the logical flow.

### 4. Labels, Forms & Text Alternatives

1.  Locate buttons, inputs, and images in the `take_snapshot` output.
2.  Ensure interactive elements have an accessible name (e.g., a button should not just say `""` if it only contains an icon).
3.  **Orphaned Inputs**: Verify that all form inputs have associated labels. Use `evaluate_script` with the **"Find Orphaned Form Inputs" snippet** found in [references/a11y-snippets.md](references/a11y-snippets.md).
4.  Check images for `alt` text.

### 5. Focus & Keyboard Navigation

Testing "keyboard traps" and proper focus management without visual feedback relies on tracking the focused element.

1.  Use the `press_key` tool with `"Tab"` or `"Shift+Tab"` to move focus.
2.  Use `take_snapshot` to capture the updated accessibility tree.
3.  Locate the element marked as focused in the snapshot to verify focus moved to the expected interactive element.
4.  If a modal opens, focus must move into the modal and "trap" within it until closed.

### 6. Tap Targets and Visuals

According to web.dev, tap targets should be at least 48x48 pixels with sufficient spacing. Since the accessibility tree doesn't show sizes, use `evaluate_script` with the **"Measure Tap Target Size" snippet** found in [references/a11y-snippets.md](references/a11y-snippets.md).

_Pass the element's `uid` from the snapshot as an argument to `evaluate_script`._

### 7. Color Contrast

To verify color contrast ratios, start by checking for native accessibility issues:

1.  Call `list_console_messages` with `types: ["issue"]`.
2.  Look for "Low Contrast" issues in the output.

If native audits do not report issues (which may happen in some headless environments) or if you need to check a specific element manually, use `evaluate_script` with the **"Check Color Contrast" snippet** found in [references/a11y-snippets.md](references/a11y-snippets.md).

### 8. Global Page Checks

Verify document-level accessibility settings often missed in component testing using the **"Global Page Checks" snippet** found in [references/a11y-snippets.md](references/a11y-snippets.md).

## Troubleshooting

If standard a11y queries fail or the `evaluate_script` snippets return unexpected results:

- **Visual Inspection**: If automated scripts cannot determine contrast (e.g., text over gradient images or complex backgrounds), use `take_screenshot` to capture the element. While models cannot measure exact contrast ratios from images, they can visually assess legibility and identify obvious issues.
