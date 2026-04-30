---
name: workflow-runner
description: Run an agency-orchestrator style YAML workflow inside the current Trae conversation by simulating or coordinating multiple roles. Use when the user provides a `.yaml` or `.yml` workflow, asks for multi-role collaboration, says things like “用多个角色一起评审这个 PRD”“多角色协作”“先生成工作流再执行”“让产品经理、架构师、QA 一起看一下”, or wants roles such as product manager, architect, reviewer, or QA to work together. Supports layered execution, role prompting, variable interpolation, document-backed inputs, and parallel steps only when the current environment has a clear subagent mapping. Do not use for ordinary implementation plans, simple code changes, or tasks already covered by `writing-plans`, `executing-plans`, `subagent-driven-development`, or single-purpose review/debug skills.
---

# Workflow Runner

## Overview

Use this skill to run an `agency-orchestrator` style multi-role workflow within the current Trae conversation. The core purpose is not standard task breakdown, but rather:

- Reading or generating a YAML workflow.
- Maintaining DAG layers based on `depends_on`.
- Reading role files and switching roles for execution.
- Executing true parallel steps only when conditions are met.

The default goal is stable execution, not superficial parallelism.

## Use This Skill

- The user provides a `.yaml` or `.yml` workflow and requests to execute it.
- The user explicitly asks for "multi-role collaboration" or "multiple roles analyzing/reviewing/creating together".
- The user wants to generate a multi-role workflow first, then confirm and execute it.
- The user wants to preserve role division, step dependencies, and execution layers, rather than just getting a plain summary.

## Do Not Use

- The user just wants a normal answer without the appearance of role orchestration.
- The user wants to write an implementation plan or break down development tasks; use `writing-plans` instead.
- The user already has an implementation plan and wants to execute it sequentially; use `executing-plans` instead.
- The user has an implementation plan and the environment supports implementation subagents; use `subagent-driven-development` instead.
- The user is only asking for a single code review, single debugging session, or single browser validation.

## Input Contract

**Required Inputs:**

- `workflow_file`: The path to the YAML file provided by the user; OR
- `workflow_intent`: The multi-role collaboration goal described by the user, used to generate a workflow first.

**Common Optional Inputs:**

- `agents_dir`
- `persist_outputs`
- `output_dir`
- `execution_mode_hint`

Missing input handling:
- **No YAML, but multi-role orchestration requested**: Generate a minimal workflow draft first; do not execute immediately.
- **Missing required inputs**: Ask first; do not guess default values.
- **Missing role directory or role files**: Report the missing items and search locations; do not skip steps.
- **Incomplete inputs but partial preview possible**: Provide a pre-execution plan or YAML draft, but do not pretend it has been executed.

### Input Extraction

Collect input values in this order:

1. Explicit assignments in the user's current message (e.g., `topic = "..."`, `topic: ...`).
2. Values with the same name explicitly given by the user earlier in the session.
3. The `default` value in the YAML.
4. Ask the user if still missing.

If the user provides both `workflow_file` and input values in the same message, extract the inputs first, then determine if follow-up questions are needed.

### Document-Backed Inputs

If an input name clearly indicates a document path, such as:
- `prd_file`
- `spec_file`
- `doc_file`
- `brief_file`
- `*_file`
- `*_path`

Treat it as a "document input that must be read first" by default.

Rules:
1. Verify the path exists and is readable.
2. Use `Read` to read the document.
3. Include the key content of the document as part of the role context.
4. Do not just inject the path string into the task template.
5. If the document is too long, summarize it first, but state that execution is based on the summary.

## Execution Protocol

Default execution path:

1. **Obtain Workflow**: Read the YAML file, or generate a minimal draft if none exists.
2. **Locate Role Files**: Find `agents_dir` and read role files.
3. **Collect Inputs**: Extract inputs; read documents for document-backed inputs.
4. **Build Layered Plan**: Group steps by `depends_on` and execute sequentially by layer.
5. **Parallel Execution**: Only execute same-layer steps in true parallel if there is an explicit subagent mapping.
6. **Aggregate Results**: Summarize the output; write to `.ao-output/` only if persistence is requested.

### 1. Obtain Workflow

- **YAML provided**: Use `Read` to extract `name`, `agents_dir`, `inputs`, `steps`.
- **Intent provided**: Generate a minimal workflow draft and get confirmation before executing.
- The workflow must have at least one step; otherwise, stop and report.

### 2. Locate Role Files

Locate `agents_dir` in this order:
1. Same directory as the YAML file.
2. Current workspace.
3. Parent of current workspace.
4. Common dependency directories (e.g., `node_modules/<agents_dir>`).

Use tools like `LS`, `Glob`, `Read`; do not rely on Unix shell checks.

