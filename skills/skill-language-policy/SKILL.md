---
name: skill-language-policy
description: Define the repository-wide language policy for Trae Skills. Use when creating, refactoring, or reviewing Skills that need consistent rules for English machine-facing structure, retained Chinese trigger phrases, and agent-first language decisions, including Chinese requests such as skill 语言规范, Skill 中英文怎么分层, 哪些字段必须英文, 触发短语是否该保留中文, or 检查 skill 是否过度英文化.
---

# Skill Language Policy

This policy lives as a standard Skill package so it follows the same packaging and entrypoint conventions as other repository Skills. It is primarily a repository policy asset referenced by Skill creation and review workflows.

## Purpose
This policy defines the standard language rules for all Trae Skills in this repository. Its goal is to maintain a stable, predictable, and machine-readable execution environment for AI agents while preserving natural communication for Chinese-speaking users. All rules prioritize `agent-first` stability over pure human readability or internationalization.

## Do Not Use
Do not use this Skill when:
1. The task is to create, refactor, or review ordinary application code unrelated to Trae Skills.
2. The user only wants general English writing polish, translation, or copy editing without Skill packaging concerns.
3. The task is about tool/runtime debugging, repository release readiness, or code quality rather than Skill language-layer decisions.

## Asset Layers
Every file in a Skill package must be classified into one of these layers before applying language rules:
1. **`trigger asset`**: Improves auto-invocation and request matching (e.g., `SKILL.md` description, trigger examples).
2. **`execution contract`**: Defines ordered steps, inputs, outputs, success criteria, and failure handling (e.g., `SKILL.md` body).
3. **`template/prompt asset`**: Provides reusable skeletons, slots, or structured prompts the agent can fill (e.g., `*-prompt.md`, role templates).
4. **`reference asset`**: Supplies supporting patterns, deeper examples, schemas, or domain context loaded on demand.
5. **`human-oriented example`**: Shows representative behavior, primarily designed for human reading.

## English-Required Layers
The following machine-sensitive elements **MUST** be written in English or their original technical form to ensure structural stability:
1. Section headings in `SKILL.md` (e.g., `Overview`, `Use This Skill`, `Input Contract`, `Output Contract`).
2. Machine-facing output field names and structured response keys in prompts, reviewer assets, templates, scripts, and other extraction-sensitive interfaces.
3. State values and status markers (e.g., `success`, `in_progress`, `failed`).
4. CLI flags, arguments, and command names.
5. JSON keys and config keys.
6. Tool names, API names, and environment variables.
7. Structural placeholders, template slot names, and script interfaces.
8. Structural rules and keys in prompt, reviewer, or role assets.

## Chinese-Retained Layers
Chinese is allowed and preferred in the following areas to ensure natural interaction:
1. Trigger phrases and natural use cases inside the `description` frontmatter.
2. Examples of how a Chinese-speaking user would state their request.
3. User-facing conversational summaries, clarifying questions, or progress reports.
4. Short explanatory sentences that explicitly help Chinese users understand constraints or steps, provided they do not break machine readability.
5. User-facing sample values, placeholder prose, and final-delivery example content inside templates, unless a downstream parser requires a fixed English form.

## Template Output Rules
When a template appears inside `SKILL.md` or another Skill asset, review it in two layers before deciding the language:
1. **Structure layer**: Field keys, section names, slot names, and parser-sensitive markers stay in English or the original technical form when they are needed for stable execution.
2. **Rendered content layer**: Example values, helper prose, placeholder text, and direct-delivery skeleton content must follow the target user's language.
3. If a template block is meant to be delivered directly to a Chinese-speaking user, do not leave English filler such as `Chinese Name`, `Describe here`, or `As needed` inside the rendered content layer unless that English term is itself the required technical artifact.
4. Technical tokens such as tool names, protocol names, capability names, API names, and UI-aligned product terms may remain in their original form inside otherwise Chinese output when translation would reduce precision.

## Migration Strategy
1. **Rule First**: This policy applies immediately to all newly created Skills and assets.
2. **Incremental Migration**: Legacy files should be migrated progressively when they are touched for other reasons, rather than through massive, disruptive rewrites.
3. **Execution Chain Priority**: Core execution-chain Skills (e.g., `executing-plans`, `workflow-runner`) must be migrated first to establish stable templates.
4. **Structure Before Language**: If a file needs both structural simplification and language unification, stabilize the structure (inputs, outputs, boundaries) before rewriting the language.
5. **First-Round Exemptions**: `examples/`, most `references/`, and human-oriented Chinese sample documents are not required to be translated to English in the first migration pass.

## Review Rules
When reviewing Skills (e.g., via `skill-stability-review`), apply these standards:
1. Do not flag a file as defective simply because it contains "too much Chinese".
2. Flag an issue **only** if:
   - Section headings in `SKILL.md` are not unified in English.
   - Machine-sensitive layers (JSON keys, CLI flags, machine-facing output fields) use Chinese.
   - Prompt/reviewer assets contain structural Chinese keys.
   - User-facing delivery templates keep English placeholder prose or sample values where Chinese should be used.
   - Direct-delivery tables or helper copy use English state words without a parser or product-term reason.
   - The `description` is missing Chinese trigger phrases.
3. Reviewers must verify that language unification does not blur the execution contract, weaken failure handling, or accidentally remove valid Chinese triggers.
