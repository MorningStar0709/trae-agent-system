# Trae AI Agent System: Make Your Agent Smarter and More Reliable

> A Trae AI Agent rules and skills collection.
>
> Quick intro: [01-intro.md](./01-intro.md) | Complete overview: [05-architecture.md](./05-architecture.md) | Quick reference: [03-components.md](./03-components.md)

***

## One-Line Summary

**33 Skills + 8 Rules + Memory System** — transforms your AI Agent from "can do anything but unstable" to "fast when simple, rigorous when complex, always learning".

***

## What It Solves

| Agent's Common Mistakes                           | Our Solution                                                        |
| :------------------------------------------------ | :------------------------------------------------------------------ |
| Starts coding before clarifying requirements      | **brainstorming** skill — ask first, then act                       |
| "Blind guess" fixes that hide the real problem    | **systematic-debugging** — requires evidence before fixing          |
| Treats core config changes the same as text edits | **T-Shirt sizing + Forced escalation** — differentiate by task size |
| Says "it's done" without running tests            | **verification-before-completion** — no verification, no completion |
| Asks too much or too little                       | **question-threshold** — ask when needed, stay silent otherwise     |
| Forgets how to resolve port conflicts             | **self-improvement** — automatically remembers lessons              |
| New conversation = start from scratch             | **Core Memory** — cross-session experience accumulation             |
| Suggests refactoring just to view a file          | **change-proposal-threshold** — evaluate before proposing           |

***

## Three Key Highlights

### Highlight 1: Task Sizing — No Time Wasted

The Agent automatically judges task size — edit text directly, use full workflow only for new features. Won't over-engineer simple tasks, won't skip thoroughness on hard ones. This **T-Shirt 4-D Matrix** (file scope × change type × risk level × expected pace) is an original design, not official standard capability.

### Highlight 2: Closed-Loop Quality — No Guessing

Every line of code requires verification: tests pass, build succeeds, bug reproduction path disappears — only then is it "done". Trust fresh evidence, not gut feeling. From `brainstorming` → `writing-plans` → `executing-plans` → `verification-before-completion` → `git-commit`, each skill works like a production line, collaborating upstream-downstream.

### Highlight 3: Self-Improvement — Never Repeat Mistakes

Every time a new problem arises, the Agent automatically stores lessons in long-term memory. Next time the same port conflict or environment issue appears — no need to search again, it already remembers. This mechanism builds on Trae's native memory system without breaking it, actively managing memory quality for mutual benefit.

***

## Design Philosophy: Not Just Another Prompt Collection

Many "Agent enhancement packs" are just prompt collections. Our system has deeper design logic:

**Rule + Skill Dual-Wheel Drive**: Rules act like traffic police deciding "which path to take", Skills act like professional toolboxes handling "how to do it". Each does its job without interfering.

**Fully Compliant with Trae Official Specs**: Our 33 skills + 8 rules strictly follow Trae's frontmatter spec, SKILL.md contract template, and 250-character description limit. Can serve as a **best practice reference**.

**Original Decision Mechanisms**: T-Shirt sizing (4-dimension task scoring) and question thresholds (when to ask users, when not to) are original designs by this system. Trae won't have these built-in — we designed them based on observed pain points.

**Honest Response to Platform Limits**: The `agent-blueprint-architect` skill doesn't try to automate Agent creation via scripts — because Trae's Agent config is stored in an encrypted database, making external writes extremely unstable. The team abandoned automation in favor of **"blueprint delivery + manual paste"**. Users copy sections into the Trae UI. Stability over flashiness.

**Continuously Refined Execution Contracts**: Each Skill includes Input Contract, Do Not Use boundaries, Failure Handling degradation paths, and Integration upstream-downstream declarations. Each skill underwent 3-5 rounds of iteration with git-traceable history. Not one-off prompts, but ongoing engineering investment.

***

## Special Considerations for Chinese Developers

- Full Chinese natural language triggers — say "帮我提交" or "排查这个 bug" and it activates
- Domestic Git platform support: detects remote address via `git remote -v` during branch completion — github.com follows GitHub flow, Gitee/GitLab/Coding follow domestic platform flow
- Hybrid commit messages — `type` in English for tool compatibility, body in Chinese to reduce communication cost
- Skill docs: English for machine-readable fields, Chinese for human-readable instructions
- Full Windows environment adaptation: PowerShell syntax, port conflict recovery, path conventions

***

## Brief Overview

**Rules Layer** — 8 "traffic rules" telling the Agent what it can/can't do and when to ask users. 5 are always-on, 3 are scenario-triggered.

**Skills Layer** — 33 "professional toolboxes" covering requirement clarification, design planning, code implementation, debugging, code review, commit management, branch completion, knowledge accumulation, browser debugging, accessibility auditing, data visualization, frontend design...

**Memory Layer (Core Memory)** — Agent's "notebook". Knowledge stores facts, Rule stores preferences, Experience stores lessons. Auto-loaded in new conversations, no need to start from scratch.

***

## Quick Try

Place this project's `.trae/` directory into your Trae IDE project root. The Agent immediately gains all these capabilities. No configuration, no installation.

After starting a conversation, try these commands:

> "帮我排查一下这个报错"
> "实现这个功能，先写计划"
> "改好了没？跑下测试验证一下"
> "记住这个处理方式"
> "提交代码"

The Agent will automatically match the corresponding skills and rules to complete.

***

> Project source: all code under the `.trae/` directory.
>
> More: [01-intro.md](./01-intro.md) (quick intro) | [04-design.md](./04-design.md) (design philosophy) | [05-architecture.md](./05-architecture.md) (complete overview) | [03-components.md](./03-components.md) (quick reference)

