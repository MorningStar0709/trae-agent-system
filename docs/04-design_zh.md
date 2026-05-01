# 设计思路与巧思

> 本文档集中说明本系统的核心设计思路、工程权衡和独创机制。读完此处，你应该理解"为什么这样设计"。
>
> 快速定位：极简介绍 → [01-intro_zh.md](./01-intro_zh.md) ｜ 全景文档 → [05-architecture_zh.md](./05-architecture_zh.md)

---

## 一、设计纲领：三层分离

本系统的核心架构决策是 **Rule 做决策、Skill 做执行、Trae 原生做底座** 的三层分离。

```
用户输入
    │
    ▼
Rules（规则层）——判断"该走哪条路"
    │  ║ 路由决策（T-Shirt 分档 → 技能映射）
    │  ║ 行为约束（提问阈值、升级护栏、变更自检）
    │  ║ 环境处理（终端纪律、MCP 降级、端口恢复）
    ▼
Skills（技能层）——执行"具体怎么做"
    │  ║ 每个技能聚焦单一职责
    │  ║ 上下游通过 Integration 声明自动拼装
    │  ║ 通过 Context Payload 精炼传递设计上下文
    ▼
Trae 原生（底座层）——提供基础设施
    │  ║ Rule Frontmatter 控制加载
    │  ║ `Skill` 工具匹配 description
    │  ║ `manage_core_memory` 存记忆
    │  ║ `Task` 子代理分派
    │  ║ IDE 工具集（Read/Write/RunCommand...）
```

**为什么这样分？**
- 单体 Agent 什么都做，但什么都不精 → 拆成小技能，每个聚焦
- Agent 需要知道"什么能做"和"怎么做"是两类问题 → 规则管"什么"，技能管"怎么"
- 系统会进化，底座会升级 → 本系统只做原生之上的增量，不替代不破坏

---

## 二、七个设计巧思

### 2.1 Rule + Skill 双轮协同，上下游流水线化

**核心思路**：Rule 像交通警察判断"走哪条路"，Skill 像专业工具箱负责"怎么做"。两者各司其职，互不干扰。

**流水线协作**：Skill 之间不是孤立的——每个 Skill 的 `Integration` 字段声明上游和下游，Agent 在运行时动态拼接：

```
brainstorming → writing-plans → executing-plans → verification-before-completion → git-commit → finishing-a-development-branch → self-improvement
```

**Context Payload** 是上下游之间的"精选传递包"——只传递 Architecture / Key Interfaces / Conventions / Constraints / Uncertainties，不堆砌原始对话。下游拿到的是决策信息，不是聊天记录。

**设计价值**：单体 Agent 做不到的专业度，通过"小技能流水线"实现。每个技能聚焦单一职责，组合起来覆盖全流程。

### 2.2 深度绑定 Trae 原生能力，互补不冲突

**核心思路**：不绕过、不替代 Trae 的任何原生机制，只在之上做互补增强。

| Trae 原生 | 本系统增强 | 关系 |
|:----------|:-----------|:-----|
| Core Memory（20 条上限、自动淘汰） | `self-improvement` 主动管理记忆质量 | 互补 |
| `manage_core_memory` 工具 | 封装为 Knowledge/Rule/Experience 三层 | 增强 |
| `Task` 子代理 | 预检→分派→两层审查完整闭环 | 增强 |
| `Skill` 自动匹配 | 中英双语 description，33 个契约化 SKILL.md | 适配 |
| IDE 工具集 | 终端纪律规范 + MCP 降级 | 规范 |
| Rule Frontmatter | 4 激活模式全覆盖 + 质量标准 | 遵循 |

**设计价值**：用户安装本系统不会破坏任何 Trae 原生行为。原生记忆照常工作，原生规则照常加载——本系统是原生之上的第二层增强层。

### 2.3 遵循官方规范，不发明格式

**核心思路**：不创造自己的配置格式，完全按 Trae 官方规范编写。这意味着本系统本身就是最佳实践范例。

- Rule 文件：标准 YAML frontmatter + Markdown，四种官方激活模式
- SKILL.md：严格遵循官方推荐的 contract 模板
- 质量标准：description ≤ 250 字符、规则 ≤ 50 行、alwaysApply ≤ 30 行——均来自官方文档
- 自动化审查：`skill-stability-review` 内置 16 维审查脚本（review_skills.py，888 行），自动检查每一条 rule 和 skill 的合规性
- 三层元技能保障：`creating-trae-rules` 指导写规则、`skill-creator` 指导写 Skill、`skill-language-policy` 规范语言

**设计价值**：33 个技能 + 8 条规则本身就是"如何按 Trae 规范创建"的活教材。用户新写规则时直接参考即可。

### 2.4 原创决策机制：T-Shirt 分档 + 提问阈值

**核心思路**：这两个机制是 Trae 原生没有的，来自对 AI Agent 日常使用痛点的观察和归纳。

**T-Shirt 四维判定矩阵**：
```
文件范围 × 变更性质 × 风险等级 × 预期节奏 → S / M / L
```
评分不一致时以**最大的 T-Shirt 尺寸**为准（而非"最高风险维度"），无法判定时默认取该维度最大值以确保安全。Module 以独立目录边界定义，测试文件计入文件数。配以 Forced Escalation（7 类高风险场景严禁按 S 处理）——Guardrails 优先于 Exception，先评四维再交叉检查 Guardrails，取较大值。执行过程中支持动态重分类，发现更复杂时强制向上切换。

**提问阈值**：五条 MUST Ask + 五条 MUST NOT Ask，精确划出"该问用户"和"不该问用户"的边界。Trae 默认行为是"deduce and proceed"，本系统填补了这一空白。

