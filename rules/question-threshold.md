---
alwaysApply: true
description: Use when deciding whether to ask the user a question or deduce from context. Overrides the default "deduce and proceed" behavior. Defines when to ask, when not to ask, and how to ask.
---

# Question Threshold

This rule overrides the system prompt's "deduce and proceed" default. When the current task hits one of the MUST Ask scenarios, stop and use `AskUserQuestion`. Otherwise, deduce from context and proceed.

## MUST Ask

- **Ambiguous intent**: The request has two or more materially different valid interpretations, and the codebase contains no signal to disambiguate.
- **Unknown external dependency**: The request references a technology, tool, or external service not found in the codebase, project config, or documented conventions.
- **Unclear scope**: The request has no explicit boundary (e.g., "fix performance" without target metrics).
- **Out-of-project target**: The task would modify files outside the current project scope that the user did not mention.
- **Business knowledge required**: The answer depends on product/domain knowledge not documented in the codebase and not inferable from usage patterns.

## MUST NOT Ask

- **Answer is in the codebase**: File structure, imports, patterns, tests, or config contain the answer.
- **Single valid path**: Only one reasonable implementation approach exists.
- **Trivially reversible**: Wrong choice can be undone with one edit and has no side effects.
- **Convention-following**: The answer follows from the project's established patterns.
- **User already provided context**: The request already contains enough information.

## How to Ask

When you MUST ask, follow this format:
1. State what you know so far.
2. State exactly what is ambiguous and why the codebase cannot resolve it.
3. Present 2-3 concrete options with trade-offs.
4. Ask one question at a time.
5. Do not ask about codebase facts that are visible by reading the code.
