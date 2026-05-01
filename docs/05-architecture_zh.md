# Trae AI Agent System 技能与规则体系：产品全景文档

> **文档版本:** v1.1 | **更新日期:** 2026-04-30 | **作者:** MorningStar0709
>
> 本文档以产品经理视角，完整介绍本项目的 Skill + Rule 体系架构、工作流程、解决的核心痛点以及演进路线。全文围绕 **Trae IDE 平台特性** 和 **中文团队场景** 进行适配说明。
>
> 配套文档：
>
> - **极简介绍** → [01-intro\_zh.md](./01-intro_zh.md)（15 秒速览）
> - **快速上手** → [02-overview\_zh.md](./02-overview_zh.md)（亮点与痛点宣传）
> - **组件速查** → [03-components\_zh.md](./03-components_zh.md)（各组件一句话职责）

***

## 一、背景与定位

### 1.1 项目是什么

本项目的本质是一套 **AI Agent 认知增强框架**——通过 **Rules（规则层）** 和 **Skills（技能层）** 的双层架构，为 Trae IDE 中的 AI Agent 提供：

- **路由决策能力**：知道什么任务该用什么技能处理
- **行为约束系统**：知道什么能做、什么不能做、什么情况下要问人
- **执行协议规范**：知道每一步该怎么执行、输出什么格式
- **持续进化机制**：能从每次交互中学习，不再重复踩坑

### 1.2 平台基础：Trae IDE

本系统深度绑定 Trae IDE 的以下平台能力构建：

- **Rule 机制**：通过 `.trae/rules/` 目录下的 Markdown 文件（YAML frontmatter + 内容），支持 alwaysApply（每次加载）、description（智能场景匹配）、globs（文件匹配）、scene: git\_message（提交信息）四种激活模式。规则可嵌套三层，支持项目级和模块级覆盖。
- **Skill 机制**：通过 `skills/<skill-name>/SKILL.md` 文件定义，每个 Skill 包含 frontmatter 元数据（name/description）、Input Contract（输入契约）、Execution Protocol（执行协议）、Failure Handling（失败处理）和 Integration（上下游衔接）。Skill 通过 Agent 的 `Skill` 工具触发——Agent 收到用户请求后，对比 SKILL.md 的 description 是否匹配当前意图，匹配则自动加载该 Skill 的完整指令。
- **Core Memory 系统**：通过 `manage_core_memory` 工具管理，支持 Knowledge / Rule / Experience 三类记忆。新对话启动时注入 XML 静态快照，user 和 project 各最多 20 条。
- **子代理（Subagent）系统**：通过 `Task` 工具的 `subagent_type` 参数动态指派，每个子代理独立执行一次任务后返回结构化结果（DONE / DONE\_WITH\_CONCERNS / NEEDS\_CONTEXT / BLOCKED）。
- **IDE 内置工具集**：包括 `RunCommand`（终端执行）、`Read` / `Write` / `SearchReplace`（文件操作）、`Grep` / `Glob` / `SearchCodebase`（代码搜索）、`GetDiagnostics`（语言诊断）、`WebSearch` / `WebFetch`（网络检索）、`AskUserQuestion`（用户交互）、`OpenPreview`（预览服务）。
- **MCP（Model Context Protocol）生态**：支持 Chrome DevTools MCP（浏览器自动化）、Everything Search MCP（Windows 文件搜索）等外部工具接入。

本项目的所有 Rules 和 Skills，均以 Trae 可识别的格式存放在项目根目录的 `.trae/` 文件夹中。

### 1.3 为什么需要这个系统

AI Agent 在 IDE 中工作，本质上面临三类矛盾：

| 矛盾            | 表现                    | 不解决的后果            |
| :------------ | :-------------------- | :---------------- |
| **通用 vs 专业化** | Agent 什么都能做，但什么都不精    | 简单任务过度复杂，复杂任务处理不当 |
| **主动 vs 可控**  | Agent 越主动越容易犯错，越保守越没用 | 要么胡乱操作，要么什么都问用户   |
| **单次 vs 持续**  | 每次对话从零开始，没有记忆积累       | 同一个坑反复踩，同样的知识反复学  |

本系统正是为解决这三类矛盾而设计。

***

## 二、系统架构概览

系统分为三层，自上而下依次传递：用户输入 → 规则层路由决策 → 技能层执行 → 记忆层沉淀。

**第一层：用户交互层（User Input）**
用户下达指令，进入规则层。

**第二层：规则层（Rules）** —— 负责路由决策

- **alwaysApply 规则**（YAML frontmatter 中 `alwaysApply: true`，每次对话自动加载）：
  - 变更提议阈值、提问阈值、强制升级护栏、终端执行稳定性、技能路由与执行路径
- **条件触发规则**（YAML frontmatter 中 `alwaysApply: false` 但设 `description`，Agent 根据语义匹配合适场景时自动加载）：
  - 审查与收尾门禁、环境降级（MCP 失败处理）、端口冲突恢复
- **手动规则**（`alwaysApply: false` 且无 description，用户通过 `#Rule 规则名` 手动引用才加载）：适用于极少使用的专项指导

规则文件存放在 `.trae/rules/` 目录，支持项目根目录和模块级子目录（嵌套最多三层）。规则层做出路由决策后，将任务分派到技能层。

**第三层：技能层（Skills）** —— 负责具体执行
每个 Skill 对应 `skills/<skill-name>/SKILL.md` 文件，Agent 通过比对该文件的 `description` 字段判断是否匹配当前用户意图。技能层按路径组织：

- **设计/规划路径**：brainstorming → writing-plans → executing-plans / subagent-driven-development
- **调试/质量路径**：systematic-debugging → test-driven-development → verification-before-completion
- **收尾/持续进化路径**：verification-before-completion → git-commit → finishing-a-development-branch → self-improvement
- **编排/工具路径**：dispatching-parallel-agents / workflow-runner / discovering-subagent-capabilities / find-docs
- **浏览器/前端路径**：chrome-devtools / frontend-design / chart-visualization / a11y-debugging / memory-leak-debugging
- **元技能路径**（技能管理）：skill-creator / skill-stability-review / skill-language-policy

技能层执行完毕后，将可沉淀的教训传递到记忆层。

**第四层：记忆层（Core Memory）** —— 负责学习沉淀
通过 Trae 的 `manage_core_memory` 工具管理，按类型分为：

- **Knowledge**（稳定知识：架构、领域信息）
- **Rule**（用户偏好：coding 规范、个人习惯）
- **Experience**（操作经验：排错路径、workaround）

范围分两种：user（跨项目全局通用）和 project（仅当前仓库有效），各最多 20 条。超出时系统自动淘汰最久未用的条目，因此需要主动维护。

**技术特点说明：**

- 规则与技能的激活均依赖 Trae 的 frontmatter 机制——YAML 格式的元数据头控制加载策略
- Agent 的行为约束和执行流程分布在 Rules 和 Skills 两层中，各有侧重
- 所有决策和执行都在 Trae IDE 会话中进行，依赖 IDE 内置工具集而非外部脚本

