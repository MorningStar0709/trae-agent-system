# Skill + Rule 工作流程与组件速查

> 本文档是本系统各组件（Rules / Skills）的简明介绍，说明每条规则和每个技能的职责、触发方式以及在整个工作流中的位置。快速了解"谁负责什么、什么时候用"。
>
> 完整全景文档请参见 [05-architecture_zh.md](./05-architecture_zh.md)。

---

## 一、工作流程概览

### 功能开发流（M/L 级别）

**阶段一：路由分派**
- `skill-routing-and-execution-path` 对任务做 T-Shirt 分档（S/M/L）
- `forced-escalation-guardrails` 拦截高风险任务误判为 S 级
- 匹配任务类型后路由到对应技能

**阶段二：设计路径**
- `brainstorming` → 将模糊需求澄清为设计方案
- `writing-plans` → 将稳定方案拆分为可执行的任务计划

**阶段三：执行路径**
- `executing-plans` → 当前会话按计划逐任务执行
- `subagent-driven-development` → 子代理独立执行 + 两层审查

**阶段四：质量门禁**
- `verification-before-completion` → 验证通过才能声称完成
- `requesting-code-review` / `receiving-code-review` → 独立审查与反馈处理

**阶段五：收尾路径**
- `git-commit` → 按 Conventional Commits 规范提交
- `finishing-a-development-branch` → 分支收尾（合并/PR/保持/丢弃）
- `self-improvement` → 沉淀教训到核心记忆

### Bug 修复流

1. 路由到 `systematic-debugging`
2. 读症状 → 稳定复现 → 缩小范围 → 形成假设 → 验证 → 修复 → 确认
3. 进入收尾路径
4. 非显而易见根因 → `self-improvement` 沉淀记忆

### 知识积累流

命令失败 / 用户纠正 / 最佳实践发现 / 知识盲区 → `self-improvement` → 分类存储（Knowledge / Rule / Experience）到 Core Memory

---

## 二、Rules（规则层）

规则文件存放在 `.trae/rules/`，通过 YAML frontmatter 控制加载行为。

### 2.1 Always Apply 规则（每次对话自动加载）

| 规则 | 一句话职责 | 为什么重要 |
|:-----|:----------|:-----------|
| **change-proposal-threshold** | 改规则/skill 之前先自问"值不值得" | 防止 Agent 随意提议重构，节约决策成本 |
| **question-threshold** | 精确定义"必须问"和"绝不能问"的场景 | 用户只在真正需要决策时被介入 |
| **forced-escalation-guardrails** | 7 类高风险任务严禁按小任务处理 | 保护核心配置、安全、CI/CD 不被草率对待 |
| **terminal-execution-stability** | 用稳定证据替代终端猜测 | 杜绝"看起来成功"的假通过 |

### 2.2 条件触发规则（智能匹配场景时加载）

| 规则 | 触发条件 | 做什么 |
|:-----|:---------|:-------|
| **skill-routing-and-execution-path** | 非平凡开发任务 | T-Shirt 分档 + 路由到正确技能，是整个系统的交通枢纽 |
| **review-and-completion-gates** | 任务临近完成 | 编排收尾五步执行顺序（验证→审查→修复→再验证→收尾） |
| **environment-resilience** | MCP 工具连接失败 | 三级降级链：重试 → PowerShell 替代 → 报告局限 |
| **port-conflict-recovery** | 端口冲突/僵尸进程 | netstat 查 PID → taskkill → 确认释放 → 重试 |

---

## 三、Skills（技能层）

技能存放在 `skills/<skill-name>/SKILL.md`，Agent 通过对比 `description` 自动匹配触发。

### 3.1 设计/规划路径

| 技能 | 输入 | 输出 | 一句话职责 |
|:-----|:-----|:-----|:-----------|
| **brainstorming** | 模糊需求 | 内联设计摘要 / 规格文件 | 把"大概想做 X"变成"具体做 X" |
| **writing-plans** | 稳定设计/规格 | 可执行的多任务计划 | 把"做什么"拆解成"先改 A 文件→再改 B 文件→跑验证→提交" |

### 3.2 执行路径

| 技能 | 适用场景 | 工作方式 |
|:-----|:---------|:---------|
| **executing-plans** | 任务耦合度高 / 环境不支持子代理 | 当前会话顺序执行，每 3 个任务设批审查点 |
| **subagent-driven-development** | 任务独立 / 环境支持子代理 | 每任务派新子代理 → 规约审查 → 代码质量审查，一次只推进一个 |

### 3.3 调试/质量路径

| 技能 | 一句话职责 | 核心原则 |
|:-----|:----------|:---------|
| **systematic-debugging** | 用证据链找出根因再修复 | 根因调查完成前不提修复方案 |
| **test-driven-development** | 行为变更 / 回归风险场景先写测试 | 红 → 绿 → 重构 |
| **verification-before-completion** | 完成前用新鲜证据验证 | 没有新鲜证据，不能声称完成 |
| **requesting-code-review** | 请求独立审查 | 越早审查越便宜 |
| **receiving-code-review** | 处理审查反馈 | 审查意见是技术输入，不是盲从指令 |

### 3.4 收尾/进化路径