**设计价值**：完全原创。不是跟随某个官方标准，而是在使用中发现问题、自己归纳方案。

### 2.5 agent-blueprint-architect：稳定比花哨更重要

**核心思路**：不试图自动化创建 Agent，而是输出用户可直接复制粘贴的 Markdown 蓝图。

**走过的弯路**：早期尝试写 Python 脚本自动写入 Trae 的加密 SQLite 数据库（`%APPDATA%\trae\ModularData\ai-agent\database.db`），发现：
1. 数据库被 IDE 独占锁定，外部写入会导致崩溃
2. 加密格式不透明，反编译风险高
3. 只跑通一次就因版本更新失效

**最终方案**：放弃自动化，改为"蓝图交付 + 手动粘贴"：

```
中文显示名 → 复制到 Trae UI 的显示名输入框
System Prompt → 复制到 Trae UI 的系统提示词输入框
英文标识 → 复制到 Trae UI 的标识符输入框
触发说明 → 复制到 Trae UI 的触发条件输入框
能力配置 → 指导用户在 UI 中勾选/取消对应开关
```

**设计价值**：诚实地适配平台限制。用户手动粘贴的成本远低于脚本崩溃的风险。

### 2.6 Skill 内部逻辑高度优化，不是一次性提示词

**核心思路**：每个 Skill 不是一次写成的提示词，而是经过 3-5 轮迭代、有 git 记录可追溯的"执行契约"。

每个 SKILL.md 包含五层结构：
- **Input Contract**：精确声明需要什么输入
- **Output Contract**：保证输出什么格式
- **Do Not Use**：边界声明，防止误触发
- **Failure Handling**：5-8 种失败场景的降级路径
- **Integration**：上下游声明，形成 DAG 依赖图

此外有 **红绿线清单**——设置"红线"（绝对禁止）和"绿线"（必须执行）。例如 `verification-before-completion` 的 6 条红线包括"应该没问题""大概没 bug"等口头承诺式表述。

**设计价值**：每个技能都是持续的工程投资，不是一次性产出。

### 2.7 中文与 Windows 分层适配，Python 保可移植

**核心思路**：LLM 推理最佳语言是英文（稳定），但中文用户需要中文交互。本系统的方案是分层隔离，不搞一刀切。

**分层中英文策略**：

| 场景 | 英文 | 中文 | 理由 |
|:-----|:-----|:-----|:-----|
| Skill description | 核心描述（机器匹配） | 触发短语（用户表达） | 匹配精度 + 自然入口 |
| Conventional Commit | type 字段 | scope + body | 工具兼容 + 团队沟通 |
| SKILL.md | frontmatter、代码示例 | 流程说明、失败处理 | 机器稳定 + 人易懂 |
| Agent 推理 | 内部推理链路 | 最终用户交互 | 推理质量 + 交互体验 |

**Windows 适配**：全部命令 PowerShell 语法，端口冲突恢复封装为独立规则，路径、文件搜索按 Windows 习惯编写。

**Python 脚本可移植架构**：不受平台依赖的工具逻辑（review_skills.py、quick_validate.py）统一用 Python 实现。Python 天然跨平台，`Path.resolve()` + `subprocess.run()` 避开 Windows 编码和路径坑。

**设计价值**：对中文用户不是"[用中文回复]"，是系统的分层中英文隔离。对 Windows 不是"加几条 PowerShell 命令"，是从架构层面确保一致的执行体验。

---

## 三、走过的弯路（失败的决策）

> 记录设计过程中的关键失败尝试，避免后来者重复踩坑。

### 自动化创建 Agent（agent-blueprint-architect 前身）

**尝试**：写 Python 脚本直接操作 Trae 本地的 `database.db`，自动写入 Agent 配置。
**失败原因**：数据库被 IDE 独占锁定？加密格式不透明？版本更新即失效。
**最终方案**：蓝图交付 + 手动粘贴。
**教训**：不要绕过平台约束去自动化。平台不开放的能力，手动就是最稳定的方案。

### Skill 与 Rule 内容重叠

**尝试**：同一套流程说明既写在 rule 中又写在 skill 中，"反正都加载了，用户多看一遍没关系"。
**问题**：改一个地方忘改另一处，两处内容逐渐不一致。
**修正**：确立"规则做决策，skill 做操作"原则，rule 只保留决策语句和指针引用，操作细节全放 skill。
**教训**：每多一个冗余副本，就多一个同步债务。

### alwaysApply 膨胀

**尝试**：把端口冲突恢复、MCP 降级等流程也设成 `alwaysApply: true`，"反正都是常用功能"。
**问题**：每次对话加载变慢，Agent 上下文被不相关的内容占据。
**修正**：降级为条件触发（`alwaysApply: false` + `description`），只在相关场景加载。
**教训**：alwaysApply 每多一行，每次对话的成本就高一分。30 行上限不是形式主义。

---

## 四、核心设计原则（备忘）

### 去重

```
Rule 中已有的内容 → Skill 中不重复
Skill 中已有的内容 → Rule 中只保留指针引用
记忆中有覆盖 → 先检查更新，不新建重复条目
```

### alwaysApply 精简

- 一条 alwaysApply 规则只承载一个独立关注点
- 超过 30 行先判断：单一关注点（保留）还是多关注点（拆分）
- 禁止为压行数删除可操作内容

### 路由规则管指向谁，Skill 管能不能执行

- 规则做决策，skill 做操作
- 环境前置条件放在 skill 的 Failure Handling 中
- 不把 skill 的执行约束提升为规则

---

> 本文档是 [05-architecture_zh.md](./05-architecture_zh.md) 章七的独立提取版，内容一致，方便单独查阅。
