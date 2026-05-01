---
name: systematic-debugging
description: Use when debugging bugs, test failures, build breaks, performance regressions, or unclear behavior before proposing a fix, including Chinese requests such as “逐步排查”“为什么失败”“先定位原因”“不要先猜修复”. Do not use for straightforward implementation tasks, pure document edits, or issues that already have a confirmed root cause and only need mechanical changes.
---

# Systematic Debugging

## Overview

Proposing a fix directly without evidence usually just buries the symptom deeper. Use this skill to break debugging into an executable chain: collect evidence first, form a hypothesis, and only then fix the root cause.

**Core Principle:** No fix proposals until the root cause investigation is complete.

## Use This Skill

- The user reports a bug, test failure, build break, abnormal behavior, or performance issue.
- You have already tried 1-2 fixes but the issue is not stably resolved.
- The issue spans multiple components, scripts, services, threads, or async boundaries.
- The user asks to "debug step by step", "locate the cause first", or "don't guess the fix".

## Do Not Use

- The user just wants you to implement a clear feature, with no abnormal or failing symptoms.
- The user is asking for a normal code review; prioritize `requesting-code-review` or the environment's code review process.
- The issue is already clear enough that only mechanical changes remain, needing no debugging.
- The failure is a Chrome DevTools MCP connection, startup, or missing tool issue; prioritize `troubleshooting`.

## Input Contract

**Required Inputs:**
- At least one observable symptom, such as an error message, failing test, abnormal behavior, performance degradation, or build failure.

**Optional but highly recommended inputs:**
- Reproduction steps.
- Error logs, stack traces, exit codes.
- Recent changes, environment differences, config differences.
- Expected behavior vs. actual behavior.

**Missing input handling:**
- **Symptoms insufficient to judge the issue**: Clarify the phenomenon first; do not modify code directly.
- **Unable to reproduce stably**: Prioritize adding observation points and finding the minimal reproduction path.
- **Only "please fix it" without failure evidence**: Collect evidence first, then decide whether to enter the fix phase.

## Execution Protocol

### 1. Read the Symptom

Read the phenomenon itself completely first:
- Error messages, stack traces, failing test names, exit codes.
- Time of first occurrence and trigger conditions.
- Whether it reproduces stably.
- Recent code, config, dependency, or environment changes.

If the symptom is unclear, clarify it. Do not start fixing.

### 2. Reproduce Stably

The goal is not "I saw the error once", but "I know how to trigger it again".
- Record minimal reproduction steps.
- Narrow down inputs, scope, and target files as much as possible.
- If it cannot be reproduced stably, continue adding logs and observation points instead of changing code directly.

### 3. Establish Evidence Chain

Record inputs, outputs, and state for each suspicious boundary:
- What was received before entering the component.
- What was produced after leaving the component.
- Whether environment variables, configs, thread states, and network results are passed correctly.
- At which layer it starts deviating from expectations.

Multi-layer system example:
```powershell
Write-Host "=== Workflow layer ==="
Write-Host ("IDENTITY: " + ($(if ($env:IDENTITY) { "SET" } else { "UNSET" })))

Write-Host "=== Build script layer ==="
Get-ChildItem Env:IDENTITY -ErrorAction SilentlyContinue

Write-Host "=== Signing step ==="
& codesign --sign $env:IDENTITY --verbose=4 $env:APP
```

### 4. Compare with Normal Path

Find a "working similar implementation" first, then compare differences:
- Normal tests, commands, or modules in the same repository.
- Reference implementations under the same pattern.
- Differences in dependencies, initialization order, config values, or boundary conditions.

Do not just say "it looks about the same here" based on intuition.

### 5. Propose a Single Hypothesis

Keep only one root cause hypothesis at a time, formatted as explicitly as possible:
```text
I believe X is the root cause because Y; if this judgment is correct, then minimal validation should show Z.
```
Then do only one minimal validation. Do not stack multiple fixes simultaneously.

### 6. Write Failing Validation First, Then Fix

Once the root cause is clear:
- Prioritize writing a failing test or minimal reproduction script.
- Fix only the root cause; do not refactor unrelated things along the way.
- Re-run the reproduction path and related tests after the fix.

This step should integrate with `test-driven-development`.

### 7. Fallback on Fix Failure

- 1st validation failure: Update hypothesis, return to Step 3.
- 2nd validation failure: Expand evidence scope, re-check the call chain.
- 3rd validation failure: Stop "trying one more time", start questioning the architecture or approach itself.