| 技能 | 一句话职责 | 关键行为 |
|:-----|:----------|:---------|
| **git-commit** | 按 Conventional Commits 提交代码 | type 英文 + scope/body 中文（面向中国团队） |
| **finishing-a-development-branch** | 分支收尾决策与执行 | 先验证 → 再给选项（合并/PR/保持/丢弃） |
| **self-improvement** | 将教训沉淀为持久知识 | 分类 → 去重 → 容量检查 → 写入 Core Memory / Rule / Skill |

### 3.5 编排/工具路径

| 技能 | 什么时候用 |
|:-----|:-----------|
| **dispatching-parallel-agents** | 2 个以上独立的只读/分析任务需要并行执行 |
| **workflow-runner** | 需要多角色（产品/架构/QA）协作的 YAML 编排 |
| **discovering-subagent-capabilities** | 需要确认当前环境有哪些可用子代理类型 |
| **find-docs** | 需要查询框架/库/SDK 的最新官方文档 |
| **chinese-git-workflow** | 项目托管在 Gitee / GitLab / Coding 而非 GitHub |
| **chinese-copywriting** | 需要排版中文技术文档（中英文混排、标点规范） |

### 3.6 浏览器/前端路径

| 技能 | 什么时候用 |
|:-----|:-----------|
| **chrome-devtools** | 需要浏览器自动化、调试、Console/Network/DOM 检查 |
| **frontend-design** | 需要构建或美化前端 UI |
| **chart-visualization** | 需要生成数据图表（折线/柱状/饼图/词云等） |
| **a11y-debugging** | 需要检查可访问性（ARIA 标签、键盘导航、颜色对比度） |
| **debug-optimize-lcp** | LCP / Core Web Vitals 优化 |
| **memory-leak-debugging** | JS / 浏览器内存泄漏排查 |

### 3.7 元技能（技能管理）

| 技能 | 什么时候用 |
|:-----|:-----------|
| **skill-creator** | 创建或修改 SKILL.md |
| **skill-stability-review** | 审查 Skill 包的稳定性（16 个审查维度） |
| **skill-language-policy** | 定义仓库级语言策略（机器层英文 / 用户层中文） |
| **creating-trae-rules** | 创建或修改 `.trae/rules/` 规则文件 |

---

## 四、路由决策速查

### T-Shirt 分档简表

```
S（小任务）→ 直接走，不经过design/plan skill
  ├─ ≤3 个文件
  ├─ 机械变更（复制、重命名、类型修复）
  └─ 无强制升级触发项

M（中任务）→ writing-plans → executing-plans
  ├─ 4-10 个文件
  ├─ 非平凡但设计明确
  └─ 可选 TDD

L/XL（大任务）→ brainstorming 必须先
  ├─ 跨模块/多系统
  ├─ 需求模糊/架构变更
  └─ 设计 → 拆分 → 实现
```

### 技能路由速查

| 如果任务是... | 走这个技能 |
|:-------------|:-----------|
| 需求模糊，不清楚做什么 | brainstorming |
| 设计明确，需要拆任务 | writing-plans |
| 有 Bug / 测试失败 / 构建失败 | systematic-debugging |
| 行为变更需要防回归 | test-driven-development |
| 需要提交代码 | git-commit |
| 需要分支收尾 | finishing-a-development-branch |
| 需要停止重复踩坑 | self-improvement |

---

## 五、平台适配要点

### Trae IDE 机制

- **Rule 激活**：alwaysApply（自动加载）/ description（智能匹配）/ globs（文件匹配）/ `#Rule`（手动引用）
- **Skill 触发**：Agent 自动对比 SKILL.md 的 `description` 字段匹配用户意图
- **记忆管理**：`manage_core_memory` 工具，user + project 各最多 20 条
- **子代理**：`Task` 工具通过 `subagent_type` 参数动态指派

### Windows 环境

- 统一使用 PowerShell 语法（`Select-String` 替代 `grep` 等）
- 端口冲突用 `netstat` + `taskkill`
- `globs` 统一用正斜杠

### 中文团队

- Skill description 内嵌中文触发短语（"帮我提交""逐步排查"等）
- 提交信息格式：`type` 英文 + `scope/body` 中文
- 国内 Git 平台：`finishing-a-development-branch` 通过 `git remote -v` 检测远程地址后自动分流（GitHub 走 CLI，其他走 web UI）
- 技能文件：机器层（frontmatter）英文 + 用户层（流程说明）中文

---

> 本文档为快速参考。每个组件（Rule / Skill）的完整定义、执行协议、输入输出契约及失败处理，请参见对应的源文件（`.trae/rules/` 或 `skills/<name>/SKILL.md`）。
>
> **设计哲学（一句话）**：Rule 做决策（指向谁）、Skill 做操作（怎么做）、Trae 原生能力做底座（不破坏、不替代）、原创机制做增量（T-Shirt 分档、提问阈值）、中文适配做体验（分层中英文策略）。
>
> 更多资料：
> - **极简介绍** → [01-intro_zh.md](./01-intro_zh.md)
> - **设计思路** → [04-design_zh.md](./04-design_zh.md)
> - **亮点宣传** → [02-overview_zh.md](./02-overview_zh.md)
> - **全景详解** → [05-architecture_zh.md](./05-architecture_zh.md)
