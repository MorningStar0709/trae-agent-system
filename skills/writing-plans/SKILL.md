---
name: writing-plans
description: Use when you need to turn a clear spec, approved design, or stable requirement into an executable multi-step implementation plan before coding, including Chinese requests such as “写实现计划”“拆任务”“先规划再写代码”. It is especially suitable for handing off a brainstorming result into file-level tasks, tests, and validation steps. Do not use when requirements are still unclear, the change is small enough to implement directly, or you are already executing an existing plan.
---

# Writing Plans

## Overview

Write execution-oriented implementation plans, assuming by default that the downstream executor has near-zero prior knowledge of the current codebase and domain context. The plan must explicitly state file scopes, implementation boundaries, testing paths, validation commands, expected results, and necessary handoff information. Break the work into independently executable, small-step tasks, minimizing guesswork during execution. Follow DRY, YAGNI, TDD, and frequent commits.

Assume the executor has general development skills but does not know repository conventions, local architecture, or testing habits. Therefore, key constraints, interface names, testing entry points, and validation criteria should be written explicitly in the plan, rather than relying on the executor to deduce them.

## Use This Skill

- A relatively stable spec, design conclusion, or clear requirement exists, and needs to be translated into an executable multi-step plan.
- The task is complex enough to warrant defining file structures, phase boundaries, validation methods, and commit rhythms upfront.
- You anticipate handing the plan off to `executing-plans` or `subagent-driven-development` and want it complete beforehand.
- The user requests "write an implementation plan", "break down tasks", "give me executable steps", or "plan first before coding".

## Do Not Use

- Requirements are still vague or solutions undecided; use `brainstorming` first to clarify.
- The task is a simple single-point change, copy adjustment, config fix, or small bugfix; implement it directly.
- The current step is already executing an existing plan, not generating a new one; use `executing-plans` or `subagent-driven-development`.
- The user only wants a high-level summary, milestone list, or casual advice, rather than an execution plan with file/test/command details.

## Input Contract

**Required Inputs:**
- A relatively stable spec, design conclusion, or clear requirement.
- The target scope the plan should cover (not just a vague direction).

**Optional but highly recommended inputs:**
- Relevant code paths, module names, existing entry points.
- Completed `brainstorming` conclusions.
- Technical constraints, non-functional requirements, compatibility requirements.
- User-preferred plan save location.

**Missing input handling:**
- **Requirements still exploratory**: Do not generate a plan; switch to `brainstorming`.
- **Only partial requirements stable**: Explicitly list missing items first, then generate a plan only for the confirmed scope.
- **Missing paths/modules/context but planning is possible**: Write "code area to be read/confirmed" in the plan, but do not use placeholders for core implementation decisions.

**Plan Save Location:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- (User preference overrides this default)

**Validation Assets:**
- evals: `evals/evals.json`
- examples: `examples/input.md`, `examples/output.md`
- review template: `plan-document-reviewer-prompt.md`

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If not, recommend splitting them into separate plans—one per subsystem. Each plan should independently yield working, testable software.

## Execution Protocol

Generate the plan in the following order; do not skip steps:

1. Confirm whether a plan is genuinely needed, rather than direct implementation or further clarification.
2. Extract goals, boundaries, constraints, existing code entry points, and validation requirements.
3. List the file structure and responsibilities before breaking down tasks.
4. Output prerequisites, completion signals, steps, tests, and validations per task.
5. Self-check for spec coverage, placeholders, and type consistency.
6. Save the plan and provide execution recommendations.

If any step is blocked, explicitly state the block reason in the final reply. Do not pretend the plan is complete.

## File Structure

Before defining tasks, list the files to be created or modified and the responsibility of each. This is where you lock in breakdown decisions and reduce execution ambiguity.

- Units with clear design boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code that fits in context at once; the more focused the file, the more reliable your edits. Prefer small, focused files over large, monolithic ones.
- Files that change together should be grouped together. Split by responsibility, not technical layers.
- Follow existing patterns in the codebase. If it uses large files, do not unilaterally refactor—but if the file you are modifying has become unmanageable, including a split in the plan is reasonable.

This structure determines the task breakdown. Each task should produce independent, meaningful changes, allowing downstream skills to advance directly along file boundaries.

## Granularity of Tasks

Default granularity rules:
- One step does one type of action: write tests, run validation, modify implementation, update docs, commit changes.
- If a step requires modifying multiple loosely coupled files simultaneously, split it into multiple steps or tasks.
- If a step depends on the output of a previous step to clarify its content, write that dependency into the step description.
- When a task is complete, it should yield a verifiable, staged result.

## Plan Document Header

**Every plan must start with this header:**

```markdown
# [特性名称] 实现计划

> **For AI Agent Workers:** Prioritize using `subagent-driven-development` (when the environment supports implementation subagents and tasks are mostly independent) or `executing-plans` (when sequential execution in the current session is needed or implementation subagents are unsupported) to implement this plan task by task. Use checkbox (`- [ ]`) syntax to track progress.

**目标:** [用一句话描述要构建的内容]

**架构:** [用 2-3 句话描述技术方案或结构]

**技术栈:** [列出关键技术/库]

---
```

## Task Structure

````markdown
### 任务 N: [组件或模块名称]

**文件:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py` (必要时补充符号/函数/模块锚点)
- Test: `tests/exact/path/to/test.py`

**前置条件:**
- [如果没有，请写 "无"]

**完成标准:**
- [描述任务完成时的可观测结果]

- [ ] **Step 1: Write failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test and verify failure**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL, error "function not defined"

- [ ] **Step 3: Write minimal implementation code**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test and verify success**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```powershell
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

