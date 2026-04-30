---
name: skill-stability-review
description: Use only when the user wants to review Trae Skill packages or SKILL.md files, including related scripts, resources, references, templates, config examples, trigger boundaries, Windows/Trae adaptation, Chinese-user fit, execution stability, script synchronization, and over-localization risks inside a Skill package. Typical Chinese requests include "审查这个 skill", "扫描 skills", "检查这个 SKILL.md", "评估这个 Trae Skill 是否稳定", or "检查 skill 的脚本同步适配". Do not use for ordinary project review, code review, repository readiness, git/GitHub push standards, release checks, general script checks, general Chinese writing polish, or non-Skill stability reviews unless the target is explicitly a Trae Skill package or SKILL.md.
---

# Skill Stability Review

Use this Skill to review complete Trae Skill packages for practical stability. A review target includes `SKILL.md` and any related scripts, resources, references, templates, config examples, or generated artifacts that the Skill instructs the agent to use. The goal is not to make every file Chinese, but to help agents execute reliably in Windows Trae while serving Chinese-speaking users naturally.

When the user writes in Chinese, report findings and recommendations in Simplified Chinese. Keep Skill names, file paths, CLI commands, JSON keys, config keys, tool names, API names, environment variables, and error identifiers in English or original form.

The reviewer is the agent. No human review step is required unless the user explicitly asks for one. Treat scripts as repeatable evidence gatherers, not authorities: the final review is an agent contextual judgment based on script leads, direct file reading, tight evidence, and the rating rules in this Skill.

## Use This Skill

Use this Skill when the user asks to review Trae Skill packages or `SKILL.md` files:

- Review one or more Trae Skills for Windows, Trae, or Chinese-user adaptation.
- Scan `SKILL.md` files for trigger quality, boundaries, workflow clarity, and failure handling.
- Check whether related scripts, references, resources, templates, and config examples match the instructions in `SKILL.md`.
- Audit Skill-package `scripts/`, `references/`, `resources/`, and `templates/` for Windows host compatibility, machine-readable output, script exit behavior, shell assumptions, path examples, and over-localization risks.
- Detect Unix-only assumptions inside Trae Skill instructions or Skill-bundled scripts.
- Detect over-localization that harms Skill machine readability or Skill script stability.
- Rate Skills for readiness, stability, or suitability for Chinese-speaking users.
- Turn a general Skill language policy into concrete Skill-package review criteria.

Do not use this Skill when:

- The user wants to create a new Skill from scratch; use `skill-creator` unless the task is specifically a stability review.
- The user asks for ordinary application code review unrelated to Trae Skills.
- The user asks to scan an ordinary project or repository for git/GitHub push readiness, release readiness, CI readiness, test coverage, code quality, security, or general stability.
- The user asks to inspect ordinary project scripts, build files, docs, or configuration that are not part of a Trae Skill package.
- The task is library/API documentation lookup; use the docs workflow instead.
- The request is only about general Chinese writing quality and not agent execution stability.

By default, review and report findings only. Edit files only when the user explicitly asks to optimize, fix, update, rewrite, or apply changes.

## Core Principle

Review with this hierarchy:

1. Agent execution stability.
2. Windows and Trae compatibility.
3. Chinese user trigger and communication quality.
4. Maintainability and minimal ambiguity.
5. Language polish.

All reviews must enforce the repository-wide `skills/skill-language-policy/SKILL.md`. Do not penalize English technical text just because the user is Chinese. Penalize only when language choice harms trigger stability, execution accuracy, machine readability, or user communication.

Use this rule of thumb:

```text
中文负责意图和沟通，英文负责接口和执行，结构化输出负责稳定性。
```

## Asset Classification

Review every file in a Skill package as an agent asset first, not as human-facing prose first.

Classify each file before judging language or style:

