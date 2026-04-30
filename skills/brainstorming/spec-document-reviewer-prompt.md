# Spec Document Reviewer Prompt Template

Use this template when a written spec needs review.

**Purpose:** Verify that the spec is complete, internally consistent, and ready for implementation planning.

**When to Use:** After the spec has been written to a user-approved location. If the current environment supports `Task` or reviewer subagents, it can be delegated; otherwise, the main agent can review directly with this template.

**Important:** The content below is a review prompt template, not a copy-paste `Task` payload. If you invoke `Task`, adapt it to the real schema and compress the prompt body into a short `query`.

```
Task tool (optional, illustrative field names only):
  description: "审查规格文档"
  query: "审查指定规格文档，返回是否可进入计划阶段、关键问题和可选建议。"
  response_language: "zh-CN"

Prompt body:

你是一名规格文档审查员。验证此规格是否完整并准备好进行计划编写。

**Spec to Review:** `[SPEC_FILE_PATH]`

## Review Areas

| 类别 | 检查要点 |
|------|----------|
| 完整性 | TODO、占位符、"TBD"、不完整的章节 |
| 一致性 | 内部矛盾、相互冲突的需求 |
| 清晰度 | 需求模糊到可能导致构建出错误的东西 |
| 范围 | 是否足够聚焦以用于单个计划，而非涵盖多个独立子系统 |
| YAGNI | 未请求的功能、过度设计 |

## Calibration Standard

**只标记会在实现计划阶段造成实际问题的事项。**
缺失的章节、矛盾之处、或者模糊到可能被两种不同方式理解的需求，
这些才是问题。措辞上的小改进、风格偏好、以及"某些章节不如其他章节详细"则不是。

除非存在会导致计划或实现出错的严重缺陷，否则应予以通过。

## Output Format

## Spec Review

**Status:** `PASS` | `ISSUES_FOUND`

**Issues:**
- [Chapter X]: [Specific issue] - [Why it matters for planning], in Chinese
- If none, write `- None`

**Suggestions:**
- [Improvement suggestions], in Chinese
- If none, write `- None`
```

**Reviewer Returns:** Status, Issues, Suggestions
