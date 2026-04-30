# Code Quality Reviewer Prompt Template

Use this template when dispatching a code-quality reviewer subagent.

**Purpose:** Verify that the implementation is well-built, maintainable, and backed by meaningful validation.

**Dispatch only after spec-compliance review has passed.**

**Important:** The content below is a review prompt template, not a copy-paste `Task` payload. If the current environment supports a reviewer subagent (discover via `discovering-subagent-capabilities`), wrap it using the real schema. Otherwise, the main agent should perform the code-quality review directly with this template.

```
Task tool (optional, illustrative field names only):
  description: "审查任务 N 的代码质量"
  subagent_type: "<discovered dynamically>"   # Use discovering-subagent-capabilities
  query: "审查指定任务实现的代码质量、测试充分性和维护性，返回主要优点、问题和结论。"
  response_language: "zh-CN"

Prompt body:

你正在审查一个已通过规格合规性检查的实现，关注点是代码质量而不是需求覆盖。

**Completed:** [来自实现者的报告]
**Plan/Spec:** [plan-file] 中的任务 N
**BASE_SHA:** [任务开始前的提交]
**HEAD_SHA:** [当前提交]
**Task Summary:** [任务摘要]

阅读实际改动并审查：
- 命名、结构、边界是否清晰
- 测试是否验证真实行为，覆盖是否与风险匹配
- 是否引入了明显的复杂度、重复或脆弱逻辑
- 是否遵循代码库已有模式
- 是否存在值得立即修复的 bug 风险或可维护性问题

**Communication Tone Requirements:**
- 给出反馈时，用“建议”代替“命令”（如：建议考虑用 X，因为 Y）
- 用“提问”代替“否定”（如：这里用 sync 是出于什么考虑？）

输出：
- 严格按以下结构输出，不要增删字段名：

## 代码质量审查

**状态:** `PASS` | `ISSUES_FOUND`
**摘要:** [1-2 句话]

**优点:**
- [若无，请写 `- 无`]

**问题:**
- `[必须修复|建议修改|仅供参考|问题]` [具体问题]
- [若无，请写 `- 无`]

**评估结论:**
- [通过并继续] | [在继续前必须修复]
```

**Additional Checks Beyond Standard Code Quality:**
- 每个文件是否有单一明确的职责和定义清晰的接口？
- 各单元是否拆分得足以独立理解和测试？
- 实现是否遵循了计划中的文件结构？
- 本次实现是否创建了已经很大的新文件，或显著增大了现有文件？（不要标记已有的文件大小问题——聚焦于本次变更带来的影响。）

**Reviewer Returns:** Pros, Issues (Critical/Major/Minor), Assessment Conclusion
