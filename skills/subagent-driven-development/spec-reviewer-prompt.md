# Spec Compliance Reviewer Prompt Template

Use this template when dispatching a spec-compliance reviewer subagent.

**Purpose:** Verify that the implementer built exactly what was requested, with no missing scope or unnecessary extras.

**Important:** The content below is a review prompt template, not a copy-paste `Task` payload. If the current environment supports a reviewer subagent (discover via `discovering-subagent-capabilities`), wrap it using the real schema. Otherwise, the main agent should perform the spec-compliance review directly with this template.

```
Task tool (optional, illustrative field names only):
  description: "审查任务 N 的规格合规性"
  subagent_type: "<discovered dynamically>"   # Use discovering-subagent-capabilities
  query: "审查指定任务实现是否严格符合要求，返回通过/问题列表和最小修复建议。"
  response_language: "zh-CN"

Prompt body:

你正在审查一个实现是否与其规格匹配。

## Required Scope

[任务需求的完整文本]

## Claimed Implementation

[来自实现者的报告]

## Critical Rule: Do Not Trust The Report

实现者完成得疑似过快。他们的报告可能不完整、
不准确或过于乐观。你必须独立验证所有内容。

**Do Not:**
- 相信他们关于实现内容的说法
- 信任他们关于完整性的声明
- 接受他们对需求的解读

**You Must:**
- 阅读他们写的实际代码
- 逐行对比实际实现和需求
- 检查他们声称已实现但实际遗漏的部分
- 寻找他们未提及的多余功能

## Your Work

阅读实现代码并验证：

**Missing Requirements:**
- 他们是否实现了所有被要求的内容？
- 是否有他们跳过或遗漏的需求？
- 是否有他们声称可用但实际未实现的功能？

**Extra / Unnecessary Work:**
- 他们是否构建了未被要求的内容？
- 他们是否过度工程化或添加了不必要的功能？
- 他们是否添加了规格中没有的"锦上添花"功能？

**Misunderstandings:**
- 他们是否以不同于预期的方式解读了需求？
- 他们是否解决了错误的问题？
- 他们是否实现了正确的功能但方式不对？

**通过阅读代码来验证，而非信任报告。**

严格按以下结构输出，不要增删字段名：

## 需求审查结果

**任务:** [任务 N / 任务名称]
**结论:** `通过` | `需要修改`
**摘要:** [1-2 句话，总结审查结果]

**未对齐的需求或计划偏离:**
- [遗漏 / 多余 / 误解；带上 file:line 引用]
- [若无偏离，请写 "- 无"]

**不合理的假设或硬编码:**
- [带上 file:line 引用]
- [若无假设，请写 "- 无"]

**下一步操作:**
- [继续执行] | [在继续前必须修复]
```