**Task Writing Rules:**
- Default to exact file paths; supplement with stable anchors (symbols, classes, functions, routes, config keys) when necessary. Do not rely on fragile line numbers.
- Only use code blocks for: new test cases, interface contracts, complex implementation snippets, easily misunderstood data structures, key config content.
- For simple mechanical changes, use "modification point + constraint + validation command" instead of full code blocks to avoid drowning the plan in low-value boilerplate.
- Every task must explicitly state completion signals so the executor knows when it is done.

## No Placeholders

Every step must contain the actual content an engineer needs. The following are **plan defects**—never write them:
- "TBD", "TODO", "Implement later", "Add details"
- "Add appropriate error handling" / "Add validation" / "Handle edge cases"
- "Write tests for the above code" (without actual test code)
- "Similar to Task N" (repeated code—engineers may not read tasks in order)
- Steps that describe what to do without showing how (code steps must have code blocks)
- Referencing types, functions, or methods not defined in any task

**Exception — Intentional Pending**: When an interface, dependency, or API contract genuinely cannot be finalized until a later task completes, you may mark it as `**Pending**: determined by Task N output`. This is not a TODO gap — it is an explicit dependency declaration. The downstream task must resolve the pending item before its own completion.

## Notes
- Always use exact file paths.
- Prioritize exact paths, stable anchors, validation commands, and expected results; include key code snippets only when necessary.
- Exact commands and expected outputs.
- DRY, YAGNI, TDD, frequent commits.

## Self-Check

After writing the complete plan, review the spec with fresh eyes and check the plan against it. This is a checklist you execute yourself—not a subagent dispatch.

**1. Spec Coverage:** Skim every section/requirement in the spec. Can you point to the task that implements it? List any omissions.

**2. Placeholder Scan:** Search the plan for red flags—any pattern from the "No Placeholders" section above. Fix them.

**3. Type Consistency:** Do the types, method signatures, and property names used in later tasks match those defined in earlier tasks? Calling it `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline directly. No need to re-review—fix and continue. If you find requirements in the spec without a corresponding task, add the task.

## Output Contract

The final output must include at least:
- Plan file save path
- Goals, architecture, and tech stack within the plan
- File structure and responsibility boundaries
- Task list, each task containing files, prerequisites, completion signals, steps, and validation
- Explicit execution recommendations

The final reply must use this skeleton by default:

```markdown
计划已完成并保存到 `<plan-path>`。

**计划摘要:**
- 目标: [一句话描述]
- 任务数: [N]
- 关键文件: [2-5 个最重要的路径]

**推荐执行方式:** `subagent-driven-development` | `executing-plans`
**原因:** [基于环境能力和任务耦合度的 1-2 句话说明]
**替代方案:** `subagent-driven-development` | `executing-plans`
**下一步:** [直接说明接下来应调用哪个技能]
```

If the plan is incomplete, do not use the phrasing "计划已完成并保存到 `<plan-path>`。"; explicitly state the reasons for incompletion and missing conditions.

> **Context Payload (for downstream handoff)**
>
> When handing off to the next skill (e.g., `executing-plans`, `subagent-driven-development`), append this context block to the output. It preserves architectural assumptions so downstream executors do not lose design context:
>
> ```markdown
> **[Context Payload]**
> **Architecture:** [Key architectural decisions and rationale]
> **Key Interfaces:** [Public APIs, data contracts, interfaces the executor must respect]
> **Conventions:** [Naming, testing patterns, commit style assumed by this plan]
> **Constraints:** [Time, environment, dependency, or performance constraints]
> **Uncertainties:** [What is still unconfirmed and may need adjustment during execution]
> **Handoff Files:** [Paths to the plan document, relevant specs, or design docs]
> ```

**Execution Recommendation Rules:**
- If the environment supports implementation subagents and tasks are mostly independent: Default to recommending `subagent-driven-development`.
- Otherwise: Default to recommending `executing-plans`.
- Do not invent capability names or leave the routing decision entirely up to the user as a default handoff.
- If recommending `subagent-driven-development`, the reason must explicitly mention "environment supports implementation subagents" and "tasks are mostly independent".
- If recommending `executing-plans`, the reason must explicitly mention "requires sequential progression" or "environment lacks implementation subagents".

## Failure Handling

- **Requirements still vague**: Do not output an implementation plan; explain why `brainstorming` should be used first.
- **Scope too large and unsplit**: Suggest splitting into multiple plans first, then decide whether to output only a portion.
- **Missing key technical constraints**: Point out missing info first, then explain what can and cannot be planned.
- **Unable to read key context files**: Can generate a restricted plan, but explicitly mark risk points and pending areas.
- **Environment lacks implementation subagents**: Plan can still be completed, but handoff must default to recommending `executing-plans`.
- **Issues found during review phase**: Reference the structured output of `plan-document-reviewer-prompt.md`; do not replace review conclusions with loose comments.

## Integration

- `brainstorming`: Upstream — brainstorming clarifies requirements and explores alternatives; writing-plans only starts after design is stable.
- `executing-plans`: Downstream — the plan is executed sequentially in the current session.
- `subagent-driven-development`: Downstream — the plan is executed by assigning mostly independent tasks to implementation subagents.
- `workflow-runner`: Adjacent — workflow-runner handles multi-role YAML orchestration, not development plans; these two do not share the same downstream path.