- `trigger asset`: improves auto-invocation and request matching
- `execution contract`: defines ordered steps, inputs, outputs, and failure handling
- `template/prompt asset`: gives the agent reusable slots, schemas, or prompt skeletons
- `reference asset`: supplies supporting patterns, examples, or detailed context
- `human-oriented example`: demonstrates behavior, but should not be the only place where critical execution rules live

Use this decision rule:

- Do not treat "mostly Chinese" as a defect by itself.
- Treat it as a defect only when language or structure harms trigger stability, contract clarity, machine readability, field stability, tool usage, or execution reliability.
- Do not reward English prose by default if it makes the asset less actionable for the agent.

When reviewing a file, ask in this order:

1. What asset type is this file?
2. Does its structure help the agent extract stable instructions or interfaces?
3. Is any machine-sensitive layer incorrectly localized or ambiguously phrased?
4. Only then decide whether language or presentation needs adjustment.

## Inputs

Expected inputs may include:

- A Skill directory such as `C:\Users\skyler\.trae\skills\some-skill`.
- A global skills directory such as `C:\Users\skyler\.trae\skills`.
- One or more `SKILL.md` files.
- Related scripts under `scripts/`, `references/`, `resources/`, or `templates/`.
- Files referenced by `SKILL.md`, including `.py`, `.js`, `.ts`, `.ps1`, `.bat`, `.cmd`, `.json`, `.md`, and template files.
- A policy document such as `LLM中文使用者Skill与Rule语言权衡-20260428-140622.md`.

If the user provides a Skill directory, treat the entire directory as in scope, not only `SKILL.md`. If the user provides a parent skills directory, scan every immediate Skill folder and its related files. Ask only when no reasonable target can be inferred.

## Review Scope

Always review these files when present:

- `SKILL.md`
- `scripts/**/*`
- `references/**/*`
- `resources/**/*`
- `templates/**/*`
- config examples such as `.json`, `.yaml`, `.toml`, `.env.example`
- executable or command-bearing files: `.py`, `.js`, `.ts`, `.mjs`, `.cjs`, `.ps1`, `.bat`, `.cmd`, `.sh`

Do not assume a Skill is stable just because `SKILL.md` is well written. If the Skill invokes a script, the script is part of the contract.

Use progressive disclosure:

- Read `SKILL.md` first.
- Then inspect only files referenced by `SKILL.md` and files in conventional execution locations such as `scripts/`.
- For large reference folders, sample or search for command-bearing files before reading everything.
- When a file under `examples/`, `templates/`, or `resources/` is mostly Chinese, do not treat that alone as a finding; first classify whether it acts as a trigger asset, execution contract, template asset, reference asset, or human-oriented example.

## Review Criteria

### 0. Asset Type And Role

Check:

- The file's job is identifiable: trigger asset, execution contract, template/prompt asset, reference asset, or human-oriented example.
- Critical execution rules do not live only inside a human-oriented example.
- Template and contract files are structured for extraction rather than written as long-form essays.
- Chinese content is not penalized unless it harms machine-sensitive layers or execution reliability.

Common mistake:

```text
Seeing a mostly Chinese Markdown file and flagging it only because it is not English.
```

Correct judgment:

```text
First determine whether the file is a trigger sample, prompt/template, contract, reference, or human-oriented example. Then evaluate whether its language and structure help or hurt agent execution.
```

### 1. Trigger And Boundary

Check:

- `description` contains concrete use cases, not vague capability claims.
- Chinese natural trigger phrases match how the user is likely to ask.
- English technical keywords are present for tools, domains, and APIs.
- Positive and negative boundaries are both present.
- The Skill does not overlap too broadly with adjacent Skills.

Stable pattern:

```md
Use when the user needs [specific action] involving [specific domain/artifact], including Chinese requests such as "...".
Do not use when [near-miss task] or [adjacent Skill territory].
```

### 2. Agent Executability

Check:

- The body tells the agent what to do, not just what the domain means.
- Workflow steps are ordered and actionable.
- Required inputs and optional inputs are explicit.
- Output contract is clear enough for the agent to finish without guessing.
- The Skill distinguishes success, partial success, failure, and missing input.
- Failure handling prevents improvisation.

