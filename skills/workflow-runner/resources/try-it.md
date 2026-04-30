# 最小试跑

## 资源位置

- 工作流：`resources/sample-workflow.yaml`
- 文档工作流：`resources/sample-prd-review-workflow.yaml`
- 示例 PRD：`resources/sample-prd.md`
- 角色目录：`resources/sample-agents/`

## 推荐试跑提示

```text
请使用 workflow-runner 执行 `c:\Users\skyler\.trae\skills\workflow-runner\resources\sample-workflow.yaml`。
输入 topic = “为一个 PRD 做多角色评审”
输入 context = “重点关注可执行性、风险和最终结论”
如果第二层可以并行，请按当前环境的实际能力处理。
```

## 推荐文档试跑提示

```text
请使用 workflow-runner 执行 `c:\Users\skyler\.trae\skills\workflow-runner\resources\sample-prd-review-workflow.yaml`。
输入 prd_file = `c:\Users\skyler\.trae\skills\workflow-runner\resources\sample-prd.md`
输入 review_focus = “重点关注目标清晰度、实施代价、风险和验收标准”
如果第二层可以并行，请按当前环境的实际能力处理。
```

## 预期行为

- 先读取 YAML
- 定位 `sample-agents`
- 读取 `analysis/researcher` 角色
- 生成 3 层执行计划
- 第 2 层识别为逻辑上可并行的两个步骤
- 输出最终综合结论

## 当前环境下的预期执行形态

- 这套样例的第 2 层在语义上可并行
- 但如果当前环境没有明确可映射的通用执行型子代理，预期行为应是“逻辑并行层，实际顺序执行”
- 这不是失败，而是 `workflow-runner` 的正确回退策略

## 这个最小样例验证什么

- YAML 驱动是否生效
- 角色路径映射是否稳定
- 变量替换是否生效
- 并行层识别是否正确
- 最终汇总步骤是否能消费前序输出

## 文档试跑额外验证什么

- `prd_file` 这类输入是否会被识别为“先读文档”
- 角色执行时是否真的引用文档内容，而不是只复述文件路径
- 当有真实文档输入时，输出是否从“评审框架”升级为“针对文档的具体判断”

## 结果解释边界

- 这个样例默认输入的是“评审主题”，不是一份真实 PRD 正文
- 因此合理输出应偏向“评审框架、主要风险、下一步建议”
- 如果直接产出像真实评审结论那样过于具体的 verdict，反而说明执行时在硬猜输入