### 2.1 核心设计原则

**原则一：路由规则管指向谁，Skill 管能不能执行**

- 规则做决策（"这个 bug 该走 systematic-debugging"）
- Skill 做操作（"执行这几步来定位问题"）
- 环境前置条件放在 Skill 的 Failure Handling 中，不提升到规则层

**原则二：不把 Skill 的执行约束提升为规则**

- 只影响单个 Skill 的约束 → 放在该 Skill 内部
- 影响多条路线时 → 才考虑写入规则层

**原则三：规则做决策，Skill 做操作**

- 规则体以"如果 X，使用 Y"的决策语句为主
- 操作细节（命令、参数、路径）属于 Skill 的内容

### 2.2 完整体系一览

#### 五层核心体系（开发流水线）

| 层                        | 包含组件                                                                                                                                             | 职责                         |
| :----------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------- |
| **基础设施层**（6 个 Metaskill） | self-improvement / creating-trae-rules / skill-creator / skill-stability-review / skill-language-policy / discovering-subagent-capabilities      | 维护系统本身——学习沉淀、规则管理、Skill 管理 |
| **护栏层**（8 条 Rule）        | 5 条 alwaysApply + 3 条条件触发                                                                                                                        | 路由决策、行为约束、环境处理             |
| **设计/规划层**（2 个 Skill）    | brainstorming → writing-plans                                                                                                                    | 需求模糊时先设计，设计稳定后拆计划          |
| **执行层**（7 个 Skill）       | executing-plans / subagent-driven-development / workflow-runner / TDD / systematic-debugging / dispatching-parallel-agents / using-git-worktrees | 按计划执行、调试定位、测试驱动            |
| **验证/审查层**（3 个 Skill）    | verification-before-completion → requesting-code-review → receiving-code-review                                                                  | 证据化验证、独立审查、反馈落地            |
| **收尾层**（2 个 Skill）       | git-commit → finishing-a-development-branch                                                                                                      | 规范提交、分支收尾                  |

#### 路由流程（S/M/L 三级路径）

| 级别         | 路由路径                                                                      | 适用场景             |
| :--------- | :------------------------------------------------------------------------ | :--------------- |
| **S（小任务）** | 实现 → verification → finishing-branch                                      | ≤3 文件、机械变更、无风险触发 |
| **M（中任务）** | writing-plans → executing-plans/subagent-driven → 验证 → 审查 → 再验证 → 提交 → 收尾 | 4-10 文件、非平凡但设计明确 |
| **L（大任务）** | brainstorming → \[进入 M 路径]                                                | 跨模块、需求模糊、架构变更    |

#### 工具层 / 专项 Skill（13 个独立可插拔）

| 类别           | Skill 列表                                                                      |
| :----------- | :---------------------------------------------------------------------------- |
| **浏览器调试**    | chrome-devtools / a11y-debugging / memory-leak-debugging / debug-optimize-lcp |
| **前端/设计**    | frontend-design / visual-brainstorming                                        |
| **图表**       | chart-visualization                                                           |
| **搜索/文档**    | everything-search / find-docs                                                 |
| **中文/国内**    | chinese-copywriting / chinese-git-workflow                                    |
| **故障排查**     | troubleshooting                                                               |
| **Agent 架构** | agent-blueprint-architect                                                     |

***

## 三、Rules 规则层详解

### 3.0 规则在 Trae IDE 中的工作机制

本项目的规则文件均存放在 `.trae/rules/` 目录下，使用 YAML frontmatter 控制加载行为。Trae IDE 支持四种规则激活模式：

| 激活模式                  | frontmatter 配置                         | 加载时机                  | 适用场景              |
| :-------------------- | :------------------------------------- | :-------------------- | :---------------- |
| **Always Apply**      | `alwaysApply: true`                    | 每次新对话自动加载             | 全局行为约束（提问边界、升级护栏） |
| **Intelligent Apply** | `alwaysApply: false` + 设 `description` | Agent 根据语义匹配到相关场景时    | 场景指导（路由规则、收尾门禁）   |
| **Specific File**     | `alwaysApply: false` + 设 `globs`       | 用户操作的文件匹配 glob 模式时    | 文件类型专属规则          |
| **Manual Only**       | `alwaysApply: false` + 无 description   | 用户通过 `#Rule 规则名` 手动引用 | 极少使用的专项指南         |

**规则设计质量标准**（参见 `creating-trae-rules` 技能）：

- description 不超过 250 字符：过长会降低 Agent 匹配精度
- 规则文件不超过 50 行：超出说明职责不聚焦，应考虑拆分
- alwaysApply 文件行数从严：建议不超过 30 行，只承载一个独立关注点
- 禁止为压缩行数而删除可操作内容

此外，Trae 还支持**模块级规则**：在子模块目录下创建 `.trae/rules/` 或 `AGENTS.md`，仅当用户提到该模块文件时触发。规则嵌套最多三层。

### 3.1 alwaysApply 规则（全局护栏）

这五类规则每次对话自动加载，确保 Agent 在任何场景下都遵守基本行为规范与路由决策：

| 规则文件                                | 职责        | 一句话概括                    |
| :---------------------------------- | :-------- | :----------------------- |
| **change-proposal-threshold.md**    | 变更提议自检    | 想改规则/Skill 之前，先自问"值不值得改" |
| **question-threshold.md**           | 提问边界控制    | 定义哪些情况下必须问用户、哪些绝对不能问     |
| **forced-escalation-guardrails.md** | S 级任务强制升级 | 7 类高风险场景，严禁按小任务处理        |
| **terminal-execution-stability.md** | 终端操作纪律    | 终端的本质是取证工具，不是猜谜工具        |
| **skill-routing-and-execution-path.md** | 核心路由    | T-Shirt 分档 + 路由到正确技能，始终加载确保分类规则不缺失 |

#### 3.1.1 change-proposal-threshold：变更提议阈值

> **痛点解决：** Agent 不再随意建议重构/改规则/换方案。

这是一个五维自检矩阵：

| 维度        | 自问                | 否定结论         |
| :-------- | :---------------- | :----------- |
| **问题明确性** | 这是一个具体的、重复出现的痛点吗？ | 否 → 不改       |
| **影响面**   | 影响多个工作流或节省多轮交互？   | 否 → 不值得      |
| **维护成本**  | 改动的维护成本 > 解决的问题？  | 是 → 不改       |
| **风险**    | 会破坏现有工作流或制造歧义？    | 是 → 附带风控方案再提 |
| **替代方案**  | 有更简单的路径吗？         | 有 → 走简单路径    |

如果净收益明确 → 直接提案；边际 → 仅作为观察提及；负面 → 内部消化，不提。

#### 3.1.2 question-threshold：提问阈值

> **痛点解决：** Agent 不再无休止地问问题打断用户，也不再自作主张导致灾难。

