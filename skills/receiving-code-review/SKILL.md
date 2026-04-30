---
name: receiving-code-review
description: Use when you already have code review feedback and need to validate, clarify, and apply it safely, including Chinese requests such as “这些 review 意见怎么处理”“收到审查反馈后怎么落地”“先别急着改，帮我判断哪些该修”. Do not use when no review feedback exists yet, or when the task is ordinary code review rather than responding to comments.
---

# Receiving Code Review

## Overview

Use this skill to handle the "what to do after a review" phase. The focus is not on polite acknowledgment, but on translating feedback into technical judgments, clarifying questions, and orderly implementation.

**Core Principle:** Validate feedback first, then decide whether to implement it.

## Use This Skill

- You have already received code review feedback.
- The feedback contains multiple modification suggestions.
- Some suggestions are unclear, or you suspect they might introduce regressions.
- You need to distinguish what must be fixed, what can be refuted, and what needs clarification first.

## Do Not Use

- There are no review results yet; use `requesting-code-review` first.
- The user just wants a normal code review, rather than processing feedback.
- The current task is implementing a feature from scratch, not responding to review comments.

## Execution Protocol

### 1. Read Feedback Completely First

Do not start modifying code upon seeing the first comment. First confirm:
- How many feedback items there are in total.
- Which ones are blocking issues.
- Which ones are unclear.
- Which ones might be related to each other.

### 2. Reiterate Technical Understanding

If there are multiple feedback items, clarify your understanding of the scope before acting:
```text
I understand items 1, 2, and 3 are...
The scope of items 4 and 5 is not clear enough and needs confirmation first.
```

### 3. Validate If Feedback Is Valid

Check each item:
- Does the codebase currently actually have this problem?
- Is the suggested fix suitable for the current tech stack and existing constraints?
- Will it break existing behavior, compatibility, or architectural decisions?
- Is it just "looks more standard" but actually unneeded by anyone?

### 4. Categorize Handling

- **Clear and correct**: Implement directly.
- **Unclear**: Clarify first, then implement.
- **Technically invalid**: Provide evidence to refute.
- **Trade-off needed**: Confirm the direction with the user before proceeding.

## Handling Unclear Feedback

If you cannot accurately explain the meaning of a piece of feedback, do not start modifying it.

**Incorrect approach:**
- Modify what you understand first, and guess the rest as you go.

**Correct approach:**
- Point out which items are understood.
- Explicitly list which items need clarification.
- Wait for clarification before advancing as a whole.

## When To Refute

You should refute or request further justification when:
- The suggestion would break existing functionality.
- The reviewer lacks context.
- The suggestion violates YAGNI, and no one in the codebase uses it.
- The current implementation is limited by compatibility, platform, or historical constraints.
- It conflicts with established architectural decisions.

When refuting, provide:
- Specific file or implementation evidence.
- Existing tests or behavioral proof.
- Alternative solutions or specific questions.

## Implementation Order

When there are multiple feedback items, recommended order:
1. Blocking issues.
2. Clear and small fixes.
3. Complex logic or refactoring items.
4. Style and maintainability items.

Re-validate between each item; do not pile up many changes at once.

## Trae / Windows Conventions

- When processing feedback, prioritize using `Read`, `Grep`, `SearchCodebase`, `GetDiagnostics`, and necessary validation commands to verify facts.
- When needing to clarify multiple feedback items with the user or partner, prioritize using structured, concise questions instead of guessing while doing.
- Re-validate every time you fix an item; if you finally want to declare it "fixed", go through `verification-before-completion`.

## Failure Handling

- **Unable to validate a piece of feedback**: Explicitly state the missing context or dependency.
- **Feedback items conflict with each other**: Stop and request the user to determine priority.
- **You initially refuted, but later realized you were wrong**: Directly admit the validation result and start fixing; do not make long excuses.
- **Fixing one item introduces a new problem**: Return to the validation phase, confirm if the scope needs to be expanded.

## Output Contract

When processing feedback, the output must at least contain:
- Which feedback items you understood.
- Which items have been validated as true.
- Which items still need clarification.
- Which items you plan to implement or refute.
- Once all feedback items are resolved, must invoke `verification-before-completion` to re-verify before declaring "fixed".

## Integration

- `requesting-code-review`: Initiates the independent review.
- `verification-before-completion`: Performs final validation after feedback is fixed.

## Bottom Line

Code review feedback is technical input to be validated, not an absolute command that must be blindly followed.