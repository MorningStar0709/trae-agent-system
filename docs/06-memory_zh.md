# 记忆系统 — 双轨持久化记忆

## 概述

本项目实现了**双轨记忆系统**，将 Trae 原生的核心记忆与 MCP Memory Server 提供的持久化知识图谱相结合。

系统的工作方式如下：

当用户或 Agent 触发查询时，**核心记忆**（Trae 原生，会话级缓存）优先被检查以获得快速访问。如果核心记忆中找不到所需上下文，或者需要跨会话召回，请求会落到 **MCP 记忆**（知识图谱，持久化存储）。写入走双轨：核心记忆处理自动的会话级写入，而 MCP 记忆通过 `memory-kernel` skill 显式写入，保存需要跨会话持久化的信息。

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

`skill-routing-and-execution-path.md` 规则控制何时路由到记忆系统：

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

在开始处理已知项目任务或被问及历史上下文时：

1. 通过 `mcp_memory_search_nodes` 搜索相关关键词
2. 通过 `mcp_memory_open_nodes` 打开匹配的节点
3. 如无相关结果，正常执行任务，并考虑事后写入上下文

### 更新协议

当记忆中的信息已过时：

1. 通过 `mcp_memory_delete_observations` 移除过时观察
2. 通过 `mcp_memory_add_observations` 添加修正后的观察
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

## 冲突处理

| 冲突场景 | 处理方式 |
|:---------|:---------|
| 双轨都有相同信息 | 允许——Core Memory 是会话缓存，MCP Memory 是权威源 |
| 信息冲突 | 信任 MCP Memory（它是主动维护的）|
| MCP 中的信息已过时 | 通过 delete_observations + add_observations 立即更新 |
| MCP 不可用 | 仅回退到 Core Memory，不阻塞执行 |

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