**必须问（MUST Ask）的场景：**

- 歧义意图：请求有两种以上合理解释，且代码库无法区分
- 未知外部依赖：涉及项目中不存在的技术/工具/服务
- 范围不明确：缺乏边界（如"优化性能"但没有目标指标）
- 项目外修改：任务涉及用户未提到的项目外文件
- 业务知识依赖：答案依赖代码库中未记录的领域知识

**禁止问（MUST NOT Ask）的场景：**

- 答案在代码库中
- 只有一条合理路径
- 选错可以一键回滚且无副作用
- 遵循项目已有惯例即可
- 用户已提供足够信息

#### 3.1.3 forced-escalation-guardrails：强制升级护栏

> **痛点解决：** 核心配置/安全/CI-CD 等高风险任务不会被当作"小修改"草率处理。

以下 7 类场景**严禁当作 S（Small）任务**，最低 M（Medium）：

1. 修改核心配置文件（package.json、数据库 schema、全局状态管理）
2. 修改公共 API、共享组件、被其他模块依赖的接口
3. "简单"bug 但根因未经证据证实（必须先走 systematic-debugging）
4. 有可预见的副作用或回归风险（必须先走 TDD）
5. 认证/授权/安全敏感逻辑
6. CI/CD 流水线、部署脚本、Dockerfile、基础设施代码
7. 破坏性操作（数据迁移、批量删除、文件系统操作、数据库 schema 变更）

#### 3.1.4 terminal-execution-stability：终端执行稳定性

> **痛点解决：** Agent 不再凭"看起来成功"下结论，不再用复杂 shell 技巧代替稳定证据。

核心纪律：

- 可读证据 > 巧妙的 shell：优先简单命令 + IDE 工具
- 短检查用阻塞模式，服务器用非阻塞
- 长输出写文件再检查，不依赖终端截断输出
- IDE 工具优先于终端解析（Read > Grep > 终端）
- 不猜：输出丢失或歧义时，缩小范围重跑

### 3.2 条件触发规则（智能匹配）

| 规则文件                                    | 触发场景       | 职责                          |
| :-------------------------------------- | :--------- | :-------------------------- |
| **review-and-completion-gates.md**      | 任务临近完成     | 收尾门禁执行顺序编排                  |
| **environment-resilience.md**           | MCP 工具连接失败 | 优雅降级链（重试→终端替代→报告）           |
| **port-conflict-recovery.md**           | 端口冲突/僵尸进程  | Windows 端口恢复流程              |

#### 3.2.1 skill-routing-and-execution-path：核心路由（alwaysApply）

> 此规则现已从条件触发升级为 `alwaysApply: true`，确保任何代码变更前都先执行 T-Shirt 分类，避免漏分类导致的错误路由。

这是整个系统的**交通枢纽**。它通过 T-Shirt Sizing 对任务分档，再根据任务类型路由到正确的技能：

**T-Shirt 四维判定矩阵：**

| 维度   | S（小）    | M（中）     | L/XL（大）      |
| :--- | :------ | :------- | :----------- |
| 文件范围 | ≤3 个文件  | 4-10 个文件 | 跨模块/多系统      |
| 变更性质 | 机械/已知逻辑 | 非平凡但设计明确 | 需求模糊/架构变更    |
| 风险等级 | 无强制升级触发 | 有触发但变更明确 | 有触发 + 架构不确定性 |
| 预期节奏 | 单次专注通过  | 需要多轮迭代   | 设计→拆分→实现     |

**判定规则（本次修复的核心）：**
- **四维不一致时**：取最大的 T-Shirt 尺寸，而非"最高风险维度"（例：文件范围=S、变更性质=M、风险等级=M、预期节奏=S → 最终=M）
- **无法判定时**：无法就某一维度下结论时，默认取该维度最大值，确保安全
- **Module 定义**：以独立目录边界为一个模块（如 `src/auth/`、`src/api/`），测试目录不计为独立模块
- **测试文件计数**：测试文件计入文件数（如 2 个实现文件 + 2 个测试文件 = 4 文件 → M）
- **Guardrails 优先**：Forced Escalation Guardrails 优先于 Exception to Escalation；先评四维，再交叉检查 Guardrails，最终分类取较大值

**例外机制**：即使是 4+ 文件或跨模块，若纯属机械操作（复制微调、平凡重命名、类型修复、全局路径更新），仍按 S 处理。但触碰 Guardrails 则最低 M。

**执行中重分类**：分类可在执行过程中重新评估。向上重分类（S→M, M→L）为**强制**，发现更复杂时必须立即切换路径；向下重分类为**可选**，不强制。

**技能路由表（核心映射）：**

| 任务类型          | 路由目标                        | 替代方案（不推荐）    |
| :------------ | :-------------------------- | :----------- |
| 需求模糊/架构设计     | brainstorming               | 直接实现（会返工）    |
| Bug/测试失败/构建失败 | systematic-debugging        | 猜修复（越修越坏）    |
| 行为变更/回归风险     | test-driven-development     | 无测试实现（风险不可控） |
| 设计明确/需任务拆分    | writing-plans               | 临时编码（漏边界）    |
| 用户修正/新发现      | self-improvement            | 忽略教训（下次还犯）   |
| 多角色编排         | workflow-runner             | 单个 skill 硬撑  |
| 并行只读分析        | dispatching-parallel-agents | 逐个执行（效率低）    |

#### 3.2.2 review-and-completion-gates：审查与收尾门禁

**痛点解决：** 大任务收尾不会被跳过，但小任务也不会被流程压死。

固定执行顺序（M/L 任务）：

```
1. verification-before-completion      ← 自验证
2. requesting-code-review              ← 请求独立审查
3. receiving-code-review               ← 处理审查反馈（若有）
4. verification-before-completion      ← 修复后重验证（若有修复）
5. git-commit                          ← 提交修复（若有修复）
6. finishing-a-development-branch      ← 分支收尾
```

S 任务直接跳步骤 2-5（即从步骤 1 直接到步骤 6），走快速通道。S 路径在 verification 通过后直接提交并附加收尾指导。

内置两个关键门禁：

- **Knowledge Promotion Gate**：收尾时自动检查是否有可沉淀的教训。"持久"定义为同一分支中出现 ≥2 次，或单次非平凡发现（如未文档化的环境坑）。满足条件则调用 self-improvement 写入核心记忆。
- **Proactive Review Gate**：M/L 任务收尾时快速扫描系统状态，发现可优化的规则/skill 覆盖缺口

#### 3.2.3 环境降级与端口恢复

| 机制                         | 问题              | 方案                                     |
| :------------------------- | :-------------- | :------------------------------------- |
| **environment-resilience** | MCP 工具连接超时/失败   | 重试1次 → PowerShell 替代 → 报告局限            |
| **port-conflict-recovery** | EADDRINUSE/端口被占 | netstat 查 PID → taskkill → 确认端口释放 → 重试 |

***

## 四、Skills 技能层详解

