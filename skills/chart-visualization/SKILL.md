---
name: chart-visualization
description: Visualize data in Trae by selecting the most suitable chart type, extracting parameters, and generating a chart image with the local JavaScript script. Use for Chinese or English requests such as 数据可视化, 生成图表, 画折线图, 柱状图, 饼图, 漏斗图, 词云, 地图, 组织架构图, or 把这些数据做成图.
---

# Chart Visualization Skill

This skill provides a comprehensive workflow for transforming data into visual charts. It handles chart selection, parameter extraction, and image generation.

When the user writes in Chinese, explain chart choices and results in Simplified Chinese. Keep chart tool names, JSON keys, and script arguments in English.

## Trae and Windows Notes

- Treat this as an agent execution workflow, not end-user documentation.
- Run commands from this skill directory or use an absolute script path so `scripts/generate.js` resolves reliably.
- On Windows Trae, prefer PowerShell-compatible commands and avoid shell quoting that only works in Unix shells.
- If the user writes in Chinese, ask clarifying questions, explain chart choices, and report results in Simplified Chinese. Keep `tool`, `args`, JSON keys, URLs, and file paths in their original form.
- Do not invent missing data. If required chart fields are absent or ambiguous, ask one concise clarification before running the script.

## Do Not Use

Do not use this skill when:

- The user only wants a conceptual explanation of chart types and does not need a generated chart artifact.
- The task is spreadsheet editing, data cleaning, or statistical analysis without chart generation.
- The user asks for frontend chart component code instead of generating an image through this script.
- The request depends on live data retrieval, database queries, or web scraping that has not already produced chart-ready data.
- The user needs manual visual design of an infographic, poster, or dashboard rather than structured chart generation.

## Workflow

To visualize data, follow these steps:

### 1. Intelligent Chart Selection
Analyze the user's data features to determine the most appropriate chart type. Use the following guidelines (and consult `references/` for detailed specs):

- **Time Series**: Use `generate_line_chart` (trends) or `generate_area_chart` (accumulated trends). Use `generate_dual_axes_chart` for two different scales.
- **Comparisons**: Use `generate_bar_chart` (categorical) or `generate_column_chart`. Use `generate_histogram_chart` for frequency distributions.
- **Part-to-Whole**: Use `generate_pie_chart` or `generate_treemap_chart` (hierarchical).
- **Relationships & Flow**: Use `generate_scatter_chart` (correlation), `generate_sankey_chart` (flow), or `generate_venn_chart` (overlap).
- **Maps**: Use `generate_district_map` (regions), `generate_pin_map` (points), or `generate_path_map` (routes).
- **Hierarchies & Trees**: Use `generate_organization_chart` or `generate_mind_map`.
- **Specialized**:
    - `generate_radar_chart`: Multi-dimensional comparison.
    - `generate_funnel_chart`: Process stages.
    - `generate_liquid_chart`: Percentage/Progress.
    - `generate_word_cloud_chart`: Text frequency.
    - `generate_boxplot_chart` or `generate_violin_chart`: Statistical distribution.
    - `generate_network_graph`: Complex node-edge relationships.
    - `generate_fishbone_diagram`: Cause-effect analysis.
    - `generate_flow_diagram`: Process flow.
    - `generate_spreadsheet`: Tabular data or pivot tables for structured data display and cross-tabulation.

### 2. Parameter Extraction
Once a chart type is selected, read the corresponding file in the `references/` directory (e.g., `references/generate_line_chart.md`) to identify the required and optional fields.
Extract the data from the user's input and map it to the expected `args` format.

### 3. Chart Generation
Invoke the `scripts/generate.js` script with a JSON payload.

**Payload Format:**
```json
{
  "tool": "generate_chart_type_name",
  "args": {
    "data": [...],
    "title": "...",
    "theme": "...",
    "style": { ... }
  }
}
```

**Execution Command:**
```powershell
node ".\scripts\generate.js" '{ "tool": "generate_chart_type_name", "args": { "data": [], "title": "..." } }'
```

For complex payloads in PowerShell, prefer storing compact JSON in a variable before invoking Node:

```powershell
$payload = '{"tool":"generate_line_chart","args":{"data":[],"title":"..."}}'
node ".\scripts\generate.js" $payload
```

### 4. Result Return
The script will output the URL of the generated chart image.
Return the following to the user:
- The image URL.
- The complete `args` (specification) used for generation.

## Failure Handling

- Missing or ambiguous data -> ask for the smallest missing detail needed to choose the chart or fill required fields.
- Unknown chart type -> select the closest supported chart type from `references/` and explain the mapping briefly.
- Script path not found -> verify the current working directory and rerun with the absolute path to `scripts/generate.js`.
- JSON parse or shell quoting error -> rebuild a compact JSON payload and pass it as one PowerShell argument.
- Script returns no URL -> report the failure, include the tool name used, and do not fabricate an image URL.

## Reference Material
Detailed specifications for each chart type are located in the `references/` directory. Consult these files to ensure the `args` passed to the script match the expected schema.
