---
name: test-driven-development
description: Use when implementing behavior with tests first, including new features, bug fixes, behavior changes, and regression protection, and including Chinese requests such as “先写测试”“补回归”“按 TDD 修复”. Do not use for pure copy edits, generated outputs with little test value, or tasks where the user explicitly wants to skip testing and accepts the risk.
---

# Test-Driven Development

## Overview

TDD is not "adding tests at the end", but defining behavior with a failing test first, then satisfying it with minimal implementation. The goal of this skill is to reduce regression risk and keep implementation aligned with requirements.

**Core Principle:** If you don't see the test fail first, you don't know if it's actually protecting the correct behavior.

## Use This Skill

- Developing new features.
- Fixing bugs and adding regression protection.
- Changing existing behavior.
- Adding safety nets to legacy code lacking tests.

## Do Not Use

- Only modifying copy, comments, or static configs without behavioral changes.
- Generating files or third-party artifacts with very low testing value.
- The user explicitly asks to skip testing and accepts the corresponding risk.
- The current task is just discussing solutions; use `brainstorming` or `writing-plans` first.

## Input Contract

**Required Inputs:**
- A clear behavioral target: what behavior needs to be implemented, fixed, or changed.

**Optional but highly recommended inputs:**
- Existing project testing patterns and framework configuration.
- Related test files or code paths.
- **Context Payload from upstream skill (e.g., `systematic-debugging`, `writing-plans`)**: When handed off from an upstream skill, check the conversation for a `[Context Payload]` block. It preserves the confirmed root cause, ruled-out paths, residual risks, and fix guidance that should inform the failing test design.

**Missing input handling:**
- **Behavioral target unclear**: Do not start the TDD loop; clarify first.
- **Context Payload available**: Read it during Phase 0 before writing the failing test.
- **Context Payload absent**: Proceed without it.

## Execution Protocol

### Phase 0: Read Upstream Context (if handed off from upstream skill)

If the current task was handed off from an upstream skill (e.g., `systematic-debugging`), check the conversation for a `[Context Payload]` block before starting the TDD loop. Pay special attention to these fields:

- **Root Cause** (from `systematic-debugging`): Confirmed root cause that the fix must address.
- **Ruled Out** (from `systematic-debugging`): What was already investigated — avoid repeating dead ends.
- **Residual Risk** (from `systematic-debugging`): Edge cases or uncertainties that the TDD regression test should cover.
- **Fix Guidance** (from `systematic-debugging`): One-sentence summary of what needs to change.

If a Context Payload is present, incorporate its content into the failing test design and implementation scope. If absent, proceed without it.

### 1. Red Light: Write Failing Test First

The test must first express the expected behavior, then expose the current gap.

A good failing test should:
- Test only one behavior at a time.
- Have a clear name.
- Prioritize testing real behavior, not the mock itself.
- Be minimally reproducible.

Example:
```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = async () => {
    attempts += 1;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```

### 2. Verify Red Light: Must See It Fail

Use PowerShell-compatible commands on a Windows host, for example:
```powershell
npm test -- path\to\retry.test.ts
```
Or:
```powershell
pytest tests/test_retry.py -k retries_failed_operations
```

Confirm three things:
- The test fails, not the test file itself throwing a syntax/load error.
- The failure reason matches expectations.
- The failure comes from missing behavior, not typos or environment errors.

If the test passes immediately upon writing, it means it is not protecting the actual new behavior.

### 3. Green Light: Write Minimal Implementation

Write only the minimum code required to make the current failing test pass. Do not opportunistically expand interfaces or optimize unrelated logic.

Example:
```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i += 1) {
    try {
      return await fn();
    } catch (error) {
      if (i === 2) throw error;
    }
  }

  throw new Error('unreachable');
}
```

### 4. Verify Green Light: Re-run Tests

Run the exact same test command again and confirm:
- The target test passes.
- Related tests do not regress.
- The output has no new errors or obvious warnings.

### 5. Mutation Test: Break Then Verify (Anti-False-Green)