### 4.0 技能在 Trae IDE 中的工作机制

每个技能对应一个 `skills/<skill-name>/SKILL.md` 文件，使用 YAML frontmatter 定义元数据，正文定义执行协议。Agent 通过以下方式触发技能：

**自动触发（推荐）**：Agent 收到用户请求后，遍历所有可用 Skill 的 `description` 字段，匹配则自动加载该 Skill 的完整指令。这是最常用的触发方式。

**手动触发**：用户或上游流程通过 `Skill` 工具显式调用指定 Skill。

**中文触发短语设计**：本项目的每个 Skill 的 `description` 均包含中英双语触发短语，确保中文用户使用自然语言时也能精准匹配。例如：

- `systematic-debugging`：description 中包含 "逐步排查""为什么失败""先定位原因""不要先猜修复"
- `writing-plans`：description 中包含 "写实现计划""拆任务""先规划再写代码"
- `git-commit`：description 中包含 "帮我提交""生成提交信息""提交当前修改""按规范提交"
- `verification-before-completion`：description 中包含 "确认真的修好了""提交前再验证一下""不要没跑就说完成"

这种设计策略称为 **Agent 优先原则**：description 面向 Agent 的语义匹配优化，确保机器可读性和触发稳定性，同时保留中文自然语言入口。

每个 SKILL.md 遵循固定的模板结构：name/description → Do Not Use（边界声明）→ Input Contract（输入契约）→ Execution Protocol（执行协议）→ Failure Handling（失败处理）→ Output Contract（输出契约）→ Integration（上下游衔接）。这种**契约式设计**确保每个技能的行为可预测、可验证、可拼接。

### 4.1 设计/规划路径（Design & Planning Pipeline）

这是从**模糊想法到可执行计划**的完整流水线，按以下阶段依次推进：

1. **模糊想法** → 进入 brainstorming
2. **brainstorming** → 输出设计结论（内联摘要或规格文件）
3. **设计结论** → 进入 writing-plans
4. **writing-plans** → 输出执行计划
5. **执行计划** 分两个出口：
   - **executing-plans**（当前会话顺序执行，每 3 个任务设批审查点）
   - **subagent-driven-development**（子代理独立执行 + 两层审查）

- 适用条件：executing-plans 用于环境不支持子代理或任务耦合度高时；subagent-driven-development 用于环境支持子代理且任务独立时

#### brainstorming：头脑风暴

- **职责**：把模糊需求澄清为可执行的设计方案
- **关键设计**：每次只问一个问题 + 优先选择题 + 展示视觉原型 + YAGNI 严控范围
- **输出**：内联设计摘要（默认）或规格文件（复杂场景）
- **下游**：writing-plans / 直接实现 / 结束于设计结论

#### writing-plans：编写计划

- **职责**：把稳定设计转化为分步执行计划
- **关键设计**：假设下游执行者零上下文，显式写出文件路径、验证命令、预期结果
- **禁止项**：TBD/TODO/"类似任务 N"等占位符
- **Context Payload**：向上游收集架构决策、排除路径、残余风险，传递给下游

#### executing-plans：顺序执行计划

- **职责**：在当前会话中按计划逐任务执行 + 每 3 个任务设批审查点
- **适用条件**：环境不支持可靠实现子代理，或任务间耦合度高

#### subagent-driven-development：子代理驱动开发

- **职责**：每个独立任务派一个全新子代理执行，附带规约审查 + 代码质量审查两层关卡
- **核心原则**：一次只推进一个任务 + 任务间不共享上下文 + 审查不通过不前进
- **失败降级**：子代理不满足条件时，回退到 executing-plans

### 4.2 调试/质量路径（Debugging & Quality Pipeline）

发现问题后依次推进：

1. **发现问题** → 进入 systematic-debugging
2. **systematic-debugging** → 输出根因确认结果
3. **根因确认** → 实施修复
4. **修复完成** → 进入 verification-before-completion
5. **验证通过后**，M/L 任务可选分支：requesting-code-review → receiving-code-review（处理审查反馈后重走第 4 步）

#### systematic-debugging：系统化调试

- **核心原则**：根因调查完成前，不提修复方案
- **执行协议**：读症状 → 稳定复现 → 缩小范围 → 形成假设 → 验证 → 修复 → 确认
- **禁止模式**：看到错误直接猜修复、凭经验跳过证据收集

#### test-driven-development：测试驱动开发

- **职责**：行为变更 + 回归风险场景，先写测试再实现
- **适用场景**：行为变更、bug 修复、现有测试覆盖不足

#### verification-before-completion：完成前验证

- **核心原则**：没有新鲜证据，就不能声称完成
- **执行协议**：先定义"要证明什么"→ 运行对应的验证 → 读取完整结果 → 基于证据下结论
- **红线清单**："应该没问题"、"大概没 bug"、"我很自信"——均属未经验证的断言

#### requesting-code-review / receiving-code-review：代码审查

- 请求审查 → 处理反馈，形成完整闭环
- receiving-code-review 的核心态度：审查意见是技术输入，不是必须盲从的指令

### 4.3 收尾/持续进化路径

按以下阶段依次推进：

1. **完成任务** → 进入 verification-before-completion
2. **verification-before-completion** → 验证通过后进入 git-commit
3. **git-commit** → 提交完成后进入 finishing-a-development-branch
4. **finishing-a-development-branch** → 收尾过程中触发 self-improvement
5. **self-improvement** → 将教训沉淀为持久知识（核心记忆 / 项目规则 / 新 Skill）

#### git-commit：提交管理

- 支持 Conventional Commits 格式
- **混合格式**：type 英文 + scope/body 中文（面向中国团队），例如 `fix(路由规则): 修正 T-Shirt Size 矩阵的 3 个结构缺陷`
  - type 保持英文确保工具兼容性（semantic-release、changelog 自动生成等）
  - scope、description、body 使用中文，降低团队沟通成本
- **粒度标准**：单原子变更一笔提交；多文件关联变更用 body 列出变更点；松散组合变更用 body 逐项列出
- 安全协议：不修改 git config、不 --no-verify、不 force push、不提交凭据

#### finishing-a-development-branch：分支收尾

- 提供 4 个选项：本地合并 / 创建 PR / 保持现状 / 丢弃
- 必须先确认验证结果，再给选项
- 非 GitHub 平台（Gitee/GitLab/Coding）走 `chinese-git-workflow` 进行远程配置和 PR/MR 创建
- 支持国内 Git 平台：`finishing-a-development-branch` 通过 `git remote -v` 检测远程地址后自动分流（github.com 走 `gh` CLI，其他走 web UI）

#### self-improvement：自我进化

- **职责**：将开发过程中发现的教训、修正、最佳实践沉淀为持久知识
- **四类触发**：命令失败 / 用户纠正 / 最佳实践发现 / 知识盲区
- **三个输出路径**：核心记忆（Knowledge/Rule/Experience）→ 项目规则 → 新 Skill
- **记忆维护**：提供完整的整合审计五步流程（枚举→分类→合并→删除→验证）

