---
name: dispatching-parallel-agents
description: Use when there are 2 or more independent tasks that can be delegated to available Task subagents in parallel, including Chinese requests such as “并行搜索”“并行审查”“并行浏览器验证”“并行跑子代理”. Do not use when tasks share file edits, depend on shared state, require sequential reasoning, or are faster with direct tools.
---

# Dispatching Parallel Agents

## Overview

Use this skill to determine which tasks are suitable for parallel delegation to independent subagents. Parallel execution requires true independence between tasks and the availability of capable subagent types in the current environment.

Core principle: Only parallelize truly independent tasks. If tasks have dependencies, execute them sequentially.

## Use This Skill

- There are 2 or more mutually independent search, review, or browser validation tasks.
- Each task can be clearly described on its own.
- Tasks do not share file editing state, runtime state, or intermediate results.

## Do Not Use

- Multiple tasks will edit the same file or depend on the same intermediate state.
- The current environment lacks the required implementation/review subagent capabilities.
- The tasks are essentially different facets of the same problem and require holistic understanding.
- The work is small enough that doing it directly is clearly faster — if in doubt, dispatch is safer than over-optimizing for speed.
- The user is asking for a YAML-based multi-role simulation; use `workflow-runner` instead.
- The tasks involve writing or modifying code; use `subagent-driven-development` instead. This skill is strictly for read-only, analysis, or independent review tasks.

## Input Contract

Required inputs:
- A clear list of tasks to be evaluated for parallel execution.

Optional inputs:
- The specific subagent types available in the current environment — discover dynamically via `discovering-subagent-capabilities`.

Missing input handling:
- If tasks are not clearly separated, split them first before evaluating parallel feasibility.

## Execution Protocol

Execute in the following order:

1. **Pre-flight: Discover Available Subagents**: Use `discovering-subagent-capabilities` to read the Task tool's `subagent_type` enum from the system prompt. Read each subagent's description and match against the task types. The enum is dynamic — do not assume a fixed set of agent names. If no matching subagent exists for a task type, fallback to inline execution.
2. **Evaluate Task Boundaries**: Confirm that tasks are truly independent. If they share file edits, runtime state, or have sequential dependencies, abort parallelization.
3. **Verify Environment**: Check if the current environment has capable subagents for the task types found in step 1. If code implementation is needed and no reliable implementation subagent exists, fallback to `executing-plans` or sequential execution.
4. **Check Parallel Conditions**:
   - The problem can be split into independent sub-problems.
   - Each sub-problem can be written as a self-contained prompt.
   - The results from each subagent can be consumed independently.
   - Starting them simultaneously will not cause resource conflicts (port contention, same-file write locks, same external API rate limit).
5. **Prepare Prompts**: Write a self-contained prompt for each subagent, including goal, scope, necessary context, expected return content, and constraints. Keep each prompt focused and narrow — if a parallel task is expected to be large (5+ files or broad scope), pre-split it into multiple finer-grained sub-tasks before dispatch. Use the subagent types identified in step 1 to route each task to the best-matching agent.
6. **Dispatch**: Launch multiple `Task` calls simultaneously in a single tool message, using the `subagent_type` values discovered in step 1. Do not exceed 4 parallel tasks.
7. **Aggregate**: After subagents return, the main session must aggregate and cross-check the results. Do not treat subagent reports as final facts without verification.

**Aggregation Protocol:**
```
1. Extract key findings from each subagent report.
2. Compare findings side by side: which points agree, which conflict.
3. For conflicting claims, evaluate credibility based on:
   - Did the subagent have access to the necessary context?
   - Is the claim supported by evidence or just opinion?
   - Does the claim contradict known facts from other sources?
4. State the final conclusion per conflict point, with reasoning.
5. If conflicts cannot be resolved without additional input, flag them for the user.
```

## Failure Handling

- **Shared State Detected**: If tasks share state, immediately fallback to sequential execution.
- **Subagent Unavailable**: If the required subagent type is missing, fallback to sequential tool usage or `executing-plans`.
- **Subagent Failure**: If a parallel subagent fails, report the specific failure and either retry that specific task or complete it sequentially.

## Output Contract

The final output must include:
- The list of tasks dispatched in parallel.
- The aggregated results from all subagents.
- Any cross-check or verification performed on the results.
- Any failures or fallback actions taken.

## Integration

- `workflow-runner`: Adjacent — workflow-runner handles YAML-based multi-role orchestration with DAG dependencies; dispatching-parallel-agents handles ad-hoc parallel subagent tasks without a pre-defined workflow.
- `subagent-driven-development`: Adjacent — subagent-driven-development dispatches implementation subagents **sequentially** with two-stage reviews; dispatching-parallel-agents is for **read-only** parallel analysis/review tasks only.
- `executing-plans`: Fallback — when tasks are not truly independent, fall back to sequential execution in the main session.
- `discovering-subagent-capabilities`: Upstream — before dispatching, use this skill if you need to verify which subagent types are available in the current environment.