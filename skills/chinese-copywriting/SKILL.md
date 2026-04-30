---
name: chinese-copywriting
description: Apply professional Chinese copywriting and typography guidelines. Use when the user asks to format, polish, write, or translate technical documentation, plans, code comments, or reports in Chinese, including requests like "排版一下文档", "中文文档规范", or "调整中英文混排".
---

# Chinese Copywriting Guidelines

## Overview

Use this skill to format and polish Chinese technical content. The goal is to ensure the text looks professional, reads naturally, and avoids "machine-translation" artifacts by enforcing strict typography rules.

**Core Principle:** Typography serves the reading experience, standardization serves consistency.

## Use This Skill

- When writing, editing, or polishing technical documentation in Chinese.
- When generating reports, plans, or summaries for a Chinese-speaking user.
- When translating English content to Chinese and formatting the result.
- The user explicitly asks for "排版", "中英文混排规范", or "中文文档格式化".

## Do Not Use

- When writing pure code, config files, or logs where spacing would break syntax.
- When the user explicitly requests raw, unformatted output.

## Formatting Rules

### 1. Spacing

- **Add a space between Chinese and English/Numbers:**
  - Good: `使用 Git 进行版本管理，配合 Jenkins 实现持续集成。`
  - Bad: `使用Git进行版本管理，配合Jenkins实现持续集成。`
  - Good: `本次更新包含 3 个新功能和 12 个 Bug 修复。`
  - Bad: `本次更新包含3个新功能和12个Bug修复。`
- **Add a space between numbers and units:**
  - Good: `文件大小不超过 5 MB，响应时间控制在 200 ms 以内。`
  - Bad: `文件大小不超过5MB，响应时间控制在200ms以内。`
  - *Exception*: Do not add spaces for degrees or percentages (e.g., `气温 32°C，CPU 使用率 95%`).
- **Add a space around Markdown links:**
  - Good: `请参考 [官方文档](https://example.com) 获取更多信息。`
  - Bad: `请参考[官方文档](https://example.com)获取更多信息。`

### 2. Punctuation

- **Use full-width punctuation in Chinese contexts:**
  - Good: `注意：该接口需要鉴权，请先获取 Token。`
  - Bad: `注意:该接口需要鉴权,请先获取 Token.`
- **Do not add spaces next to full-width punctuation:**
  - Good: `项目使用 MIT 协议，详见 LICENSE 文件。`
  - Bad: `项目使用 MIT 协议 ，详见 LICENSE 文件 。`
- **Brackets:**
  - Use full-width brackets for pure Chinese context: `请运行安装命令（详见下方说明）。`
  - Use half-width brackets with outer spaces if the content is mostly English/Code: `该项目基于 Spring Boot (v3.2.0) 开发。`

## Output Contract

1. Apply the formatting rules to the target text.
2. Return the polished content.
3. If necessary, provide a brief summary of the major formatting changes made.

## Failure Handling

- If the input is code where spacing changes would break execution, abort formatting for those blocks and explain why.