### 4.4 编排/工具路径

| 技能                                    | 职责                                 | 亮点                             |
| :------------------------------------ | :--------------------------------- | :----------------------------- |
| **dispatching-parallel-agents**       | 并行派发只读/分析任务                        | 预检测可用子代理类型、结果聚合交叉验证            |
| **workflow-runner**                   | YAML 多角色编排仿真                       | 支持 DAG 依赖、角色目录、多轮协作            |
| **discovering-subagent-capabilities** | 动态发现可用子代理                          | 不硬编码代理名，读 system prompt 的 enum |
| **find-docs**                         | 检索官方技术文档                           | 通过 Context7 查询框架/库/SDK 文档      |
| **chinese-git-workflow**              | 国内 Git 平台（Gitee/GitLab/Coding）远程配置 | 按需手动调用，提供平台专用 URL、SSH 和镜像同步命令  |
| **chinese-copywriting**               | 中文技术文档排版与写作规范                      | 自动处理中英文混排、全角半角、标点规范            |

### 4.5 浏览器/前端调试路径

| 技能                        | 职责                     | 工具链                     |
| :------------------------ | :--------------------- | :---------------------- |
| **chrome-devtools**       | 浏览器自动化/调试              | Chrome DevTools MCP     |
| **frontend-design**       | 前端 UI 设计/美化            | React/Vue/HTML/CSS      |
| **chart-visualization**   | 数据可视化图表生成              | 本地 JS 脚本生成图片            |
| **a11y-debugging**        | 可访问性审计                 | Chrome DevTools a11y 工具 |
| **debug-optimize-lcp**    | LCP/Core Web Vitals 优化 | Performance trace       |
| **memory-leak-debugging** | JS/浏览器内存泄漏排查           | Heap snapshot + memlab  |

### 4.6 元技能路径（技能管理）

| 技能                         | 职责             | 关键工具                                   |
| :------------------------- | :------------- | :------------------------------------- |
| **skill-creator**          | 创建/修改/审查 Skill | quick\_validate.py                     |
| **skill-stability-review** | 审查 Skill 包稳定性  | review\_skills.py（888 行，16 种审查维度）      |
| **skill-language-policy**  | 定义仓库级语言策略      | English-Required / Chinese-Retained 分层 |

**skill-language-policy 的核心决策框架**：仓库中的 Skill 文件采用"机器层英文 + 用户层中文"的分层策略——

- **English-Required 层**：frontmatter 元数据（name/description）、工具调用参数、合约接口、代码示例——这些字段面向机器解析，强制使用英文
- **Chinese-Retained 层**：流程说明、失败处理、使用场景举例、输出契约正文——这些字段面向中文用户理解，保留中文
- 不以"全英文显得专业"或"全中文便于阅读"走极端，而是按受众决定语言

***

## 五、完整工作流：从需求到上线

### 5.1 功能开发完整流（M/L 级别）

**阶段一：路由分派（Step 0 → Step 1）**

用户提出需求后，由 `skill-routing-and-execution-path` 进行 T-Shirt Size 匹配与路由分派：

- 如果涉及 7 类高风险 → `forced-escalation-guardrails` 拦截 S→M
- 如果需求模糊 → 路由到 brainstorming
- 如果涉及行为变更 → 路由到 test-driven-development
- 如果涉及 bug → 路由到 systematic-debugging
- 如果需求明确且复杂 → 路由到 writing-plans

**阶段二：设计路径**

1. **brainstorming**：探索项目上下文 → 提供视觉伴侣（可选）→ 提出澄清问题（一次一个）→ 提出 2-3 种方案 + 推荐 → 输出设计结论/规格文件
2. **writing-plans**：确定文件结构与职责边界 → 逐任务输出（文件、步骤、验证命令）→ 自检（Spec 覆盖、占位符、类型一致性）

**阶段三：执行路径**

选择以下两种方式之一：

- **executing-plans**：加载并审查计划 → 逐任务执行（TodoWrite 跟踪）→ 每 3 个任务设批审查点
- **subagent-driven-development**：每个独立任务派子代理执行 → 两层审查（规约审查 + 代码质量审查）

**阶段四：质量门禁**

1. **verification-before-completion**：重跑测试/构建/复现路径 → 读完整结果，基于证据下结论
2. **requesting-code-review**（M/L 任务专有）：独立审查 → receiving-code-review（处理反馈）
3. **verification-before-completion**（再次）：修复后重新验证

**阶段五：收尾路径**

1. **git-commit**：分析 diff → 生成 Conventional Commit → 执行提交
2. **finishing-a-development-branch**：
   - Knowledge Promotion Gate → self-improvement（沉淀教训）
   - Proactive Review Gate（扫描系统缺口）
   - 提供 4 选项：本地合并 / 创建 PR / 保持现状 / 丢弃

### 5.2 Bug 修复流

1. 用户报告 BUG → `skill-routing` 路由到 `systematic-debugging`
2. **systematic-debugging 执行七步流程**：
   - Step 1：读症状（错误信息、堆栈、复现条件）
   - Step 2：稳定复现
   - Step 3：缩小范围（二分法、隔离法、对比法）
   - Step 4：形成假设
   - Step 5：验证假设
   - Step 6：实施修复
   - Step 7：确认（走 `verification-before-completion` 标准验证）
3. 进入收尾路径：git-commit → finishing-a-development-branch
4. 若发现非显而易见的根因 → 调用 `self-improvement` 沉淀为 Experience 记忆

### 5.3 知识积累流

开发过程中可能遇到以下四类触发场景：

- 命令失败（端口冲突、依赖缺失）
- 用户纠正了错误理解
- 发现了更好的实践方式
- 发现了知识盲区

以上任意场景触发后进入 `self-improvement`，执行以下流程：

1. **分类**：判断属于 Knowledge（稳定事实）、Rule（用户偏好）还是 Experience（操作经验）
2. **去重**：先检查是否已有相似条目 → 有则 UPDATE，不新建重复
3. **容量检查**：当前 scope 记忆数接近 20 条上限 → 先执行清理再新增
4. **选择持久化路径**：
   - Core Memory（通过 `manage_core_memory` 工具）
   - Project Rule（`.trae/rules/` 文件）
   - New Skill（通过 `skill-creator` 创建）
5. **输出格式**：
   - 分类：Core Memory / Project Rule / New Skill
   - 摘要：一句话概括
   - 应用场景：什么情况下会用

***

## 六、核心痛点与解决效果

### 痛点 1：「需求不清就开始编码」

- **现象**：用户说"帮我做个功能"，Agent 直接开写代码，写完发现理解有偏差，返工成本极高。
- **方案**：`brainstorming` 技能在前置环节拦截——需求模糊时不进入实现。通过"每次只问一个问题"+"展示 2-3 种方案"+"分节展示设计并逐段获得批准"的节奏，确保需求收敛后再进入实现。
- **效果**：返工率显著降低，设计阶段用户即确认方向。

