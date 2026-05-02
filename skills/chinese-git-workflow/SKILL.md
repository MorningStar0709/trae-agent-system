---
name: chinese-git-workflow
description: Configure Git for domestic platforms and manage branching strategies suitable for Chinese teams. Use when the user asks to configure remotes, set up SSH, or manage Git workflows for Gitee, Coding, Jihu GitLab, or CNB, including requests like "配置国内 Git", "设置 Gitee 远程仓库", "推荐适合小团队的 Git 流程".
---

# Chinese Git Workflow

## Use This Skill

- When configuring remotes for Gitee, Coding.net, Jihu GitLab, or CNB.
- When setting up SSH keys for these platforms.
- When configuring mirror synchronization (e.g., push to both Gitee and GitHub).
- When a user asks for a recommended Git branching strategy suitable for their team size in China.

## Do Not Use

- When the user is only asking for general Git commands (e.g., `git add`, `git commit`) unrelated to platform configuration or branching strategy.
- When the user is exclusively using GitHub without needing domestic mirrors.

## Platform Configurations

### 1. Gitee
- **HTTPS:** `https://gitee.com/<org>/<repo>.git`
- **SSH:** `git@gitee.com:<org>/<repo>.git`
- **Mirror Sync (Push to both):**
  ```powershell
  git remote set-url --add --push origin https://gitee.com/<org>/<repo>.git
  git remote set-url --add --push origin https://github.com/<org>/<repo>.git
  ```

### 2. Coding.net
- **HTTPS:** `https://e.coding.net/<team>/<project>/<repo>.git`
- **SSH:** `git@e.coding.net:<team>/<project>/<repo>.git`

### 3. Jihu GitLab / Private GitLab
- **Common Format:** `https://jihulab.com/<group>/<repo>.git`
- **Internal Deployment:** `https://gitlab.yourcompany.com/<group>/<repo>.git`

### 4. CNB (Cloud Native Build)
- **HTTPS (Only):** `https://cnb.cool/<org>/<repo>.git`
- **Authentication:** Username is `cnb`, password is a Personal Access Token.
  ```powershell
  git config credential.helper store
  ```

## Recommended Branching Workflows

When advising teams:
- **Trunk-Based Development (主干开发):** Recommended for small, fast-iterating teams (2-8 people) with solid automated testing. Uses short-lived feature branches merged into `main`.
- **Simplified GitHub/GitLab Flow:** Recommended for most standard projects. Use `main` as the stable release branch, create `feat/*` or `fix/*` branches, and merge via PR/MR. Avoid over-complicated GitFlow unless explicitly required by enterprise compliance.

## Output Contract

When the user asks for configuration:
1. Provide the exact commands needed to set up the requested platform.
2. Explain any platform-specific authentication details (like CNB's HTTPS-only requirement).

When the user asks for workflow advice:
1. Ask clarifying questions about team size and release frequency if not provided.
2. Recommend a specific branching strategy and explain *why* it fits.

## Failure Handling
- If the requested platform is unknown, default to standard Git configuration but ask the user for the platform's specific URL format.