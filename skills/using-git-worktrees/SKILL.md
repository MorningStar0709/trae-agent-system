---
name: using-git-worktrees
description: Use when you need a safe git worktree before starting isolated feature work, experiments, or plan execution, including Chinese requests such as “开隔离工作区”“不要污染当前分支”“先建 worktree 再做”. Do not use for read-only analysis, tiny edits that do not justify a separate workspace, or when the user explicitly wants to work in the current tree.
---

# Using Git Worktrees

## Use This Skill

- Need to start a new task without polluting the current workspace.
- Need to maintain multiple branches in parallel.
- Preparing to execute a large implementation plan or experimental changes.
- The current workspace has uncommitted changes, making it unsuitable for direct branch switching.

## Do Not Use

- Just reading code or making very small edits.
- The repository does not use git.
- The user explicitly requests to operate in the current workspace.
- You do not intend to create an independent branch or directory.

## Execution Protocol

### 1. Pre-creation Checks

**Confirm Repository Root:**
```powershell
$repoRoot = git rev-parse --show-toplevel
```

**Check if Local Directory is Ignored:**
If using a directory inside the repository, check if it's ignored:
```powershell
git check-ignore .worktrees
git check-ignore worktrees
```
If the local worktree directory is not ignored:
- Add it to `.gitignore` first.
- Explicitly state this is to prevent worktree contents from polluting the repository state.
- Unless explicitly requested by the user, do not commit these auxiliary changes casually.

**Confirm Baseline is Suitable for Forking:**
Confirm at least:
- The current repository state is readable.
- The base branch exists.
- The new branch name is clear.

### 2. Determine Target Path

Determine the worktree root directory in this order:
1. Existing `.worktrees\` in the repository.
2. Existing `worktrees\` in the repository.
3. Location explicitly specified in the repository rules.
4. Confirm with the user.

PowerShell check example:
```powershell
if (Test-Path ".worktrees") { ".worktrees" }
elseif (Test-Path "worktrees") { "worktrees" }
```

If a global directory is needed, prefer Windows-accessible paths, e.g.:
`%USERPROFILE%\worktrees\<project-name>\`

Example path calculation:
```powershell
$branchName = "feature/auth"
$worktreeRoot = ".worktrees"
$worktreePath = Join-Path $worktreeRoot "auth"
```

### 3. Create Worktree

```powershell
git worktree add "$worktreePath" -b "$branchName"
```

### 4. Minimal Initialization

Enter the worktree and perform minimal initialization based on the project type. Do not blindly run install commands for all ecosystems.

Common examples:
```powershell
if (Test-Path (Join-Path $worktreePath "package.json")) {
  npm install
}
```
```powershell
if (Test-Path (Join-Path $worktreePath "pyproject.toml")) {
  python -m pip install -e .
}
```

### 5. Verify Baseline

Run only the minimal validation to prove "the worktree is ready for development", e.g.:
- Project dependencies installed successfully.
- Key tests can run.
- Lint or type checking can at least start.

If the baseline fails, report it first; do not proceed to implementation with a failing state.

## Trae / Windows Conventions

- Use PowerShell-compatible commands on a Windows host.
- Always quote paths when they contain spaces.
- If modifying `.gitignore`, creating directories, or deleting worktrees, these are explicit actions; do not do them silently.
- If the directory location is ambiguous, ask the user first; do not assume.

## Common Errors

- Not checking if the local directory is ignored.
- Hardcoding Unix-style paths.
- Creating the worktree without confirming the branch name.
- Continuing development even if the baseline fails.
- Running a bunch of unnecessary installations or full test suites upfront.

## Failure Handling

- **Git not installed**: Run `git --version`. If Git is unavailable, stop and report that `git worktree` cannot be used. Suggest installing Git or proceeding without worktrees.
- **Not a Git repository**: Stop and report that `git worktree` cannot be used in the current directory.
- **Target path unclear or risky**: Ask the user before creating directories or changing `.gitignore`.
- **Branch already exists or conflicts**: Report the branch conflict and suggest an alternative branch name.
- **Worktree creation fails**: Show the git error and do not continue with initialization.
- **Baseline validation fails**: Report the failing check and keep the worktree in a blocked state instead of proceeding.

## Output Contract

After the worktree is created, state at least:
- Worktree path.
- Branch name.
- Whether initialization is complete.
- Which baseline validations were run.
- Whether there are unresolved blockers.

## Integration

- `executing-plans`: Execute a plan after isolating the workspace.
- `subagent-driven-development`: Advance tasks within the isolated environment.
- `finishing-a-development-branch`: Decide how to merge, keep, or clean up after work is done.