Deliberately alter one line of the implementation code you just wrote to prove the test can catch the defect.

Rules:
- Only alter implementation code, not test code.
- Make a targeted, minimal break (e.g., flip a boolean, remove a guard clause, return a wrong value, comment out a key line).
- Do not break code unrelated to what the test is verifying.
- Re-run the exact same test and confirm it **fails** with a meaningful error.
- Restore the broken code immediately after verification.

If the test does not fail under mutation, the test is **not protective** — it is a false-green test. In that case:
1. Fix the test to actually assert meaningful behavior.
2. Repeat the mutation test until the test fails when the implementation is broken.
3. If you cannot make the test fail under mutation, escalate: this likely means the code cannot fail from the outside, which is a design issue.
4. **Log via `self-improvement`**: Record the false-green pattern as an anti-pattern experience so future agents can recognize and avoid similar testing mistakes.

Example mutation sequence for a validation function:
```typescript
// Original implementation:
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: 'Email required' };
  }
  return { ok: true };
}

// Mutation: comment out the guard
function submitForm(data: FormData) {
  // if (!data.email?.trim()) {
  //   return { error: 'Email required' };
  // }
  return { ok: true };
}

// Run test → expect FAIL with meaningful error
// Then restore immediately
```

### 6. Refactor: Only After Mutation Passes

You are only allowed to do these when the tests are green:
- Deduplicate code.
- Rename variables/functions.
- Extract helper functions.
- Simplify structures.

After refactoring, you must run the tests again to ensure behavior remains unchanged.

## Bug Fix Pattern

When fixing a bug, write the bug as a failing test first, instead of fixing the implementation directly.

```typescript
test('rejects empty email', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('Email required');
});
```

Run it to get a red light, then fix:

```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: 'Email required' };
  }

  return { ok: true };
}
```

## Trae / Windows Conventions

- In Trae, use `Read`, `Grep`, `GetDiagnostics` to understand existing testing patterns before writing new tests.
- When running validations, use the project's native test commands and maintain PowerShell compatibility on the Windows host.
- Do only one thing per cycle: write failing test, run it, write minimal implementation, run it again, perform mutation test, restore, then refactor.
- After the fix is complete, if preparing to declare success, continue using `verification-before-completion`.

## Common Anti-Patterns

- Write code first, add tests at the end.
- The test passes as soon as it is written.
- Testing the number of mock calls instead of behavioral results.
- Modifying production code to be harder to understand just to make it easier to test.
- Writing a lot of implementation at once, then going back to add a bunch of tests.

See more anti-patterns in: `testing-anti-patterns.md`

## Failure Handling

- **Test won't stably fail**: Fix the test environment or minimal reproduction first; do not enter implementation.
- **Test is too hard to write**: Usually indicates the interface design is too heavy or tightly coupled; simplify the design first.
- **Requires massive mocking to test**: Prioritize checking dependency injection, boundary splitting, and responsibility separation.
- **Existing code lacks tests**: Start from the behavior being modified; add minimal regression tests first.

## Output Contract

When completing a TDD cycle, you must at least state:
- Which test was added or modified.
- What failure was seen during the red light phase.
- What minimal implementation was used to make it green.
- What validations were run at the end.
- What mutation test was performed to verify test protection.

If there is no evidence of a red light, do not claim you did TDD.

**Next Step:** After the TDD cycle is complete, must invoke `verification-before-completion` to independently verify the fix before declaring "fixed" or entering the commit process.

## Checklist

- [ ] Wrote a failing test first.
- [ ] Saw the test fail for the expected reason with my own eyes.
- [ ] Wrote only the minimal implementation to pass the test.
- [ ] Re-ran the test and confirmed it passed.
- [ ] Related tests did not regress.
- [ ] Performed mutation test: broke implementation and confirmed test failure.
- [ ] Restored implementation after mutation verification.
- [ ] If refactored, verified again after refactoring.

## Integration

- `systematic-debugging`: Locate the root cause first, then return to TDD to fix.
- `verification-before-completion`: Re-verify conclusions before claiming "fixed".