### 痛点 2：「Agent 看到 Bug 就猜修复」

- **现象**：看到报错信息后，Agent 直接给出一段"看起来合理"的修复代码，结果掩盖了真正问题。
- **方案**：`systematic-debugging` 强制"根因调查完成前不提修复方案"——必须先稳定复现→缩小范围→形成假设→验证假设，最后才是修复。
- **效果**：修复不再靠猜，每个修复方案背后都有证据链支撑。

### 痛点 3：「大小任务一样重」

- **现象**：改个文案也要走完整审查流程，重构核心模块却因为流程长被跳过。
- **方案**：T-Shirt Sizing（S/M/L）三档分流。S 任务走快速通道（不经过 brainstorming/writing-plans，收尾跳过独立审查），M/L 任务走全流程。Forced Escalation 确保高风险任务不被当作 S 处理。
- **效果**：简单任务轻快交付，复杂任务流程完整。

### 痛点 4：「做完就算成功」

- **现象**：Agent 说"改好了"，但既没跑测试也没检查构建，出了故障才开始排查。
- **方案**：`verification-before-completion` 强制——没有新鲜证据不能声称完成。必须是"刚跑过的测试全绿"、"构建 exit 0"、"原 bug 复现路径现在通过"这类可验证结论。
- **效果**："应该没问题"这句话从词汇表中删除。

### 痛点 5：「同一个坑反复踩」

- **现象**：端口冲突的处理方法每次都是临场查，每次查完就忘，下次继续卡住。
- **方案**：`self-improvement` 将每次教训沉淀为持久知识。非显而易见的根因→存为 Experience；用户纠正的偏好→存为 Rule；架构/领域知识→存为 Knowledge。后续会话自动被注入这些记忆。
- **效果**：遇到同样的问题，Agent 可以"不用查了，上次解决过"。

### 痛点 6：「Agent 不是问太多就是问太少」

- **现象**：要么每步都问用户"这个怎么命名"，要么在安全敏感操作上自行决定。
- **方案**：`question-threshold` 规则精确划分 MUST Ask（歧义、未知依赖、项目外操作）和 MUST NOT Ask（答案在代码库、唯一路径、可回滚）的边界。
- **效果**：用户只在真正需要决策时被介入，其余时间 Agent 自行推导。

### 痛点 7：「Agent 动不动就提议重写」

- **现象**：用户说"看看这个文件"，Agent 回复"建议重构为 XXX 模式"——用户只想要一个小改动。
- **方案**：`change-proposal-threshold` 规则强制自检——五维矩阵（问题明确性/影响面/维护成本/风险/替代方案）评估后再决定是否提案。
- **效果**：Agent 不再主动提出未经评估的变更方案。

### 痛点 8：「知识随会话消失」

- **现象**：新开一个对话，Agent 对之前的坑和约定一无所知，一切从零开始。
- **方案**：Core Memory 系统 + `self-improvement` 管道。新对话启动时，IDE 自动注入 user\_scope（全局偏好）+ project\_scope（仓库专属）的记忆。同时提供记忆维护流程防止信息被自动淘汰。
- **效果**：知识跨会话持续积累，Agent 越用越"懂"项目。

### 痛点 9：「Subagent 上下文膨胀失控」

- **现象**：一个任务派给子代理，结果子代理上下文里塞了整库，输出质量下降。
- **方案**：`subagent-driven-development` 要求每个子代理只接收当前任务的完整上下文 + `writing-plans` 的 Context Payload 精选信息。大任务预先由主 Agent 拆为独立小任务，每个子代理只聚焦一小块。
- **效果**：子代理输出质量稳定，任务间边界清晰。

### 痛点 10：「MCP 工具挂了就卡死」

- **现象**：Chrome DevTools 连接失败 → Agent 不知道怎么办 → 任务卡住。
- **方案**：`environment-resilience` 提供三级降级链：重试 1 次 → PowerShell/CLI 替代 → 报告局限。`port-conflict-recovery` 覆盖端口冲突场景。
- **效果**：工具失败不意味着任务失败，总有替代方案。

### 痛点 11：「国内 Git 平台适配困难」

- **现象**：项目使用 Gitee 或私有 GitLab，但 Agent 默认走 GitHub 的 `gh` CLI 工作流，push 失败、PR 无法创建。
- **方案**：`finishing-a-development-branch` 在收尾时通过 `git remote -v` 检测远程地址——识别为 github.com 走 GitHub 标准流（`git push` + `gh pr create`），识别为 gitee.com / gitlab.com / coding.net 或其他自建平台则仅 push 后引导用户在 web UI 创建 PR/MR。`chinese-git-workflow` 作为按需调用的远程配置知识库，提供各平台的 SSH/HTTPS 地址格式和镜像同步命令。
- **效果**：无论项目托管在哪个国内平台，Agent 都能正确完成远程 push 和 PR 创建流程。

### 痛点 12：「Trae Rules 的激活机制不直观」

- **现象**：新用户写了一条 rule，但 Agent 总是不按预期触发——可能是因为忘记设 frontmatter、description 太长匹配不准、或者放错了目录层级。
- **方案**：系统内置 `creating-trae-rules` 技能，精确指导四种激活模式（alwaysApply / Intelligent Apply / Specific File / Manual Only）的 frontmatter 配置和路径规范。同时 `skill-stability-review` 提供 16 个维度的自动化审查，在规则创建阶段就发现描述超长、frontmatter 格式错误、路径超层等问题。
- **效果**：规则的正确率从"靠感觉试"变为"可验证"，description 匹配精度通过 250 字符上限约束得到保障。

***

## 七、设计亮点与最佳实践

> **本文档集中讨论"为什么这样设计"。如需完整阅读设计思路和工程权衡，请参见独立文档** **[04-design\_zh.md](./04-design_zh.md)。**

本系统经历从无到有的持续迭代，形成了以下 **7 个核心设计巧思**。此处仅列概要，详细内容（含走过哪些弯路、为什么做这些决策）已在独立文档中展开：

**7.1 Rule + Skill 双轮协同，上下游流水线化**
Rule 做决策（指向谁）、Skill 做操作（怎么做）。Skill 之间通过 `Integration` 字段声明上下游，运行时动态拼接为流水线。通过 Context Payload 精炼传递设计上下文，避免下游丢失信息。

**7.2 深度绑定 Trae 原生能力，互补不冲突**
不绕过、不替代 Trae 的任何原生机制。Core Memory / `manage_core_memory` / `Task` 子代理 / `Skill` 工具 / IDE 工具集 / Rule Frontmatter——每一项都是在原生之上做增强和规范，而非替代。

**7.3 遵循官方规范，不发明格式**
不创造自己的配置格式。Rule 文件用标准 YAML frontmatter、SKILL.md 用官方 contract 模板、质量标准来自 Trae 官方文档。本系统本身即"如何按 Trae 规范创建"的最佳实践范例。

