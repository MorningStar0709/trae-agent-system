---
name: finishing-a-development-branch
description: Use when implementation is done, validation has passed, and you need to decide how to wrap up the current branch, including Chinese requests such as “接下来合并还是提 PR”“这条分支怎么收尾”“保留还是丢弃当前工作”. Do not use while implementation or verification is still in progress, or when the user only wants a normal commit.
---

# Finishing a Development Branch

## Overview

Use this skill for development wrap-up: confirm that results are genuinely usable first, provide structured options, and then execute merge, push, keep, or discard based on the user's choice.

**Core Principle:** Validate first, give options next, execute wrap-up last.

## Use This Skill

- Feature implementation is complete.
- Key validations have passed.
- You need to decide whether to merge locally, create a PR, keep as-is, or discard.
- The current work may be in a worktree or an isolated branch.

## Do Not Use

- Code is not finished or validations haven't run.
- The user only wants a normal commit, not branch-level wrap-up.
- You are still debugging or implementing a feature.

## Input Contract

**Required Inputs:**
- Implementation is complete and validation results exist.
- The current branch state is identifiable.

**Optional but highly recommended inputs:**
- Base branch name.
- Whether currently in a worktree.
- Whether the user wants to push, create PR, keep, or discard.
- Whether `gh` is available in the current environment.

**Missing input handling:**
- **Validation evidence is stale or missing**: Return to validation first; do not enter wrap-up.
- **Base branch unclear**: Ask the user first.
- **Remote capabilities unclear**: Check first or explain uncertainty; do not pretend a PR can be created.

## Execution Protocol

### 1. Confirm Validation State First

If there is no fresh validation evidence, stop and run validation first. Do not directly ask "what's next?".

Confirm at least:
- Key tests have been re-run.
- Build or lint (if relevant) has passed.
- Current branch state is clear.

### 1.5. Knowledge Promotion Gate <!-- anchor: knowledge-promotion-gate -->

During wrap-up of medium or larger tasks, check if any persistent workarounds, rule discoveries, or recurring errors occurred during this branch. Examples:

- A non-obvious environment workaround was discovered during implementation.
- A project convention was clarified through user correction.
- A recurring error pattern was encountered.

If such knowledge exists, invoke `self-improvement` to capture it before proceeding with wrap-up. This ensures learnings are not lost when the branch is merged and discarded.

Also, if memories are near the 20-entry limit or containing outdated entries, run a quick memory maintenance pass using `self-improvement`'s `resources/memory-maintenance.md` before adding new entries.

### 2. Identify Base Branch and Current Branch

PowerShell example:
```powershell
$currentBranch = git branch --show-current
$baseBranch = "main"
```
If the base branch is unclear, ask the user first. Do not assume arbitrarily.

### 3. Provide Structured Options

Recommend providing only these 4 options:
1. Merge locally back to the base branch.
2. Push and create a Pull Request.
3. Keep the current branch and workspace as-is.
4. Discard current work.

In Trae, prioritize using the current environment's structured questioning tool to let the user choose, rather than asking an open-ended question.

### 4. Execute Based on Choice

#### Option 1: Merge Locally
Execute only after validation passes.
```powershell
git checkout $baseBranch
git pull
git merge $currentBranch
```
After merging, re-run minimal necessary validations; if they pass, consider deleting the feature branch.

#### Option 2: Push and Create PR

First, detect the remote configuration:
```powershell
git remote -v
```
- **No remote configured**: Report that no remote is set up. Offer to configure one using `chinese-git-workflow` (for Gitee, GitLab, Coding) or standard `git remote add origin <url>` for GitHub. Do not proceed with push.
- **Remote is GitHub (`github.com`)**: Use standard GitHub flow:
  ```powershell
  git push -u origin $currentBranch
  gh pr create --title "<title>" --body "<summary>"
  ```
- **Remote is Gitee, GitLab, Coding, CNB, or other**: Push the branch, then guide the user to create a PR/MR through the platform's web UI. The `gh` CLI is GitHub-specific and will not work on other platforms. See `chinese-git-workflow` for platform-specific remote configuration.
- **Multiple push URLs configured (mirror sync)**: Push once — Git will push to all configured URLs automatically.

If `gh` is unavailable when using GitHub:
- Explicitly state the PR was not created.
- Provide the completed steps and the next manual actions required.

Default to **keeping the current worktree/branch**. Do not automatically clean up the local workspace right after creating a PR.

#### Option 3: Keep As-Is
Output the current branch name, path, and validation status, then stop.

#### Option 4: Discard Current Work
Requires secondary confirmation. The confirmation text must explicitly state what will be deleted:
- Branch.
- Worktree (if exists).
- Unsaved local work.

Only execute the deletion after explicit user confirmation.

## Relationship with Worktrees

If the current work is in a git worktree:
- **Option 1**: After a successful merge, optionally clean up the worktree.
- **Option 2**: Keep the worktree by default.
- **Option 3**: Keep the worktree.
- **Option 4**: Delete the worktree after confirmation.

## Trae / Windows Conventions

- Before providing any wrap-up options, confirm validation evidence using `verification-before-completion` standards.
- Use PowerShell-compatible git / gh commands on a Windows host.
- When deleting a branch, worktree, or discarding changes, explicit confirmation is mandatory.
- If the current environment lacks `gh` or remote permissions, do not pretend a PR was created successfully.
- For non-GitHub remotes (Gitee, GitLab, Coding, CNB), reference `chinese-git-workflow` for platform-specific PR/MR workflows.

## Failure Handling

- **Git not installed or no repository**: Run `git --version` first to confirm Git is available, then `git rev-parse --is-inside-work-tree` to confirm the current directory is a repository. If either fails, stop and offer to install Git, initialize one with `git init`, or proceed with file-level operations only.
- **Validation failed**: Stop wrap-up, return to implementation or fixing.
- **Base branch unclear**: Ask the user first.
- **Remote push failed**: Report the actual error; do not say "PR created".
- **Deletion action is risky**: Re-confirm the scope and consequences.

## Output Contract

When completing the wrap-up, state at least:
- Current branch and base branch.
- Validations run.
- Which wrap-up option the user chose.
- Actual commands or actions executed.
- Whether the branch/worktree was kept.

Use this fixed skeleton by default:

```markdown
分支收尾已完成。

**Current Branch:** `<current-branch>`
**Base Branch:** `<base-branch>`
**Wrap-up Method:** `Merge Locally` | `Create PR` | `Keep As-Is` | `Discard Work`

**Validation Status:**
- [Tests / lint / build / manual checks]

**Actions Executed:**
- [Commands or operations performed]

**Branch / Worktree Status:**
- [Kept / Deleted / Unmodified]

**Risks or Next Steps:**
- [If none, write `- None`]
```

If wrap-up is not truly completed due to validation failure, remote failure, or lack of user confirmation, do not use "completed". Explicitly state the current stalled state and the next step.

## Integration

- `using-git-worktrees`: Adjacent — if the current work is in an isolated workspace.
- `verification-before-completion`: Upstream — validate before stating "ready to merge / ready to commit".
- `git-commit`: Upstream — if the branch has uncommitted work that needs final commits before wrap-up.
- `chinese-git-workflow`: Adjacent — use when the remote is Gitee, GitLab, Coding, CNB, or requires platform-specific PR/MR configuration.
