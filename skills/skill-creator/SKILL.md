---
name: skill-creator
description: Create, modify, refactor, review, or iterate Trae Skills. Use only when the user is explicitly working on a Skill or SKILL.md, including Chinese requests such as 创建 skill, 修改 SKILL.md, 优化触发条件, 适配 Trae, 清理旧平台内容, or 减少歧义. Do not use for ordinary coding, docs writing, prompt writing, workflow discussion, or project refactoring unless the user asks to turn that work into a Skill or edit an existing Skill.
---

# Skill Creator

Use this Skill to create or improve Trae Skills. A Trae Skill is a reusable capability module: a clear, rigorous, executable instruction document that tells the model when to use it, how to act, and what output to produce.

The default goal is a Skill that is easy for Trae to discover, hard to misuse, and simple to maintain.

When the user writes in Chinese, discuss decisions and final summaries in Simplified Chinese. Keep Skill names, directory names, frontmatter keys, commands, and file paths in English or original form.

## Use This Skill

Use this Skill only when the active task is about creating, editing, validating, importing, or refactoring a Trae Skill itself.

Use it when the user asks to:

- Create a Skill, custom Skill, or `SKILL.md`.
- Modify, optimize, rewrite, review, or debug an existing Skill.
- Improve when a Skill should or should not be invoked.
- Convert a repeated workflow, team convention, or instruction set into a reusable Skill.
- Add or reorganize Skill files such as `examples/`, `templates/`, `resources/`, or helper scripts.
- Compare behavior of a proposed or existing Skill against a no-Skill baseline.
- Remove stale platform assumptions from a Skill.

Do not use this Skill when the user asks for:

- Ordinary application code, scripts, tests, docs, or refactors.
- General prompt writing that is not intended to become a Trae Skill.
- General workflow brainstorming without a request to create or update a Skill.
- Library, framework, SDK, API, CLI, or cloud-service help unless the result will be encoded into a Skill.
- General Trae IDE usage help unrelated to Skills.

If the request is ambiguous, proceed without this Skill unless the user mentions Skill creation, Skill editing, `SKILL.md`, a skills directory, or turning the workflow into a reusable Skill.

## Trae Skill Contract

Every Skill must make these three things explicit:

- When: the conditions that should trigger the Skill, and the near-miss cases that should not.
- How: the ordered procedure Trae should follow, including checks, tools, scripts, and fallback paths.
- What: the expected output format, artifacts, success criteria, and failure response.

All new or updated Skills must comply with `skills/skill-language-policy/SKILL.md`.

Do not treat a Skill as a one-off prompt or human-facing article. Write it as operational guidance for an AI agent.

## Agent-First Asset Model

Treat every file in a Skill package as a potential execution asset for the agent, not as human-facing documentation by default.

Before creating, importing, or rewriting files, classify each file by its primary job:

- `trigger asset`: improves auto-invocation and request matching
- `execution contract`: defines ordered steps, inputs, outputs, success criteria, and failure handling
- `template/prompt asset`: provides reusable skeletons, slots, or structured prompts the agent can fill
- `reference asset`: supplies supporting patterns, deeper examples, schemas, or domain context loaded on demand
- `human-oriented example`: shows representative behavior, but should not carry critical execution rules on its own

Apply this priority order when deciding what to write or rewrite:

1. Trigger stability
2. Execution contract clarity
3. Machine readability and schema stability
4. Human readability

Do not rewrite files just because they look "too Chinese" or "not international enough". Rewrite only when the current language or structure harms trigger matching, boundary clarity, structure extraction, field stability, tool usage, or execution reliability.

Prefer English or original form for machine-sensitive layers:

- frontmatter keys and `description`
- commands, file paths, tool names, API names, config keys, JSON keys, environment variables
- template placeholders, output fields, and script interfaces

Chinese is acceptable or preferred when it improves:

- natural trigger examples for Chinese-speaking users
- concise explanation of constraints, steps, and failure handling
- user-facing summaries that do not alter machine-sensitive structure

## Target Structure

Use this folder layout unless the user has a different existing structure:

