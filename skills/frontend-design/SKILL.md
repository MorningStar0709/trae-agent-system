---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces in Trae with high design quality. Use when the user asks to build or polish web components, pages, dashboards, React/Vue/HTML/CSS UI, landing pages, posters, or Chinese requests such as 美化页面, 优化前端界面, 做一个网页, 设计组件, 调整样式, or 提升 UI 质感. Generates polished code and avoids generic AI aesthetics.
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

When the user writes in Chinese, discuss design decisions and final summaries in Simplified Chinese. Keep framework names, CSS properties, component names, and file paths in their original form. In Trae on Windows, use Windows-friendly paths and avoid assuming a Unix-only shell.

This skill is for agent execution. Before editing, inspect the existing project conventions and reuse the installed framework, component patterns, and asset pipeline. Prefer stable, local changes over introducing new dependencies. If a dev server, build, or screenshot check fails, report the exact command and error instead of claiming visual verification.

## Do Not Use

Do not use this skill when:

- The request is purely backend, database, CLI, infrastructure, or API work with no user interface surface.
- The user asks only for a conceptual design critique and does not want code or concrete UI changes.
- The task is chart image generation, browser automation, accessibility auditing, or LCP debugging better handled by a specific skill.
- The user wants a low-level framework/API answer such as React, Vue, Tailwind, or Next.js usage without asking for interface design or styling.
- The requested change is limited to copywriting, data modeling, or business logic with no visual or interaction impact.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Trae can produce excellent frontend work when the design direction is specific, intentional, and grounded in the user's actual product context.

## Stability Checks

- Confirm the target files and framework before editing.
- Avoid adding dependencies unless the existing project already uses them or the user explicitly accepts the change.
- Use Windows-friendly commands for build, test, and preview steps.
- For Chinese users, summarize what changed, how it was verified, and any unverified visual risk in Simplified Chinese.
- If text overlap, responsive breakage, or missing assets are suspected, verify with a browser preview or screenshot before finalizing when tools are available.

## Failure Handling

- Unknown framework or entry point -> inspect project files first; if still unclear, ask one concise question before editing.
- Build or dev server command fails -> report the exact command and relevant error, then fix only if the cause is inside the requested change.
- Browser or screenshot tools unavailable -> say visual verification was not run and describe the residual UI risk.
- Missing assets or fonts -> use stable local fallbacks and report the substitution instead of referencing unavailable resources.
- Scope conflict with existing design system -> follow the existing system and avoid introducing a competing visual language.