## Trae / Windows Conventions

- In Trae, prioritize using `Read`, `Grep`, `SearchCodebase`, `GetDiagnostics`, and `RunCommand` to collect evidence.
- When these tools fail due to MCP unavailability, refer to `environment-resilience` rule for the graceful MCP degradation chain (retry → terminal fallback → report).
- When a command fails due to port conflicts or zombie processes, refer to `port-conflict-recovery` rule (identify → kill → verify → retry).
- When running commands on a Windows host, use PowerShell-compatible syntax; only use POSIX syntax when the command explicitly runs inside a container, remote Linux, or WSL.
- When needing to clarify reproduction steps, input conditions, or environment differences, use structured questions in the current environment instead of guessing.
- If a fix needs to be implemented later, switch to `test-driven-development`; if preparing to declare it fixed, switch to `verification-before-completion`.

## Red Lines

If you see these thoughts, return to the investigation phase immediately:
- "Let's fix it temporarily first, and look at it later."
- "I guess the problem is here, let's change it and see."
- "Let's change several places at once and run the tests."
- "Skip the tests, let's click manually to see."
- "Although I don't understand it yet, this change will probably work."
- "Let's try one more time" when you have already tried more than twice.

## Failure Handling

- **Cannot reproduce**: Add logs, state outputs, or minimize inputs; do not fix directly.
- **Missing context**: Confirm environment, data, commands, and expected behavior with the user.
- **External dependencies unstable**: Explicitly mark dependency risks and isolate locally verifiable parts.
- **More than three fix attempts fail**: Stop patching locally and switch to an architectural discussion.

## Output Contract

After completing the debugging phase, the output must contain at least:
- Phenomenon: What exactly failed.
- Evidence: What logs, command outputs, or code differences you saw.
- Root Cause Hypothesis: What is the most credible cause currently.
- Validation: How you prove or disprove this hypothesis.
- Next Steps: Enter fix, continue collecting evidence, or request clarification.

Use this fixed skeleton by default:

```markdown
调试阶段已完成。

**Phenomenon:**
- [What failed]

**Evidence:**
- [Logs / command outputs / code diffs]

**Most Credible Root Cause Hypothesis:**
- [If not yet located, write `- Not yet located`]

**Validation Actions:**
- [How to prove or disprove]

**Next Steps:**
- [If verified: Enter `test-driven-development` for high-risk fixes, or `executing-plans` for straightforward changes / If unverified: Propose next diagnostic step / If blocked: Ask for missing context]
```

If the root cause is not yet located, do not conclude with "应该这样修复".

> **Context Payload (for downstream handoff)**
>
> When handing off to the next skill (e.g., `test-driven-development`, `executing-plans`), append this context block to the output. It preserves the debugging journey so the fix agent does not lose prior context:
>
> ```markdown
> **[Context Payload]**
> **Phenomenon:** [What exactly failed]
> **Root Cause:** [Confirmed hypothesis or "not yet located"]
> **Ruled Out:** [What was investigated and discarded, to avoid repeat work]
> **Evidence Collected:** [Logs, command outputs, code diffs — or paths to them]
> **Residual Risk:** [What is still uncertain, what edge cases remain]
> **Affected Components:** [Files, services, or layers involved]
> **Fix Guidance:** [One-sentence summary of what needs to change]
> ```

If the root cause is non-obvious or the debugging uncovered a subtle system behavior, invoke `self-improvement` to log the finding as a `knowledge_gap` or `insight` before exiting. This prevents future agents from repeating the same investigation.

## Resources

- `root-cause-tracing.md`: Tracing the source of the problem backward along the call stack.
- `defense-in-depth.md`: How to add layered validation after the root cause is confirmed.
- `condition-based-waiting.md`: Replacing hardcoded sleeps with condition-based waiting.
- `condition-based-waiting-example.ts`: Reference implementation of condition-based waiting.

## Integration

- `test-driven-development`: Establish a failing test for the bug and drive the fix.
- `executing-plans`: Downstream — for straightforward fixes where the root cause is clear and no complex implementation plan is needed.
- `writing-plans`: Downstream — for complex root cause fixes that need architectural design or multi-step planning before execution.
- `verification-before-completion`: Downstream — re-verify whether the conclusion is supported by evidence after fixing.
