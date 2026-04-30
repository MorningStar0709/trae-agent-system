---
name: git-commit
description: Execute git commits in Trae with conventional commit message analysis, intelligent staging, and message generation. Use when the user asks to commit changes, create a git commit, mentions /commit, or says Chinese requests such as 帮我提交, 生成提交信息, 提交当前修改, or 按规范提交. Supports type/scope detection, conventional commit messages, and logical file staging.
---

# Git Commit with Conventional Commits

## Overview

Create standardized, semantic git commits using the Conventional Commits specification. Analyze the actual diff to determine appropriate type, scope, and message.

When the user writes in Chinese, default to a **hybrid Conventional Commit format**: keep the `type` in English (for tooling compatibility), but write the `scope`, `description`, and `body` in Simplified Chinese. Only use a pure English commit message if the user explicitly asks for it or the repository strictly enforces English.

This skill is for agent execution in Trae. On Windows, use PowerShell-compatible commands and avoid Unix-only shell constructs.

## Do Not Use

Do not use this skill when:

- The user asks for a code review, diff explanation, release notes, or changelog but does not want an actual commit.
- The repository has no changes and the user did not explicitly ask for an empty commit.
- The user asks to push, open a pull request, rewrite history, force-push, or manage branches beyond creating the local commit.
- The working tree is in an unresolved merge, rebase, or cherry-pick state and the user has not chosen how to proceed.
- The task involves committing secrets, credentials, private keys, or generated artifacts that should not be versioned.

## Conventional Commit Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Hybrid Chinese/English Format
When adapting for Chinese teams:
```
feat(用户模块): 添加手机号一键登录功能

- 接入运营商一键登录 SDK
- 支持移动、联通、电信三网
```

## Commit Types

| Type       | Purpose                        |
| ---------- | ------------------------------ |
| `feat`     | New feature                    |
| `fix`      | Bug fix                        |
| `docs`     | Documentation only             |
| `style`    | Formatting/style (no logic)    |
| `refactor` | Code refactor (no feature/fix) |
| `perf`     | Performance improvement        |
| `test`     | Add/update tests               |
| `build`    | Build system/dependencies      |
| `ci`       | CI/config changes              |
| `chore`    | Maintenance/misc               |
| `revert`   | Revert commit                  |

## Breaking Changes

```
# Exclamation mark after type/scope
feat!: remove deprecated endpoint

# BREAKING CHANGE footer
feat: allow config to extend other configs

BREAKING CHANGE: `extends` key behavior changed
```

## Workflow

### 1. Analyze Diff

```powershell
# If files are staged, use staged diff
git diff --staged

# If nothing staged, use working tree diff
git diff

# Also check status
git status --porcelain
```

### 2. Stage Files (if needed)

If nothing is staged or you want to group changes differently:

```powershell
# Stage specific files
git add path/to/file1 path/to/file2

# Stage by pattern
git add *.test.*
git add src/components/*

# Interactive staging
git add -p
```

**Never commit secrets** (.env, credentials.json, private keys).

### 3. Generate Commit Message

Analyze the diff to determine:

- **Type**: What kind of change is this?
- **Scope**: What area/module is affected?
- **Description**: One-line summary of what changed (present tense, imperative mood, <72 chars)

### 4. Execute Commit

```powershell
# Single line
git commit -m "<type>[scope]: <description>"

# Multi-line with body/footer in PowerShell
$msg = @"
<type>[scope]: <description>

<optional body>

<optional footer>
"@
git commit -m $msg
```

If the repository uses hooks, let them run. Do not add `--no-verify` unless the user explicitly requests it.

## Best Practices

- One logical change per commit
- Present tense: "add" not "added"
- Imperative mood: "fix bug" not "fixes bug"
- Reference issues: `Closes #123`, `Refs #456`
- Keep description under 72 characters

### Commit Message Granularity

The granularity of the commit body depends on how many logical changes the diff contains:

| Diff scope | Description | Body | Example |
|:-----------|:------------|:-----|:--------|
| **Single atomic change** (1 file, 1 concern) | One line, no body needed | Omit | `feat: add email validation helper` |
| **Single concern across multiple files** (e.g., refactor a function + update all call sites + add tests) | One line summarizing the net effect | Omit or minimal | `refactor(auth): extract token validation to middleware` |
| **Loosely related changes in one commit** (multiple fixes or features grouped by the user) | One line as a category label | **Required**: bullet-point list of what changed, one item per file or per concern | See below |
| **Chore / maintenance** (config, lint, deps, docs) | One line | Omit | `chore: update eslint rules` |

**Body writing rules:**
- One bullet per logical change, not per line of code
- Focus on WHAT changed, not WHY (why goes in the footer or PR description)
- Keep each bullet under 100 characters
- Use present tense, imperative mood, lowercase after the dash

Example of a multi-change commit body:
```text
fix: 修复路由规则触发条件 4 项修复

- alwaysApply: false → true，消除护栏加载空窗期
- 新增 Exception to Escalation，纯机械变更保持 S 级
- M 级下游加入 TDD 选择条件
- 护栏扩充：auth/CI-CD/破坏性操作
```

Example of a single-change commit:
```text
feat(api): add rate limiting middleware

Closes #456
```

## Git Safety Protocol

- NEVER update git config
- NEVER run destructive commands (--force, hard reset) without explicit request
- NEVER skip hooks (--no-verify) unless user asks
- NEVER force push to main/master
- If commit fails due to hooks, fix and create NEW commit (don't amend)
- If `git status --porcelain` is empty, do not create an empty commit unless the user explicitly asks.
- If staged and unstaged changes are mixed, preserve the user's staging intent. Ask before adding unrelated files.
- If secrets or credential-looking files are present, stop and ask before staging or committing them.
- If this is the last commit on a branch, the next step should be `finishing-a-development-branch` for branch wrap-up (merge, PR, keep, or discard).

## Failure Handling

- **Git not installed**: Stop and report Git is not available on this system. Suggest installing Git from https://git-scm.com or using Trae's built-in source control features. Do not attempt git commands.
- **Not a git repository**: Stop and tell the user the current directory is not a repository. Offer to initialize one with `git init` if the user wants version control, or suggest file-level alternatives.
- **No changes -> do not commit**: report that the working tree has no staged or unstaged changes.
- **Merge/rebase/cherry-pick in progress -> stop and ask** whether to continue, abort, or inspect the state.
- **Commit hook failure -> summarize the hook error** and fix the underlying issue when it is in scope; do not bypass hooks by default.
- **Ambiguous staging scope -> ask before staging** broad patterns or unrelated files.