Missing `Failure Handling` is a stability issue for execution-oriented Skills.

### 3. Windows And Trae Adaptation

Check:

- Commands are PowerShell-compatible when run on the Windows host.
- Windows-accessible paths are used in examples.
- Paths with spaces or Chinese characters are quoted.
- `C:\...`, `D:\...`, `%userprofile%`, or other Windows-friendly patterns appear when local paths matter.
- Trae-specific tool or MCP assumptions are explicit.
- Host shell and Docker/container shell are not confused.

High-risk host-side patterns in Windows Trae:

```text
```bash
export KEY=value
cat <<'EOF'
sudo
chmod
host-side rm -rf
~/...
/tmp/...
```

Container-side POSIX commands may be acceptable when clearly executed inside Docker, such as:

```text
docker exec <container> /bin/sh -lc "..."
```

Path conversion rules:

- Convert host-side command examples, local input paths, output paths, screenshots, reports, logs, archives, and generated files to Windows-accessible paths when the target environment is Windows Trae.
- Quote Windows paths when they contain spaces, Chinese characters, or shell-sensitive characters.
- In JSON, config, and escaped string examples, keep Windows paths correctly escaped, such as `D:\\APP\\Tools\\Everything\\SDK\\dll\\Everything64.dll`.
- Do not convert Docker/container-internal paths such as `/app/input` or `/tmp/...` when the command clearly runs inside the container.
- Do not convert URLs, API routes, package names, CLI flags, environment variable names, MCP tool names, or structured keys into Windows path form.
- Do not convert Windows paths to WSL, Unix, URL, or POSIX-style paths unless the Skill explicitly targets WSL/container execution or the user asks for that form.

Stable pattern:

```text
Windows host examples use Windows paths.
Container, remote, URL, and API paths keep their native form.
JSON/config paths use the escaping required by that format.
```

### 4. Chinese User Fit Without Over-Localization

Check:

- User-facing summaries and clarifying questions default to Simplified Chinese.
- Technical anchors remain in English or original form.
- The Skill does not translate JSON keys, CLI flags, config keys, environment variables, package names, API names, tool names, function names, or error identifiers.
- The Skill does not force all control logic into Chinese when English technical constraints are clearer.
- Chinese document processing rules preserve meaning, punctuation style, spacing style, simplified/traditional script, proper nouns, and quoted text unless the user asks for normalization.

Acceptable:

```md
`--output-dir` 是 Markdown 输出目录，必须使用 Windows 可访问路径。
```

Not acceptable:

```md
把 `--output-dir` 改成 `--输出目录`。
```

### 5. Script Synchronization

When a Skill references scripts, inspect the scripts too.

Check:

- Script file names and function names are stable English identifiers.
- Do not rely only on today's known script types. Treat future script-like files as in scope when they live under `scripts/`, have a shebang, use command-runner names, or appear in references/templates as executable command examples.
- CLI flags are English and match `SKILL.md`.
- Starter configs use Windows-friendly sample paths when the target environment is Windows.
- stdout is machine-readable when possible, preferably JSON.
- stderr is used for progress, warnings, and diagnostic context.
- Non-zero exit codes indicate failure.
- Main JSON keys remain English and stable.
- Chinese appears only where it helps user-facing progress or supplemental hints.
- Script usage examples include PowerShell-compatible invocation when relevant.

Do not over-correct scripts into Chinese. For agent-executed scripts, machine readability is more important than direct user readability.

### 6. Stability Anti-Patterns

Flag these as findings:

- Skill reads like an article rather than an execution procedure.
- Trigger phrases are only English while users are likely to ask in Chinese.
- Trigger phrases are only Chinese while the task depends on English technical keywords.
- `Do Not Use` is missing where adjacent Skills exist.
- Failure handling is missing.
- Windows host instructions contain Unix shell commands.
- Script behavior contradicts `SKILL.md`.
- Script exits with `0` after a real failure.
- Script prints only unstructured prose where JSON would be safer.
- JSON keys, CLI flags, or config keys are translated into Chinese.
- Chinese text processing normalizes punctuation, spacing, or script without explicit user request.
- The Skill asks the agent to use tools or capabilities that may not exist in Trae without fallback.

## Review Workflow

1. Identify target files: list `SKILL.md` files and related files under `scripts/`, `references/`, `resources/`, and `templates/`.
2. When available, run `scripts/review_skills.py` to get repeatable scan leads and preliminary ratings.
3. Read each `SKILL.md` first. Do not bulk-read long resource files unless referenced by the Skill or needed for evidence.
4. Map the Skill's intended job, trigger phrases, required tools, scripts, outputs, failure paths, and the asset type of each important related file.
5. Inspect related scripts for Windows host compatibility, exit code behavior, JSON/CLI stability, and over-localization.
6. Use the script output as evidence, not as the final agent judgment. Resolve `needs_context_review` hits by reading the surrounding file context.
7. Rate each Skill using the rating scale below.
8. Report actionable findings with file paths and tight line references when possible.
9. Recommend minimal fixes first. Do not suggest broad rewrites when a small boundary, command, or failure-handling patch solves the stability issue.
10. If asked to optimize, edit only the needed `SKILL.md` or script files, then run validation.

## Review Script

Use `scripts/review_skills.py` for repeatable scanning before final agent contextual judgment. The script is intentionally lightweight and uses only the Python standard library.

The script helps with:

- Discovering Skill folders and `SKILL.md` files.
- Running `skill-creator/scripts/quick_validate.py` when available.
- Timing out each `quick_validate` run instead of allowing a stuck validation to block the whole review.
- Skipping very large text files with an explicit finding instead of reading unbounded content into memory.
- Scanning related files under `scripts/`, `references/`, `resources/`, and `templates/`.
- Generalizing beyond current file types by scanning known script extensions, shebang files, command-bearing files under `scripts/`, and common runner files such as `Dockerfile`, `Makefile`, `Justfile`, and `Taskfile`.
- Scanning command examples in `references/` and `templates/` for Windows/Trae risk patterns without treating every Markdown command example as a standalone script.
- Finding Windows/Trae risk leads such as `bash` fences, `export`, heredoc, `sudo`, `chmod`, host-side `rm -rf`, Unix-style host paths, and legacy `AskUserQuestion` references.
- Checking common stability gaps such as missing negative boundaries, missing failure handling, generated packaging noise, invalid JSON configs, and script files without obvious failure exits.
- Producing preliminary dimension scores and ratings.

Recommended full-directory scan:

```powershell
python .\skill-stability-review\scripts\review_skills.py --root "C:\Users\skyler\.trae\skills" --markdown --include-generated
```

Recommended single-Skill JSON scan:

```powershell
python .\skill-stability-review\scripts\review_skills.py --skill "C:\Users\skyler\.trae\skills\everything-search" --json
```

Use `--quick-validate-timeout <seconds>` only when a Skill has unusually slow validation. Keep the default for ordinary scans.

Use `--max-file-bytes <bytes>` only when a Skill intentionally includes large reference files that still need text-pattern scanning.

Script output rules:

- Treat `preliminary_rating` as a starting point, not the final agent rating.
- Treat findings with `needs_context_review: true` as leads that require context reading; they do not lower the script's preliminary score until the agent confirms them.
- Keep JSON keys in English and stable.
- Report to Chinese-speaking users in Simplified Chinese after interpreting the script output.
- Do not automatically edit files based only on script findings.
- If `--root` or `--skill` points to a missing directory, the script returns exit code `2` and emits a structured JSON or Markdown error instead of a Python traceback.
- When reviewing `skill-stability-review` itself, the script skips only its documented anti-pattern examples and scan-command sections, not the entire `SKILL.md`.
- If a new script type appears, use the script's scan findings as leads and still read and evaluate the file context directly when it affects execution. The scanner is intentionally extensible, but final agent judgment remains contextual.

## Useful Windows Scan Commands

Use PowerShell-friendly scans when reviewing a local Skill directory:

```powershell
Get-ChildItem -Recurse -Filter SKILL.md
```

```powershell
Get-ChildItem -Recurse -File -Include *.py,*.js,*.ts,*.mjs,*.cjs,*.ps1,*.bat,*.cmd,*.sh,*.json,*.md
```

```powershell
Get-ChildItem -Recurse -File |
  Select-String -Pattern '```bash','export ','cat <<','sudo ','chmod ','rm -rf','/tmp/','~/','AskUserQuestion' -SimpleMatch
