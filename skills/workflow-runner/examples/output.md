# 示例输出

## 直接执行 YAML 时

已识别为 `workflow-runner` 场景：这是一个 YAML 驱动的多角色工作流，不是普通实现计划。

执行前计划：

- 第 1 层：`ideation`
- 第 2 层：`outline`、`critique`（逻辑上可并行）
- 第 3 层：`revision`

我会先读取工作流与角色文件，再按角色上下文执行各步骤。若当前环境存在合适子代理且这些步骤不共享状态，则第 2 层真实并行；否则保留并行层语义，在当前会话中顺序执行。

固定结果骨架：

```markdown
工作流执行已完成。

**工作流：** `<workflow-name>`
**执行模式：** `yaml` | `draft-then-run`
**执行结论：** `全部完成` | `部分完成` | `阻塞`
**层级 / 步骤：** `<layers>` / `<steps>`
**并行情况：** `真实并行` | `逻辑并行层，实际顺序执行` | `未涉及并行`

**步骤状态：**
- `<step-id>`: `completed` | `failed` | `skipped`

**最终成果：**
- [成果摘要；若内容较长，可在后面继续展开]

**阻塞或风险：**
- [若无则写 `- 无`]

**输出位置：**
- [若未落盘则写 `- 未落盘`]
```

## 没有 YAML 时

已识别为多角色编排需求。我先生成一个最小工作流草案，确认后再执行：

```yaml
name: prd-review
steps:
  - id: pm-review
    role: product/manager
    task: "从产品目标和需求完整性角度评审 PRD"
  - id: architect-review
    role: engineering/architect
    task: "从系统设计和可实施性角度评审 PRD"
    depends_on: [pm-review]
  - id: qa-review
    role: quality/qa
    task: "从测试策略和验收风险角度评审 PRD"
    depends_on: [architect-review]
```

如果你确认，我再继续读取角色文件并执行。

此时不应假装“执行已完成”，而应明确停留在“草案待确认”状态。

## 文档驱动工作流时

已识别到 `prd_file` 属于文档型输入。我会先读取 `sample-prd.md`，再把文档关键内容作为角色上下文，而不是只把路径字符串代入任务模板。

执行前计划：

- 第 1 层：`framing`
- 第 2 层：`solution-pass`、`risk-pass`（逻辑上可并行）
- 第 3 层：`synthesis`

这次预期输出应针对 PRD 正文形成具体判断，例如目标是否清晰、约束是否足够、风险是否遗漏，而不是只给通用评审框架。

## 边界场景时

这更像“执行现有实现计划”，不属于 `workflow-runner` 的优先范围；应改用 `executing-plans`，若环境支持真正的实现型子代理则考虑 `subagent-driven-development`。
