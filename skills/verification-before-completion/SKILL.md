---
name: verification-before-completion
description: Use before claiming work is done, fixed, tested, ready to commit, or ready to merge, including Chinese requests such as “确认真的修好了”“提交前再验证一下”“不要没跑就说完成”. Re-run the proving checks and report the real status from exit codes and output. Do not use while work is still exploratory or when no completion claim is being made.
---

# Verification Before Completion

## Overview

Use this skill to enforce an evidence threshold before claiming "done", "fixed", or "ready to commit". Whenever you are about to express a success state, you must first run the validation corresponding to that conclusion.

**Core Principle:** No fresh evidence, no claiming success.

## Use This Skill

- You are about to say "done", "fixed", or "tests passed".
- You are preparing to commit, create a PR, merge a branch, or finish a task.
- A subagent, script, or automated process claims it has succeeded.
- You need to convert "looks fine" into a verifiable conclusion.

## Do Not Use

- You are still in the middle of troubleshooting or implementation, with no conclusion to claim yet.
- The user is only asking for ideas, approaches, or risks, rather than requesting confirmation of results.
- You currently cannot run any validation, and you are just explaining risks or blockers upfront.

## Execution Protocol

### 1. Define What to Prove First

Before expressing a conclusion, ask yourself:
- Am I trying to prove "tests passed" or "build succeeded"?
- To prove "bug is fixed", what is the minimal validation path?
- To prove "requirement met", is there an item-by-item checklist?

### 2. Run the Corresponding Validation

Validation must map 1:1 to the conclusion:
- "Tests passed" -> Re-run the relevant tests.
- "Build succeeded" -> Re-run the build.
- "Bug fixed" -> Re-run the original reproduction path.
- "Requirement met" -> Verify against the checklist item by item.
- "Subagent is done" -> Check the changes yourself and re-verify the results.

### 3. Read the Full Results

Do not just look at the last line or the exit code.
Confirm at least:
- Did the command execute completely?
- Is the exit code correct?
- Do the failure, error, and skip counts match expectations?
- Are there hidden exceptions, warnings, or environment issues in the output?

### 4. Write Conclusion Based on Evidence

- If the evidence supports the conclusion, explicitly state the scope of success.
- If the evidence does not support it, honestly report failure, partial pass, or unverified.
- If you can only verify a part, do not write partial success as overall success.

## Common Mappings

| Conclusion | Acceptable Evidence | Unacceptable Evidence |
|---|---|---|
| Tests passed | Re-ran tests and saw passing results | Ran them earlier, guess they should pass |
| Build succeeded | Re-ran build and got exit 0 | Linter passed, logs look like a success |
| Bug fixed | Original reproduction path now passes | Changed code but didn't verify reproduction |
| Ready to commit | Relevant validations finished with clear results | "Small change, let's just commit it" |
| Subagent done | Reviewed diff yourself and re-verified | Only read the subagent's verbal report |

## Trae / Windows Conventions

- In Trae, use `RunCommand`, `GetDiagnostics`, `Read`, and necessary testing tools to collect evidence.
- Use PowerShell-compatible syntax for Windows host commands; do not execute Unix examples directly as host commands.
- If validation relies on subagents, browsers, external services, or local tools, explicitly state which evidence was actually run and which are just static checks.
- If validation is not complete, do not use vague wording to package it as a success.

## Red Lines

- "It should be fine now."
- "Probably no issues."
- "I am very confident."
- Saying "It's done" before validating.
- Announcing overall completion after only partial checks.
- Trusting subagents, scripts, or historical results without re-verifying.

## Failure Handling

- **Validation failed**: Report the real failure information; do not downplay it as "mostly done". If the failure reveals a non-obvious root cause, environment quirk, or configuration issue that future agents may encounter again, invoke `self-improvement` to log it as an `Experience` before moving on.
- **Unable to run validation**: Explicitly state the blocker, missing dependencies, and the currently unverified scope.
- **Only partially verified**: Restrict the conclusion to the verified scope.
- **External dependency unavailable**: Distinguish between "local static checks passed" and "end-to-end unverified".

## Output Contract

When wrapping up with this skill, the output must contain at least:
- What was verified.
- What commands or checks were used.
- What the key results were.
- What the boundaries of the conclusion are.

Example:
```text
Re-ran relevant tests and confirmed they passed:
- `npm test -- src/auth/auth.test.ts`
- Result: 12 passing, 0 failing

Therefore, I can only confirm the auth module changes passed this test scope; the full test suite was not re-run.
```

## Integration

- `test-driven-development`: Handles the red-green loop; this skill handles the evidence check before the final claim.
- `systematic-debugging`: Handles finding the root cause; this skill confirms the result after fixing.
- `git-commit`: Finish the validations here before committing; do not reverse the order.
- `finishing-a-development-branch`: Downstream — after verification passes, use finishing-a-development-branch for wrap-up (merge, PR, keep, or discard).
- `requesting-code-review`: Downstream — after verification, opt into code review before merging.

## Bottom Line

Validation is not a rhetorical action; it is an evidence-gathering action.
Run first. Read second. Conclude last.