```

```powershell
Get-ChildItem -Recurse -File -Include *.py,*.js,*.ts,*.mjs,*.cjs |
  Select-String -Pattern 'process.exit','sys.exit','raise SystemExit','console.error','stderr','stdout','json.dumps','JSON.stringify' -SimpleMatch
```

Treat scan hits as review leads, not automatic findings. For example, `rm -rf` inside `docker exec ... /bin/sh -lc` may be valid container-side behavior, while host-side `rm -rf` in a Windows Trae command example is risky.

## Rating Scale

Use the rating system below for every reviewed Skill. The purpose is to make the review repeatable: first score each dimension, then apply downgrade rules, then assign the final rating.

### Rating Dimensions

Score each dimension from `0` to `5`.

| Dimension | Weight | What It Measures |
|---|---:|---|
| Agent Executability | 25% | Whether the Skill gives the agent clear steps, inputs, outputs, success conditions, and failure paths. |
| Windows/Trae Fit | 20% | Whether host-side commands, paths, shell assumptions, Trae/MCP assumptions, and examples work in Windows Trae. |
| Script Sync | 20% | Whether scripts, references, resources, templates, configs, and generated artifacts match `SKILL.md` and behave reliably. |
| Trigger And Boundary | 15% | Whether the Skill triggers on the right requests, avoids adjacent Skills, and includes enough Chinese and English technical anchors. |
| Chinese User Fit | 10% | Whether user-facing communication works naturally in Simplified Chinese without translating stable technical interfaces. |
| Maintainability | 10% | Whether the Skill is concise, scoped, easy to update, and avoids broad or fragile instructions. |

Dimension score meanings:

| Score | Meaning |
|---:|---|
| 5 | Strong, explicit, and low-risk. |
| 4 | Good, with only small polish issues. |
| 3 | Usable, but has gaps that may cause friction. |
| 2 | Risky, ambiguous, or platform-fragile. |
| 1 | Mostly missing or likely to mislead execution. |
| 0 | Absent, contradictory, or actively harmful. |

### Overall Score

Calculate the weighted score:

```text
overall =
  Agent Executability * 0.25 +
  Windows/Trae Fit * 0.20 +
  Script Sync * 0.20 +
  Trigger And Boundary * 0.15 +
  Chinese User Fit * 0.10 +
  Maintainability * 0.10
