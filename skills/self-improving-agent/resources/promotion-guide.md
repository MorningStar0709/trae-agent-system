# Promotion Guide

Manage the lifecycle of learnings: from initial capture to permanent project knowledge.

## Lifecycle Overview

```text
Logged → Resolved → Promoted (to Rule / Skill / Core Memory update)
```

## Priority Guidelines

| Priority | When to Use |
|----------|-------------|
| `critical` | Blocks core functionality, data loss risk, security issue |
| `high` | Significant impact, affects common workflows, recurring issue |
| `medium` | Moderate impact, workaround exists |
| `low` | Minor convenience, edge case |

## Deduplication: Check Before Logging

Before creating a new learning entry, search existing Core Memory:

- **Similar exists** → Use `UPDATE` to merge, don't create duplicate
- **Same pattern 3+ times** → Flag for promotion to Rule (systemic issue)
- **Recurring without fix** → Log but mark as needing permanent resolution

## When to Promote

A learning qualifies for promotion when ALL are true:

| Criterion | Check |
|-----------|-------|
| Applies across multiple files/features | ☐ |
| Any contributor (human or AI) should know this | ☐ |
| Prevents recurring mistakes | ☐ |
| Documents project-specific conventions | ☐ |

### Promotion Targets

| Target | What Belongs There |
|--------|-------------------|
| Core Memory (UPDATE existing) | Quick-reference rules, personal habits |
| `.trae/rules/<name>.md` | Auto-triggering conventions for specific file types |
| New Skill | Multi-step workflows that need strict execution steps |

### Promotion Process

1. **Distill** the learning into a concise, actionable rule
2. **Add** to the appropriate target
3. **Update** the original entry status (if Core Memory, UPDATE with resolved info)
4. **Reference**: add `via` field linking back to the original learning

## Low-Value Filter

Skip logging entirely if:

- The learning is trivial/common knowledge
- It's a transient environment issue unlikely to recur
- The correction doesn't change how future work is approached
