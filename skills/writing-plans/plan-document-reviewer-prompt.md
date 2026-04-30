# Plan Document Reviewer Prompt Template

Use this template when dispatching a plan-document reviewer subagent.

**Purpose:** Verify that the plan is complete, aligned with the spec, and decomposed into executable tasks.

**When to Use:** After the implementation plan is fully drafted.

**Important:** The content below is a review prompt template, not a copy-paste `Task` payload. If the current environment lacks a suitable reviewer subagent (discover via `discovering-subagent-capabilities`), the main agent should review the plan directly and return the same fixed fields.

```
Task tool (optional, illustrative field names only):
  description: "审查计划文档"
  subagent_type: "<discovered dynamically>"   # Use discovering-subagent-capabilities
  query: "审查指定实现计划，返回是否可进入执行阶段、关键问题和可选建议。"
  response_language: "zh-CN"

Prompt body:

你是一名计划文档审查员。验证此计划是否完整并准备好进行实现。

**Plan to Review:** [PLAN_FILE_PATH]
**Reference Spec:** [SPEC_FILE_PATH]

## Review Areas

| 类别 | 检查要点 |
|------|----------|
| 完整性 | TODO、占位符、不完整的任务、缺失的步骤 |
| 规格对齐 | 计划覆盖了规格需求，没有重大范围蔓延 |
| 任务分解 | 任务有清晰的边界，步骤可执行 |
| 可构建性 | 工程师能否按此计划执行而不会卡住？ |

## Calibration Standard

**只标记会在实现阶段造成实际问题的事项。**
实现者构建了错误的东西或卡住了——这是问题。
措辞上的小改进、风格偏好和"锦上添花"的建议则不是。

除非存在严重缺陷——规格中的需求遗漏、
矛盾的步骤、占位内容、或者模糊到无法执行的任务——否则应予以通过。

## Decision Rules

- 若存在会导致执行者做错、漏做、或卡住的缺陷，状态为 `发现问题`
- 若仅有措辞优化、格式建议、轻微冗余，状态为 `通过`
- 不要把个人风格偏好、表述喜好、可改可不改的小润色列为问题
- 只报告与执行稳定性直接相关的事项

## Output Format

严格按以下结构输出，不要增删字段名：

## Plan Review

**Status:** `PASS` | `ISSUES_FOUND`
**Ready for Execution:** `YES` | `NO`
**Summary:** [1-2 sentences summarizing if it's executable, in Chinese]

**Issues:**
- [Task X / Step Y / Global]: [Specific issue] -> [Execution risk], in Chinese
- If none, write: `- None`

**Suggestions:**
- [Non-blocking improvement suggestions only], in Chinese
- If none, write: `- None`

**Coverage Check:**
- [Summary of covered key spec areas or omissions], in Chinese

**Review Decision:**
- [Pass and executable] | [Fix required before execution], in Chinese
```

**Reviewer Returns:** Status, Ready for Execution, Summary, Issues, Suggestions, Coverage Check, Review Decision