```

Convert the weighted score to a rating:

| Weighted Score | Rating |
|---:|---|
| 4.50 - 5.00 | `A` |
| 4.00 - 4.49 | `A-` |
| 3.25 - 3.99 | `B` |
| 2.25 - 3.24 | `C` |
| 0.00 - 2.24 | `D` |

Use these plain-language labels:

- `A`: Ready. Strong trigger, boundaries, Windows/Trae fit, Chinese-user fit, failure handling, and script sync.
- `A-`: Ready with minor polish. No blocking stability issue.
- `B`: Usable but has clear gaps that may cause occasional misfire or execution friction.
- `C`: Risky. Missing important workflow, boundary, platform, or failure handling.
- `D`: Not ready. Likely to mis-trigger, fail on Windows Trae, or confuse agent execution.

### Mandatory Downgrade Rules

Apply these downgrade rules after calculating the weighted score:

- If a Skill has any Blocking issue, final rating cannot exceed `C`.
- If a Skill has any High issue, final rating cannot exceed `B`.
- If host-side Windows commands are likely to fail because examples assume Unix shell, final rating cannot exceed `B`.
- If host-side examples use Linux/container paths where Windows paths are required, or JSON/config examples contain unescaped Windows paths, final rating cannot exceed `B`.
- If a referenced script can return success after a real failure, final rating cannot exceed `B`.
- If `SKILL.md` and a referenced script disagree about required arguments, output paths, or output format, final rating cannot exceed `B`.
- If JSON keys, CLI flags, config keys, environment variables, or API identifiers are translated into Chinese, final rating cannot exceed `B`.
- If the Skill has no meaningful trigger boundary and overlaps adjacent Skills, final rating cannot exceed `B`.
- If the Skill is execution-oriented and has no failure handling, final rating cannot exceed `A-`.
- If scripts exist but were not inspected, mark `Script Sync` as `Not Reviewed` and final rating cannot exceed `B`.
- If external dependencies were unavailable during validation, do not rate validation-dependent behavior above `4` unless the Skill has a clear fallback or dry-run path.

### Severity Mapping

Use this severity mapping for findings:

| Severity | Rating Impact |
|---|---|
| Blocking | Breaks execution, risks destructive behavior, corrupts output, or makes the Skill unusable in Windows Trae. |
| High | Likely causes wrong shell, wrong path, false success, wrong trigger, or script/Skill contradiction. |
| Medium | Causes avoidable ambiguity, manual friction, incomplete fallback, or occasional misfire. |
| Low | Polish, maintainability, packaging noise, or small consistency issue. |

### Red Lines

Treat these as strong evidence for `Blocking` or `High` unless context proves otherwise:

- Host-side `rm -rf`, `sudo`, `chmod`, `export KEY=value`, heredoc, or Unix path examples in Windows Trae instructions.
- Scripts that swallow exceptions and keep exit code `0`.
- Generated output paths that default to inaccessible Linux paths when the host is Windows.
- Machine interfaces localized into Chinese.
- Skill instructions that require a tool, MCP server, or service without checking availability or providing fallback.
- A Skill that claims to review or process scripts but only checks `SKILL.md`.

When rating, separate:

- `Agent Executability`
- `Windows/Trae`
- `Script Sync`
- `Trigger`
- `Chinese Fit`
- `Maintainability`
- `Failure Handling`
- `Overall`

## Output Format

For a small review, respond in this structure:

```md
**总体结论**
[A/A-/B/C/D + one short reason]