```text
skill-name/
├── SKILL.md
├── examples/
│   ├── input.md
│   └── output.md
├── templates/
│   └── component.tsx
└── resources/
    └── style-guide.md
```

Only `SKILL.md` is required. Create optional directories only when they directly reduce ambiguity, repeated work, or context load.

Use Trae's canonical optional directories by default:

- `examples/`: trigger assets, behavior examples, or human-oriented examples.
- `templates/`: reusable template/prompt assets copied or adapted into final outputs.
- `resources/`: reference assets, scripts, style guides, schemas, or other supporting files.

## Frontmatter Rules

`SKILL.md` starts with YAML frontmatter:

```yaml
---
name: skill-name
description: Third-person capability and trigger description.
---
```

Rules:

- `name` uses lowercase letters, digits, and hyphens only.
- `name` is unique, concrete, and no longer than 64 characters.
- Prefer gerund or action-oriented names, such as `running-tests`, `reviewing-code`, or `migrating-database`.
- Do not include version markers such as `v2`, dates, or personal names unless they are part of the real domain.
- `description` is the primary discovery surface, so put all trigger guidance there.
- Write `description` in third person from Trae's perspective.
- Include both capability and use cases, including likely user phrases and contexts.
- Keep `description` under 1024 characters.
- Do not put "when to use this Skill" only in the body; the body is loaded after triggering.

Good description pattern:

```yaml
description: Review code for correctness, maintainability, security, and test risk. Use when the user asks for code review, PR feedback, bug-risk analysis, refactor assessment, edge-case review, or implementation critique.
```

Avoid:

```yaml
description: I can help with code.
```

## Creation Workflow

Follow this sequence for new Skills and major rewrites.

### 1. Capture Intent

Extract context from the conversation before asking questions. Identify:

- The repeated task or workflow the user wants to capture.
- Example prompts that should trigger the Skill.
- Similar prompts that should not trigger it.
- Required inputs, optional inputs, and missing information.
- Expected outputs, file artifacts, or final response shape.
- Tools, CLI commands, APIs, local paths, and external docs involved.
- Existing failures, corrections, or user preferences from the current conversation.

Ask only for information that is required to avoid a risky assumption. If the user gives a target path, use it.

### 2. Establish a No-Skill Baseline

Before adding rules, understand what Trae already does without the Skill. Use recent conversation history, a quick manual dry run, or a small test prompt.

Record the actual gaps:

- Trigger confusion: Trae does not know when the workflow applies.
- Execution drift: Trae chooses inconsistent steps.
- Missing context: Trae forgets required files, schemas, or conventions.
- Output mismatch: Trae produces the wrong format or incomplete artifacts.
- Failure ambiguity: Trae improvises instead of following a defined recovery path.

Only add Skill content that addresses a real or strongly expected gap.

### 3. Define Eval Cases First

Create 3 to 5 realistic eval prompts before writing a large Skill. Cover:

- Golden path: the most common successful request.
- Boundary path: valid request with missing, messy, or partial inputs.
- Negative path: a near-miss that should not use the Skill or should refuse.
- Regression path: a known failure from prior usage.

For each eval, define a pass/fail rule. Prefer objective checks when possible.

Use this lightweight format when no eval system exists:

```json
{
  "skill_name": "skill-name",
  "evals": [
    {
      "id": "golden-path",
      "prompt": "Realistic user request",
      "expected_output": "Observable success criteria",
      "files": []
    }
  ]
}
```

Save evals under `evals/evals.json` when the project already uses eval files. Otherwise, keep them in the working notes or a sibling test workspace and avoid adding permanent clutter.

### 4. Write the Minimal Skill

Write the shortest Skill that makes the evals pass. Start with:

- Purpose: one paragraph naming the exact capability.
- Inputs: required and optional information.
- Workflow: numbered steps Trae can execute.
- Output: exact response or artifact contract.
- Failure handling: known failure cases and what to do.
- Resources: direct links to files that should be read only when needed.

Use imperative instructions. Prefer concrete verbs: inspect, ask, run, compare, patch, validate, summarize.

### 5. Add Resources Only When Useful

Use `resources/` for detailed domain knowledge that should be loaded on demand:

- API notes
- schemas
- glossary
- example-heavy guidance
- long policy or business rules

