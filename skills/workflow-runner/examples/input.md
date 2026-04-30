# 示例输入

## 示例 1：直接执行 YAML

执行 `workflows/story-creation.yaml`。如果其中有同层可并行步骤，就按可用能力处理。

## 示例 2：先生成工作流

帮我找三个角色一起分析这个 PRD。想要产品经理、架构师、QA 的视角。没有现成 YAML，你先生成工作流给我确认。

## 示例 3：文档驱动工作流

请使用 `workflow-runner` 执行 `resources/sample-prd-review-workflow.yaml`。输入 `prd_file = resources/sample-prd.md`，重点看可执行性、风险和验收标准。

## 示例 4：边界样例

这个仓库已经有实现计划了，你直接按计划改代码、补测试、验证并提交。