**7.4 原创决策机制：T-Shirt 分档 + 提问阈值**
Trae 原生没有的机制，来自对使用痛点的观察和归纳。T-Shirt 四维判定矩阵（文件范围 × 变更性质 × 风险等级 × 预期节奏）和五条 MUST Ask / 五条 MUST NOT Ask，填补了 Trae 默认"deduce and proceed"的空白。

**7.5 agent-blueprint-architect：稳定比花哨更重要**
不试图自动化创建 Agent，而是输出可直接复制粘贴的 Markdown 蓝图。早期尝试写 Python 脚本操作 Trae 加密数据库失败后，调整为"蓝图交付 + 手动粘贴"模式。

**7.6 Skill 内部逻辑高度优化，不是一次性提示词**
每个 Skill 包含 Input Contract / Output Contract / Do Not Use / Failure Handling / Integration 五层结构 + 红绿线清单。平均 3-5 轮迭代，git 记录可追溯。

**7.7 中文与 Windows 分层适配，Python 保可移植**
LLM 推理用英文保证稳定，用户交互用中文保证体验。分层中英文隔离策略 + PowerShell 统一语法 + Python 脚本跨平台架构。

详见 → [04-design\_zh.md](./04-design_zh.md)（设计思路与巧思，含走过的弯路和决策树）

### 7.9 稳定性验证

本系统的正确性和稳定性通过以下方式持续验证：

| 验证维度                   | 方法                                                                                                                                                | 状态                                                                                                 |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------- |
| **名称一致性**              | 逐项比对 33 个 Skill 的目录名 ↔ `name` 字段 ↔ 路由表引用 ↔ 跨 skill 交叉引用                                                                                           | 33/33 一致，50+ 引用无断裂                                                                                 |
| **路由完整性**              | 逐条验证路由表引用的技能名 → 对应 SKILL.md `name` 字段 → `description` 中无歧义                                                                                        | 10 条路由全部可达，3 对高危组合（executing/subagent、requesting/receiving review、brainstorming/writing-plans）边界清晰 |
| **Context Payload 匹配** | 验证 producers（writing-plans、systematic-debugging）产出字段是否被 consumers（executing-plans、subagent-driven-development、TDD）正确消费                            | 字段对字段完全匹配，无孤立的产出/消费字段                                                                              |
| **Rule 格式合规**          | 对照 creating-trae-rules 标准检查 frontmatter、description、alwaysApply 布尔值、行数限制                                                                          | 8 条规则全部合规，4 条 alwaysApply 均 ≤30 行                                                                  |
| **Eval 回归用例**          | 核心路径 Skill（brainstorming、writing-plans、executing-plans、subagent-driven-development、workflow-runner）提供 golden path + boundary + regression 三类 eval | 5 个 Skill × 若干用例，覆盖正确触发和拒绝触发场景                                                                     |
| **失效模式覆盖**             | 每个 Skill 的 Failure Handling 章节覆盖 3-8 种失败场景，定义明确的降级路径                                                                                              | 33 个 Skill 共约 150+ 种失效场景已定义                                                                        |
| **Git 可追溯性**           | 通过 git 提交历史追踪规则的迭代和边界校准                                                                                                                           | 多轮优化可追溯（路由规则 5 轮、收尾门禁 3 轮、护栏红线 4 轮）                                                                |

> **说明**：Eval 用例以 JSON 文件形式存放在各 Skill 的 `evals/evals.json` 中，格式为 `prompt → expected_output`，用于人工回归审查而非 CI 自动执行。如有自动执行环境后可升级为门禁。

***

## 八、演进路线与未来方向

### ✅ 已完成

- 规则三层体系（路由/执行/决策边界）建立
- 33 个技能的完整技能库覆盖
- Core Memory 管理系统
- Agent 自进化机制
- **Trae IDE 平台适配**：4 种 Rule 激活模式全覆盖、SKILL.md 契约化模板、Windows PowerShell 指令规范、MCP 降级链、IDE 内置工具集集成
- **中文团队适配**：Skill 中文触发短语覆盖全部技能、混合格式 Conventional Commit（type 英文 + body 中文）、国内 Git 平台自动分流（Gitee / GitLab / Coding）、技能语言分层策略（English-Required / Chinese-Retained）、中文技术文档排版规范

### 🔄 持续优化

- 规则去重与精简（已进行多轮）
- 技能边界校准（排查现有技能分类是否准确）
- 记忆管理自动化

### 🔭 展望

- 更智能的任务拆分（从 T-Shirt 到颗粒度自适应）
- 技能评价与淘汰机制（哪些技能真正被高频使用）
- Agent 工作流可视化（当前流程的可观测性）
- 跨项目知识共享（当前 user scope 需要用户手动确认）

***

## 九、Trae IDE 与中文团队适配要点

### 9.1 Trae IDE 平台特性适配总结