Put scripts under `resources/` by default, or under `scripts/` when the existing Skill already uses that convention. Use scripts for deterministic or repetitive operations:

- validation
- conversion
- formatting
- report generation
- fragile command sequences

Use `templates/` for reusable output materials:

- templates
- sample files
- boilerplate projects

Use `examples/` for compact input/output examples that clarify expected behavior.

Use `resources/` for icons, fonts, large samples, design resources, and other support files that are not themselves reusable output templates.

Do not create README, changelog, install guide, or extra documentation unless the Skill itself needs that file at runtime.

### 6. Validate and Iterate

After edits:

1. Check frontmatter and naming.
2. Search for stale platform names, ambiguous "it/this/that", and undefined terms.
3. Run relevant scripts or representative commands.
4. Re-run eval prompts manually or with available agent tooling.
5. Compare the result against the no-Skill baseline.
6. Simplify rules that did not affect behavior.

Use `scripts/quick_validate.py <path-to-skill-folder>` if this Skill's helper scripts are available.

## Writing Standards

### Single Responsibility

Each Skill should do one core job. Split a Skill when it combines unrelated actions.

Good:

- `running-unit-tests`
- `reviewing-code`
- `migrating-database`
- `formatting-release-notes`

Avoid:

- one Skill that runs tests, updates PR status, writes release notes, and sends notifications

### Boundary Clarity

State positive and negative boundaries when confusion is likely.

Use this pattern:

```markdown
Use this Skill when:
- The user asks to run project tests or diagnose failing test commands.
- The request includes a repository, package, or CI context.

Do not use this Skill when:
- The user only asks for a conceptual explanation of testing.
- The task is a code review and no test execution is needed.
```

Keep this section brief. The detailed trigger language still belongs in `description`.

### Structured Inputs and Outputs

For workflows with required data, define a compact contract:

```markdown
Input:
- pr_id: pull request number or URL
- branch: source branch
- run_tests: whether tests should be executed

Output:
- success: true/false
- summary: concise human-readable result
- artifacts: paths to logs, reports, or generated files
- error_message: present only on failure
```

### Degrees of Freedom

Match instruction strictness to task risk:

- High freedom: use principles and heuristics for subjective analysis or creative tasks.
- Medium freedom: use templates, checklists, or pseudocode when there is a preferred path.
- Low freedom: use scripts and exact command sequences for fragile or irreversible work.

Default to medium freedom. Move to low freedom when mistakes are costly, repetitive, or hard to detect.

### Progressive Disclosure

Keep `SKILL.md` as the entry point and navigation layer. Do not make it a giant reference manual.

Rules:

- Keep `SKILL.md` under 500 lines when possible.
- Link every resource file directly from `SKILL.md`.
- Avoid resource chains such as `SKILL.md -> a.md -> b.md`.
- Add a table of contents to resource files longer than 100 lines.
- Put information in one place only; do not duplicate detailed rules between `SKILL.md` and resources.

### Failure Strategy

Define failure behavior explicitly:

```markdown
On Failure:
- Missing input: ask one concise question listing the missing field.
- Invalid file path: report the path and ask for a valid location.
- Script failure: show the relevant error summary, preserve logs, and do not guess success.
- External service unavailable: retry only if the Skill says retrying is safe.
```

### Script Hardening

When adding scripts:

- Validate inputs before side effects.
- Print clear success and failure output.
- Convert technical exceptions into actionable messages.
- Use named constants for timeouts, limits, and thresholds.
- Let callers override risky defaults with flags.
- Avoid hidden network calls or destructive operations.
- Test at least one representative successful run and one failure path.

Good script output:

```text
CHECK FAILED: Node.js version mismatch
- Required: >= 18.0.0
- Detected: 16.14.0

VALID OPTIONS:
1. Upgrade Node.js to a supported version.
2. Switch to a compatible build image.
```

## Trae-Specific Guidance