**发现**
- [severity] [file/path:line] Problem -> why it affects stability -> minimal fix.

**评分**
| Skill | Agent Executability | Windows/Trae | Script Sync | Trigger | Chinese Fit | Maintainability | Failure Handling | Weighted Score | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

**建议修改**
- ...

**验证**
- ...
```

For a large directory scan, group findings by severity:

- `Blocking`: likely to break execution or corrupt output.
- `High`: likely to cause wrong trigger, wrong shell, wrong path, or false success.
- `Medium`: causes friction or ambiguity.
- `Low`: polish or maintainability.

If no issues are found, say that clearly and mention residual risks such as untested external tools.

## Validation

When edits are made:

- Run `python <skill-creator>/scripts/quick_validate.py <skill-dir>` for changed Skills when available.
- For Python scripts, run `python -m py_compile <script.py>`.
- For JavaScript scripts, run `node --check <script.js>`.
- For CLI scripts, run one safe success or dry-run path and one expected failure path when feasible.
- Scan for host-side Unix-only patterns after edits.

Do not claim a script is fully working if external dependencies such as Docker, ImageMagick, Chrome DevTools MCP, or network services were not actually available.

## Reference Policy

If the repository or workspace contains a language policy document, use it as review context, but do not blindly enforce every example. The practical priority remains:

```text
agent 稳定执行 > Windows/Trae 可运行 > 中文用户自然沟通 > 文案统一。
```
