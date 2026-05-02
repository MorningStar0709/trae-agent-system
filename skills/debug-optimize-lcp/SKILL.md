---
name: debug-optimize-lcp
description: Guides LCP and Core Web Vitals debugging in Trae with Chrome DevTools MCP performance tools. Use for Largest Contentful Paint, slow page loads, hero image render delays, page load speed, CWV, Performance trace, or Chinese requests such as 优化 LCP, 页面加载慢, 首屏慢, 核心网页指标, 性能分析, 主内容渲染太慢, or 首屏图片加载慢.
---

## What is LCP and why it matters

Use Simplified Chinese for explanations when the user writes in Chinese. Keep metric names such as LCP, TTFB, Resource load delay, Performance trace, and Core Web Vitals in English.

This skill is for agent execution in Trae with Chrome DevTools MCP. In Windows Trae, save traces, screenshots, or exported reports to Windows absolute paths when the tool supports file output. Keep URLs, selectors, metric names, and request paths in their original form.

## Do Not Use

Do not use this skill when:

- The issue is unrelated to page-load rendering, LCP, Core Web Vitals, Performance traces, or frontend resource timing.
- The user only asks for generic backend performance, database latency, API throughput, or server profiling.
- The task is a full accessibility audit, memory leak diagnosis, or general browser automation flow better handled by a more specific skill.
- There is no page URL, local preview, trace, screenshot, or reproducible page state and the user only wants broad performance advice.

Largest Contentful Paint (LCP) measures how quickly a page's main content becomes visible. It's the time from navigation start until the largest image or text block renders in the viewport.

- **Good**: 2.5 seconds or less
- **Needs improvement**: 2.5–4.0 seconds
- **Poor**: greater than 4.0 seconds

LCP is a Core Web Vital that directly affects user experience and search ranking. On 73% of mobile pages, the LCP element is an image.

## LCP Subparts Breakdown

Every page's LCP breaks down into four sequential subparts with no gaps or overlaps. Understanding which subpart is the bottleneck is the key to effective optimization.

| Subpart                       | Ideal % of LCP | What it measures                               |
| ----------------------------- | -------------- | ---------------------------------------------- |
| **Time to First Byte (TTFB)** | ~40%           | Navigation start → first byte of HTML received |
| **Resource load delay**       | <10%           | TTFB → browser starts loading the LCP resource |
| **Resource load duration**    | ~40%           | Time to download the LCP resource              |
| **Element render delay**      | <10%           | LCP resource downloaded → LCP element rendered |

The "delay" subparts should be as close to zero as possible. If either delay subpart is large relative to the total LCP, that's the first place to optimize.

**Common Pitfall**: Optimizing one subpart (like compressing an image to reduce load duration) without checking others. If render delay is the real bottleneck, a smaller image won't help — the saved time just shifts to render delay.

## Debugging Workflow

Follow these steps in order. Each step builds on the previous one.

### Step 1: Record a Performance Trace

Navigate to the page, then record a trace with reload to capture the full page load including LCP:

1. `navigate_page` to the target URL.
2. `performance_start_trace` with `reload: true` and `autoStop: true`.

The trace results will include LCP timing and available insight sets. Note the insight set IDs from the output — you'll need them in the next step.

### Step 2: Analyze LCP Insights

Use `performance_analyze_insight` to drill into LCP-specific insights. Look for these insight names in the trace results:

- **LCPBreakdown** — Shows the four LCP subparts with timing for each.
- **DocumentLatency** — Server response time issues affecting TTFB.
- **RenderBlocking** — Resources blocking the LCP element from rendering.
- **LCPDiscovery** — Whether the LCP resource was discoverable early.

Call `performance_analyze_insight` with the insight set ID and the insight name from the trace results.

### Step 3: Identify the LCP Element

Use `evaluate_script` with the **"Identify LCP Element" snippet** found in [references/lcp-snippets.md](references/lcp-snippets.md) to reveal the LCP element's tag, resource URL, and raw timing data.

The `url` field tells you what resource to look for in the network waterfall. If `url` is empty, the LCP element is text-based (no resource to load).

### Step 4: Check the Network Waterfall

Use `list_network_requests` to see when the LCP resource loaded relative to other resources:

- Call `list_network_requests` filtered by `resourceTypes: ["Image", "Font"]` (adjust based on Step 3).
- Then use `get_network_request` with the LCP resource's request ID for full details.

**Key Checks:**

- **Start Time**: Compare against the HTML document and the first resource. If the LCP resource starts much later than the first resource, there's resource load delay to eliminate.
- **Duration**: A large resource load duration suggests the file is too big or the server is slow.

### Step 5: Inspect HTML for Common Issues

Use `evaluate_script` with the **"Audit Common Issues" snippet** found in [references/lcp-snippets.md](references/lcp-snippets.md) to check for lazy-loaded images in the viewport, missing fetchpriority, and render-blocking scripts.

## Optimization Strategies

After identifying the bottleneck subpart, apply these prioritized fixes.

### 1. Eliminate Resource Load Delay (target: <10%)

The most common bottleneck. The LCP resource should start loading immediately.

- **Root Cause**: LCP image loaded via JS/CSS, `data-src` usage, or `loading="lazy"`.
- **Fix**: Use standard `<img>` with `src`. **Never** lazy-load the LCP image.
- **Fix**: Add `<link rel="preload" fetchpriority="high">` if the image isn't discoverable in HTML.
- **Fix**: Add `fetchpriority="high"` to the LCP `<img>` tag.

### 2. Eliminate Element Render Delay (target: <10%)

The element should render immediately after loading.

- **Root Cause**: Large stylesheets, synchronous scripts in `<head>`, or main thread blocking.
- **Fix**: Inline critical CSS, defer non-critical CSS/JS.
- **Fix**: Break up long tasks blocking the main thread.
- **Fix**: Use Server-Side Rendering (SSR) so the element exists in initial HTML.

### 3. Reduce Resource Load Duration (target: ~40%)

Make the resource smaller or faster to deliver.

- **Fix**: Use modern formats (WebP, AVIF) and responsive images (`srcset`).
- **Fix**: Serve from a CDN.
- **Fix**: Set `Cache-Control` headers.
- **Fix**: Use `font-display: swap` if LCP is text blocked by a web font.

### 4. Reduce TTFB (target: ~40%)

The HTML document itself takes too long to arrive.

- **Fix**: Minimize redirects and optimize server response time.
- **Fix**: Cache HTML at the edge (CDN).
- **Fix**: Ensure pages are eligible for back/forward cache (bfcache).

## Verifying Fixes & Emulation

- **Verification**: Re-run the trace (`performance_start_trace` with `reload: true`) and compare the new subpart breakdown. The bottleneck should shrink.
- **Emulation**: Lab measurements differ from real-world experience. Use `emulate` to test under constraints:
  - `emulate` with `networkConditions: "Fast 3G"` and `cpuThrottlingRate: 4`.

## Failure Handling

- Performance tools unavailable -> fall back to `evaluate_script`, `list_network_requests`, and screenshot evidence, and clearly state that full trace insights were not available.
- Trace recording fails or returns no LCP insight -> verify page load, rerun once with `reload: true`, then use the LCP element snippet and network waterfall as the fallback path.
- LCP element cannot be identified -> report that no LCP candidate was captured and ask for a reproducible page state or slower emulation.
- Network request for the LCP resource is missing -> check whether the LCP is text-based, CSS background-based, inline data, or loaded from cache before recommending fixes.
- When reporting to a Chinese user, lead with the bottleneck subpart and evidence, then give the smallest safe fix and verification step.