- Project Skills live in the current project's `.trae/skills/` directory.
- Global Skills for international Trae live in the user's `.trae/skills/` directory, such as `%userprofile%/.trae/skills` on Windows or the user's home `.trae/skills` directory on macOS/Linux.
- In this workspace, the user is editing `C:\Users\skyler\.trae\skills`; treat it as the explicit Trae Skills target path.
- Ask whether a new Skill should be project-level or global only when the target location is not provided and the choice affects behavior.
- If creating a project Skill from inside a repository, prefer `<project>/.trae/skills/<skill-name>/SKILL.md`.
- If creating a global Skill, prefer `%userprofile%/.trae/skills/<skill-name>/SKILL.md` on Windows.
- Use forward slashes inside Skill examples unless a Windows-only path is required by the user's actual environment.
- Keep platform wording neutral: use "Trae", "model", or "agent"; do not mention other coding agents unless the Skill explicitly integrates with them.
- If a Skill depends on Trae IDE, Trae CLI, MCP, workspace rules, or local tools, state that dependency in the body and add an eval for the missing-dependency path.
- If current docs are needed for a library, framework, SDK, API, CLI, or cloud service, fetch current documentation through the configured docs workflow before encoding details into a Skill.

### Skill Types and Scope

Use a project Skill for project-specific business rules, internal terms, architecture constraints, framework versions, test conventions, mocks, scaffolding, or project MCP/tool workflows.

Use a global Skill for reusable personal or team conventions, common tool workflows, code style, naming standards, output preferences, Git routines, CI/CD routines, or cross-project review habits.

### Creating and Importing

Trae supports three creation paths:

- Conversation-driven creation: ask Trae to create a Skill from a described need.
- Manual creation in settings: choose global or project scope, then provide name, description, and instructions.
- Manual import: import a `SKILL.md` file or a `.zip` containing `SKILL.md` plus supporting files.

When preparing a Skill for import, ensure `SKILL.md` is at the root of the folder or archive. Include only files the Skill actually needs.

### Enabling, Disabling, Editing, and Deleting

Skills can be enabled or disabled in Trae settings. When a project Skill is disabled, Trae creates or updates `.trae/skill-config.json` in the project to record disabled project Skills. Disabled global Skills are not recorded in that project file.

When editing or deleting a Skill, preserve user-created resource files unless the user explicitly asks to remove them or they are clearly obsolete for the Skill's behavior.

### Invocation

Users can invoke a Skill manually by naming it in the request, such as "use the codemap Skill to summarize this branch." Trae can also invoke a Skill automatically by matching the user request against the Skill's `description` and usage guidance.

Optimize descriptions for both paths: include the human-readable Skill purpose and the natural user phrases that should trigger automatic use.

## Refactoring Existing Skills

When improving an existing Skill:

1. Preserve the folder name and `name` unless the user explicitly asks to rename it.
2. Read `SKILL.md` first, then only the linked resources needed for the edit.
3. Identify stale platform names, unsupported commands, and ambiguous terms.
4. Remove rules that are not used by the current workflow.
5. Replace generic advice with concrete When/How/What behavior.
6. Keep useful scripts and resources, but delete or quarantine files that are platform-specific and unusable in Trae.
7. Run validation after edits.

## Anti-Pattern Checklist

Fix these before finishing:

- The Skill is only a prompt, not an executable workflow.
- `description` lacks concrete trigger contexts.
- The body contains trigger guidance that is absent from `description`.
- The Skill tries to solve multiple unrelated jobs.
- Steps use vague verbs such as handle, process, improve, or deal with.
- Inputs or outputs are implied instead of stated.
- Failure paths are missing.
- Multiple terms refer to the same concept.
- Examples use stale or platform-specific paths.
- A script can fail silently.
- The Skill includes time-sensitive details without a maintenance path.
- The Skill offers many choices without naming the default path.
- Resources are deeply nested or undiscoverable from `SKILL.md`.

## Helper Files In This Skill

- `scripts/quick_validate.py`: validate basic Skill frontmatter and naming without external Python dependencies.

Keep this Skill lean. Add new helper files only when they directly support Trae Skill creation or validation and are referenced from `SKILL.md`.

## Final Response

When finishing a Skill edit, report:

- Which files changed.
- What ambiguity or stale platform content was removed.
- What validation was run.
- Any residual risk, especially untested scripts or assumptions.
