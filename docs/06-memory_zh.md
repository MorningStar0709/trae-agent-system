# 记忆系统 — 双轨持久化记忆

## 概述

本项目实现了**双轨记忆系统**，将 Trae 原生的核心记忆与 MCP Memory Server 提供的持久化知识图谱相结合。

系统的工作方式如下：

本系统的路由规则定义了 **Step 0（记忆优先预检）** 作为所有任务的通用入口：优先查询 **MCP 记忆**（权威源，知识图谱），获取项目/模式/用户上下文。如果记忆不足以完成任务，再回退到全量文件扫描。Core Memory（Trae 原生，会话级缓存）在 MCP 不可用时作为降级备用。

双轨写入：核心记忆处理自动的会话级写入，而 MCP 记忆通过 `memory-kernel` skill 显式写入，保存需要跨会话持久化的信息。

| 维度 | 核心记忆 | MCP 记忆 |
|:-----|:---------|:---------|
| **后端** | Trae 原生 | `@modelcontextprotocol/server-memory` |
| **存储** | Trae 自动管理 | 本地 JSONL 文件 |
| **范围** | 当前会话 | 跨会话 |
| **生命周期** | 临时（会话结束即消失） | 持久化（直到主动删除） |
| **结构** | 键值观察 | 知识图谱（实体 + 关系） |
| **写入触发** | 自动（Trae 原生行为） | 显式调用 `memory-kernel` skill |
| **容量** | 每范围约 20 条 | 无限制 |
| **平台绑定** | 仅 Trae | 任意 MCP 兼容的 IDE |

## 架构

### 规则层

`skill-routing-and-execution-path.md` 规则定义了 **Step 0（记忆优先预检）** 作为所有任务的通用入口：

| 顺序 | 动作 | 角色 |
|:----|:-----|:-----|
| **Step 0** | 自动查询 MCP 记忆（权威源） | 获取项目/模式/用户上下文，避免全量扫描 |
| Step 1+ | T-Shirt 分档 → 路由到对应技能 | 正常路由流程 |

同时，以下特定场景也路由到记忆系统：

| 如果任务是... | 路由到 | 代替 |
|:--------------|:-------|:-----|
| 新会话，需要项目上下文再开始 | `memory-kernel` | 从头扫描整个项目 |
| "还记得吗"、跨会话记忆召回 | `memory-kernel` | 从当前上下文猜测 |

### 技能层

| 技能 | 角色 | 核心功能 |
|:-----|:-----|:---------|
| [`memory-kernel`](../skills/memory-kernel/SKILL.md) | 记忆执行 | MCP 记忆的读写更新协议 |
| [`self-improvement`](../skills/self-improvement/SKILL.md) | 知识提升 | 将会话中的经验沉淀为规则或记忆 |

### 工具层（MCP）

MCP Memory Server 提供以下工具：

| 工具 | 用途 |
|:-----|:------|
| `mcp_memory_create_entities` | 创建实体（名称、类型、观察） |
| `mcp_memory_create_relations` | 创建实体间的关系 |
| `mcp_memory_add_observations` | 向已有实体追加观察 |
| `mcp_memory_delete_entities` | 删除实体及其关系 |
| `mcp_memory_delete_observations` | 删除特定观察 |
| `mcp_memory_delete_relations` | 删除特定关系 |
| `mcp_memory_read_graph` | 读取整个知识图谱 |
| `mcp_memory_search_nodes` | 搜索实体 |
| `mcp_memory_open_nodes` | 按名称打开指定节点 |

## 使用方法

### 写入标准

MCP 记忆的每次写入必须遵守以下标准。详细协议见 `memory-kernel` 技能的 Writing Standard 节。

**格式**：每条观察以 `[YYYY-MM-DD]` 开头，后跟单句事实。例如：`[2025-05-01] 项目技术栈为 Node.js + React`。

**写入门槛**：
- ✅ 项目架构、技术栈、关键设计决策
- ✅ 影响多个文件的规范（命名、模式、工作流）
- ✅ 跨会话持续的用户偏好
- ✅ 可复用的解决方案、重复错误模式、根因
- ❌ 文件树结构（随时可以重新扫描）
- ❌ 用户刚在当前消息中提供的信息
- ❌ 敏感信息（密钥、密码、Token）