Each step's `role` maps to `<agents_dir>/<role>.md` by default. Before execution, read at least:
- Role name.
- Stable frontmatter.
- Role body after the second `---`.

### 3. Collect Inputs and Interpolate Variables

- Handle normal inputs via extraction rules.
- Read document inputs before providing them as context.
- `{{input_name}}` comes from input values.
- `{{previous_output}}` comes from previous step outputs.

If a variable is undefined:
- If it is a required input, pause and ask.
- If it should come from a previous step, check `depends_on` or `output` config.

### 4. Build Layered Plan

Topologically sort by `depends_on` and organize steps into layers:
- Layer 1: Steps with no dependencies.
- Subsequent layers: Steps whose dependencies are met.

Provide a brief layered plan before execution, stating total steps, steps per layer, and whether parallelism is "logical only".

### 5. Execute Layer by Layer

Default to sequential execution in the main session layer by layer. Even if logically parallelizable, do not violate DAG dependencies.

For single-step layers:
- Explicitly switch roles.
- State the step name, role name, and task goal.
- The output must reflect the role's perspective, not a generic answer.

For multi-step layers, true parallel execution is only allowed if ALL conditions are met:
- No dependencies between steps.
- No shared mutable file state.
- Suitable subagent capabilities exist in the current environment.
- Each step can be written as a self-contained prompt.
- Explicit mapping exists between the role task and subagent type.

If any condition fails, fallback to "logical parallel layer, actual sequential execution in main session". Do not force parallel execution for generic text roles (content creation, analysis, review) without explicit mapping.

### 6. Record and Persist

After each step, record at least:
- `step_id`
- `role`
- Output body
- Write to variable context if `output` field exists.

Force persistence only when:
- User explicitly requests saving artifacts.
- The workflow is an artifact-generating task by nature.

Default output directory:
`.ao-output/<workflow-name>-<YYYY-MM-DD>/`

Common outputs include:
- `steps/<index>-<step-id>.md`
- `summary.md`
- `metadata.json`

## Failure Handling

- **Missing/Invalid YAML**: Explain the location of the error. If the user just expressed an intent, switch to draft generation mode.
- **Missing Role Directory/Files**: Report attempted locations and the specific missing `role`. Do not skip the step and pretend to continue.
- **Undefined Variables**: Distinguish between missing inputs and workflow config errors. Clarify first; do not guess replacements.
- **Unread Document Inputs**: Do not treat the file path as consumed context. Read the document first. If a step heavily depends on an unreadable document, stop and report.
- **Step Failure**: Mark the step as failed, skip downstream dependent steps, and continue with other independent steps. Clearly state success, failure, and skipped items in the final report.
- **Environment Lacks True Parallelism**: Explicitly state that "logical parallel layer, actual sequential execution" is being used. Do not pretend the environment has general multi-agent capabilities if it doesn't.

## Output Contract

The final output must include:
- Workflow name
- Execution mode (YAML execution or draft generation)
- Number of layers and steps
- Status of each step
- Whether true parallelism was used
- Final deliverables
- Output directory (if persisted)

Use this fixed skeleton:

```markdown
## 工作流运行总结

**名称:** <workflow-name>
**层级/步骤:** <层级数> / <步骤数>
**状态:** `成功` | `部分成功` | `失败`

**产出物:**
- [交付物摘要；如果较长可在下方展开说明]
- [若无产出物，请写 "- 无"]

**未解决的冲突/阻碍:**
- [若无冲突，请写 "- 无"]

**下一步建议:**
- [继续下一步计划 | 等待用户确认 | 退出]
```

If still in the "generate YAML draft for confirmation" phase, do not say "工作流执行已完成。"; explicitly state "工作流草稿已生成，等待确认后执行。".

## Resources

The main file only defines the execution contract; examples and test-run assets are in companion directories:
- evals: `evals/evals.json`
- examples: `examples/input.md`, `examples/output.md`
- Minimal test run: `resources/try-it.md`
- Sample YAML: `resources/sample-workflow.yaml`
- Document-driven sample: `resources/sample-prd-review-workflow.yaml`
- Sample document: `resources/sample-prd.md`
- Directory convention: `resources/role-directory-convention.md`
- Document input guidelines: `resources/document-input-guidelines.md`

## Integration

- `writing-plans`: Downstream — after workflow-runner completes its multi-role analysis (e.g., PRD review, architect assessment), the conclusions can serve as input for `writing-plans` to generate an implementation plan. The handoff output should include key decisions, open risks, and recommended next steps.
- `executing-plans`: Sequentially executes implementation plans, does not emphasize role-playing.
- `subagent-driven-development`: Subagent-driven development, not equivalent to role workflows.
- `dispatching-parallel-agents`: Can be referenced for parallel decisions, but does not replace the workflow semantics of this skill.