| 平台特性                                                   | 在本系统中的适配方式                                                                              | 对应组件                                                      |
| :----------------------------------------------------- | :-------------------------------------------------------------------------------------- | :-------------------------------------------------------- |
| **Rule Frontmatter**                                   | 四种激活模式精确控制规则加载                                                                          | 全部 8 个规则文件                                                |
| **SKILL.md 契约**                                        | 标准化的 SKILL.md 模板（name/description → Input → Execution → Failure → Output → Integration） | 全部 33 个技能                                                 |
| **`manage_core_memory`** **工具**                        | Knowledge / Rule / Experience 分类存储 + 容量管理                                               | self-improvement 技能                                       |
| **`Task`** **子代理**                                     | Pre-flight 预检 + 单次分派 + 四态返回                                                             | subagent-driven-development / dispatching-parallel-agents |
| **`Skill`** **工具**                                     | Agent 自动匹配 description 触发技能                                                             | 全部技能                                                      |
| **`RunCommand`** **/ PowerShell**                      | Windows 原生终端执行，统一使用 PowerShell 语法                                                       | terminal-execution-stability 规则                           |
| **`Read`** **/** **`Write`** **/** **`SearchReplace`** | IDE 内置文件操作，优于外部脚本                                                                       | 全部技能                                                      |
| **`SearchCodebase`** **/** **`Grep`** **/** **`Glob`** | 代码库语义搜索和文件匹配                                                                            | systematic-debugging / 通用                                 |
| **MCP 工具**                                             | 优雅降级链：重试 → 终端替代 → 报告局限                                                                  | environment-resilience 规则                                 |
| **`WebSearch`** **/** **`WebFetch`**                   | 网络信息检索，中文搜索优化                                                                           | find-docs / 通用                                            |
| **`OpenPreview`**                                      | 开发服务器预览                                                                                 | visual-brainstorming                                      |
| **`GetDiagnostics`**                                   | 语言错误诊断                                                                                  | verification-before-completion / 通用                       |

### 9.2 Windows 开发环境适配

本系统运行在 Windows 环境（Trae IDE for Windows），以下适配贯穿所有组件：

- **统一 PowerShell 语法**：所有命令使用 PowerShell 兼容语法（`Select-String` 替代 `grep`、`Get-ChildItem` 替代 `ls`、`Write-Output` 替代 `echo`），禁止使用 Unix 专属 shell 构造
- **端口管理**：`netstat -ano | Select-String` 查端口占用，`taskkill /PID /F` 杀进程——封装为 `port-conflict-recovery` 规则
- **路径规范**：使用反斜杠和绝对路径，支持 Windows 长路径（`\\?\` 前缀），PowerShell 中文件路径用引号包裹避免空格截断
- **文件系统**：`Get-ChildItem -Recurse` 替代 `find`，`Select-String` 替代 `grep -r`
- **Git 适配**：`chinese-git-workflow` 技能处理 Windows 上的 Git for Windows 安装检测、SSH 配置路径（`%USERPROFILE%\.ssh\`）

### 9.3 中文团队场景适配

本系统为中文开发团队做了以下专项设计：

| 场景                | 适配设计                                                                                                                          | 对应组件                                                |
| :---------------- | :---------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------- |
| **自然语言触发**        | Skill description 内嵌中文触发短语（"帮我提交""逐步排查""按规范提交"）                                                                               | 全部 33 个技能                                           |
| **提交信息格式**        | 混合 Conventional Commit：`type` 英文 + `scope/body` 中文                                                                            | git-commit 技能                                       |
| **国内 Git 平台**     | `finishing-a-development-branch` 通过 `git remote -v` 检测 remote 类型后分流（GitHub 走 CLI，其他走 web UI）；`chinese-git-workflow` 按需提供配置命令库 | finishing-a-development-branch、chinese-git-workflow |
| **中英文混排**         | 文档使用中文撰写，技术标识符保持英文，自动处理空格和标点                                                                                                  | chinese-copywriting 技能、本文档                          |
| **技能语言分层**        | machine-facing 层（frontmatter）英文 + human-facing 层（流程描述）中文                                                                      | skill-language-policy                               |
| **中文用户提问**        | `question-threshold` 规则的中文触发场景描述，`AskUserQuestion` 支持中文选项                                                                     | question-threshold 规则                               |
| **Workspace 组织**  | `using-git-worktrees` 技能的 Windows 路径适配                                                                                        | using-git-worktrees 技能                              |
| **Chrome 浏览器自动化** | `chrome-devtools` 技能适配 Chrome 中文界面下的元素定位                                                                                      | chrome-devtools 技能                                  |
| **全流程中文交互**       | `brainstorming` / `verification-before-completion` / `writing-plans` / `executing-plans` 等核心技能的输出契约和用户交互默认使用中文                | 全部面向用户的技能                                           |

### 9.4 常见适配陷阱

**陷阱 1：description 超出 250 字符**

- 表现：写了一条详细描述规则场景的 description，但 Agent 始终不触发
- 原因：Trae 官方推荐 description 不超过 250 字符，过长会降低匹配精度
- 解决：精简到 250 字符以内，核心触发词放在开头

**陷阱 2：Windows 路径反斜杠未转义**

- 表现：在 YAML frontmatter 中写 `globs: src\components\**\*.tsx`，规则不生效
- 原因：YAML 中反斜杠需要转义或使用正斜杠
- 解决：globs 统一使用正斜杠（`src/components/**/*.tsx`）

**陷阱 3：中文描述在 skill description 中被截断**

- 表现：description 中的中文触发词在 IDE 界面显示正常但 Agent 匹配不到
- 原因：中文字符占用更多字节，实际计入字符数后可能超过 250
- 解决：description 以英文为主，中文仅作为补充触发词放在末尾

**陷阱 4：`alwaysApply: true`** **文件膨胀**

- 表现：每次对话加载变慢，Agent 响应中出现不相关的规则内容
- 原因：alwaysApply 文件超过 30 行且承担了多个职责
- 解决：拆分为多个独立规则，核心逻辑保持 alwaysApply，子场景降级为条件触发

**陷阱 5：Skill 和 Rule 内容重复**

- 表现：同一个流程说明既出现在 rule 中又出现在 skill 中，修改时需要同步两处
- 原因：违反了"规则做决策，skill 做操作"原则
- 解决：rule 中只保留决策语句和指针引用，操作细节放在 skill 中

***

## 十、快速参考

### 规则文件清单

| 文件                                  | alwaysApply | 行数   | 职责    |
| :---------------------------------- | :---------- | :--- | :---- |
| change-proposal-threshold.md        | ✅           | \~27 | 变更自检  |
| question-threshold.md               | ✅           | \~28 | 提问边界  |
| forced-escalation-guardrails.md     | ✅           | \~18 | 风险升级  |
| terminal-execution-stability.md     | ✅           | \~13 | 终端纪律  |
| skill-routing-and-execution-path.md | ✅           | \~44+ | 核心路由  |
| review-and-completion-gates.md      | ❌           | \~32 | 收尾门禁  |
| environment-resilience.md           | ❌           | \~20 | MCP降级 |
| port-conflict-recovery.md           | ❌           | \~44 | 端口恢复  |

### 技能速查表

| 路径 | 技能                             | 前置依赖      | 下游衔接                           | 替代方案                |
| :- | :----------------------------- | :-------- | :----------------------------- | :------------------ |
| 设计 | brainstorming                  | 模糊需求      | writing-plans                  | 直接实现（需评估）           |
| 设计 | writing-plans                  | 稳定设计/规格   | executing-plans                | 直接临时编码              |
| 执行 | executing-plans                | 执行计划      | verification-xxx               | subagent-driven-dev |
| 执行 | subagent-driven-dev            | 执行计划      | verification-xxx               | executing-plans     |
| 调试 | systematic-debugging           | 异常症状      | verification-xxx               | 猜修复（不推荐）            |
| 质量 | test-driven-development        | 行为变更需求    | verification-xxx               | 无测试实现（高风险）          |
| 质量 | verification-before-completion | 待验证结果     | git-commit                     | 口头声称（禁止）            |
| 收尾 | git-commit                     | 通过验证      | finishing-a-development-branch | raw git（无规范）        |
| 收尾 | finishing-a-development-branch | 完成实现      | 无                              | 不处理分支               |
| 进化 | self-improvement               | 错误/纠正/新发现 | 原流程继续                          | 忽略教训（不推荐）           |

***

> *本文档基于项目* *`.trae/`* *目录下的源代码和 git 提交历史分析生成。如需了解单个技能或规则的详细信息，可直接查看对应源文件。*
>
> ***
>
> - **极简介绍**：15 秒速览 → [01-intro\_zh.md](./01-intro_zh.md)
> - **快速上手**：简短的亮点介绍 → [02-overview\_zh.md](./02-overview_zh.md)
> - **组件速查**：各 Rule/Skill 一句话职责 → [03-components\_zh.md](./03-components_zh.md)
> - **全景详解**：本文档 —— 架构、流程、痛点、适配指南