**实体粒度**：每个项目只建一个项目实体，追加观察而非重复创建。每个独立解决方案建一个模式实体。

### 写入协议

只持久化跨会话有用的信息：

1. **搜索**已有实体（`mcp_memory_search_nodes`）
2. **创建**新实体（`mcp_memory_create_entities`）
3. **追加**观察（`mcp_memory_add_observations`）
4. **关联**实体（`mcp_memory_create_relations`）

**实体命名**：`snake_case`，项目相关实体以项目名称为前缀。

**实体类型**：

| 类型 | 示例 |
|:-----|:------|
| `project` | `trae_agent_enhancements` — 技术栈、架构、约定 |
| `pattern` | `known_solutions` — 可复用的解决方案和决策 |
| `preference` | 用户偏好（命名风格、工具偏好） |
| `profile` | 用户画像（姓名、背景、兴趣） |

### 读取协议

作为 **Step 0 通用预检**的一部分，在任意任务开始时（而非仅"已知项目"）：

1. 通过 `mcp_memory_search_nodes` 搜索相关关键词（项目名、领域关键词、实体类型）
2. 通过 `mcp_memory_open_nodes` 打开匹配的节点获取完整观察
3. 判定上下文是否充足：
   - **充足**：跳过项目级全量文件扫描，只读 1-2 个关键文件验证版本变更
   - **不足或为空**：正常执行任务（触发 T-Shirt 分档和文件扫描），结束后写入新发现
4. MCP 工具不可用时静默降级，不阻塞执行

### 更新协议

当记忆中的信息已过时：

1. 通过 `mcp_memory_delete_observations` 移除过时观察（按时间戳前缀 `[YYYY-MM-DD]` 识别）
2. 通过 `mcp_memory_add_observations` 添加修正后的观察，使用当前日期 `[YYYY-MM-DD]`
3. 除非整个节点无效，否则不要删除并重建实体

## 初始化

### 1. 配置 MCP Server

在 Trae 设置 → MCP Servers 中添加：

```json
{
  "mcpServers": {
    "memory": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "D:/AppData/Memory/memory.jsonl"
      }
    }
  }
}
```

### 2. 播种知识图谱

`memory-kernel` 技能支持初始播种。推荐为每个项目创建以下实体：

- **项目实体**：名称、描述、技术栈、架构、约定
- **画像实体**：用户身份与偏好
- **模式实体**：可复用的解决方案和架构决策
- **已知解决方案实体**：重复出现的问题-解决对

### 3. 验证

打开一个新会话，询问项目相关问题。系统应从 MCP 记忆获取上下文，而非从头扫描整个项目。

## 冲突处理与降级

| 场景 | 处理方式 |
|:----|:---------|
| 双轨都有相同信息 | 允许——Core Memory 是会话缓存，MCP Memory 是权威源 |
| 信息冲突 | 信任 MCP Memory（它是主动维护的）|
| MCP 中的信息已过时 | 通过 delete_observations + add_observations 立即更新 |
| **MCP 工具未注册** | 预检检测到后直接跳 Level 2，不浪费调用 |
| **MCP 不可用（运行时故障）** | 降级到 Level 1（Core Memory）；Core Memory 也不可用则 Level 2 |
| **两套都不可用** | Level 2：根据任务类型选择最轻量的兜底路径——单文件任务读当前文件，概述类读 docs，实现类才全量扫描，模糊需求问用户，对话直接回复。不硬编码"文件扫描"。 |

## 集成关系

- **`memory-kernel`**：对 MCP 记忆进行读写的主要执行技能
- **`self-improvement`**：从 self-improvement 沉淀的持久经验也应写入 MCP 记忆
- **`discovering-subagent-capabilities`**：相邻——记忆工具是平台级能力，非子 agent 级

## 与现有模式的关系

双轨记忆系统扩展了现有的 Memory-Intent-Trigger 架构：

| 模式 | 现在的工作方式 |
|:-----|:--------------|
| Memory | 同时存储在 Core Memory（快速访问）和 MCP Memory（持久图）|
| Intent | 通过 `memory-kernel` 读取协议解析——推断前先查记忆 |
| Trigger | 通过 `skill-routing-and-execution-path.md` 路由——新增了记忆操作行 |
