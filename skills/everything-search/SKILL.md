---
name: everything-search
description: Use Everything Search MCP in Trae for fast Windows local file and folder path discovery. Use when the user needs to find local files, folders, projects, PDFs, images, documents, archives, or recently modified items by name, extension, path fragment, date, or size, including Chinese requests such as 找文件, 搜索本机文件, 定位项目目录, 查找某个 PDF, 最近修改的文件, or 文件在哪. Prioritize this over default shell commands (dir/ls) or the Glob tool when searching outside the workspace, across the whole machine, or by metadata. If a workspace Glob search fails, fallback to this Skill. Do not use for semantic code search, web search, or project understanding (use the 'search' agent instead).
---

# Everything Search MCP

Use this Skill to locate local files and folders quickly through Everything Search MCP in Trae.

This Skill is not a general code search, document parser, web search, or project analysis workflow. Its job is to produce reliable local paths, then hand those paths back to the normal task workflow.

## Tool Choice

Use Everything Search MCP as a path-discovery tool, not as the default search tool for every file task. You must weigh its use against internal default tools:

| User intent | Recommended Tool / Skill |
|---|---|
| Find file/folder across the whole machine or outside workspace | Everything Search MCP |
| Find files by metadata (date, size, exact extension) | Everything Search MCP |
| Find file/folder within current workspace by name pattern | Default `Glob` tool or Everything Search MCP |
| Search inside source code or understand project structure | Default `search` agent or `SearchCodebase` tool |
| Read, summarize, convert, audit, or edit a known file | Relevant Skill or default `Read` tool |
| Batch rename, move, delete, copy, or compute custom statistics | PowerShell after confirming scope |
| Internet or official documentation lookup | Documentation / web search workflow |

Default decision rule:

```text
不知道路径或跨盘搜索 -> Everything Search MCP
工作区内找代码文件 -> Glob 工具
Glob 工具找不到文件 -> Everything Search MCP (Fallback)
要理解代码关系/内容 -> search agent / SearchCodebase
知道路径且要批处理 -> PowerShell
```

## Use This Skill

Use it when the user asks to:

- Find a local file or folder by name.
- Locate a project directory.
- Search for files by extension, such as `.pdf`, `.docx`, `.xlsx`, `.png`, `.zip`, `.py`, or `.md`.
- Find recently modified or created files.
- Locate files under a known path fragment, such as `Downloads`, `Desktop`, a drive letter, or a project name.
- Narrow many possible local files into a small candidate list.

Typical Chinese requests:

- “帮我找一下这个文件在哪”
- “全盘搜索一下这个报错日志”
- “我记得电脑里有个叫 xxx 的表格”
- “搜索本机所有 xxx.pdf”
- “定位这个项目目录”
- “工作区里搜不到，帮我在本地全局找找”
- “找最近修改的 Markdown 文件”
- “查一下桌面附近有没有这个压缩包”

Do not use it when:

- The user already gave the exact path.
- The task is to search inside file contents or source code. Use normal file/code search tools (like `SearchCodebase` or the `search` agent) instead.
- The task is to understand, summarize, convert, edit, or audit a file after it is found. First locate the path, then use the relevant Skill or default `Read` tool.
- The user is only looking for files within the current workspace that can be easily found with the `Glob` tool, unless they explicitly ask to use Everything or need metadata filtering (size/date).
- The user needs internet search or documentation lookup.
- The request could expose broad sensitive file lists without a clear target.

## MCP Tool Strategy

Use the Everything Search MCP `search` tool as a path locator.

Core parameters:

- `query`: Required search query.
- `max_results`: Keep small by default. Use 10 to 30 for exploratory searches; raise only when the user asks for broad listings.
- `match_path`: Use `true` when the user provides a directory, drive, project name, or path fragment.
- `match_case`: Usually `false`.
- `match_whole_word`: Use only when the filename term is short or ambiguous.
- `match_regex`: Use only when the user explicitly asks for regex or the pattern is clearly regex-shaped.
- `sort_by`: Use `14` for newest modified first, `12` for newest created first, `6` for largest first, and `1` for filename A to Z.

## Query Rules

Start with the narrowest query that can reasonably answer the request.

Prefer:

- Filename or distinctive phrase first.
- Extension filters when the file type is known.
- Path matching when the user mentions a folder, drive, or project.
- Date sorting for “最近”, “刚才”, “今天”, “recent”, or “latest”.

Avoid:

- Very broad queries such as `*` or `*.pdf` with hundreds of results unless the user explicitly wants a broad inventory.
- Searching the whole machine for vague words that may expose many unrelated personal files.
- Treating filename search results as proof of file contents.

## Advanced Everything Query Syntax

On Windows, the MCP query can use Everything search syntax. Prefer these patterns when they make the result narrower and safer.

Path and drive filters:

```text
D:
D:\Downloads\
"C:\Program Files\"
parent:"D:\APP\Learn"
```

File or folder only:

```text
file:
folder:
```

Extension and type filters:

```text
ext:pdf
ext:docx;xlsx;pptx
pic:
doc:
zip:
video:
```

Date filters:

```text
dm:today
dm:thisweek
dc:2026-04
dm:2026-04-01..2026-04-28
```

Size filters:

```text
size:>100mb
size:2mb..10mb
size:huge
```

Boolean and grouping:

```text
invoice ext:pdf
report|summary ext:docx
project !node_modules
<report|summary> ext:pdf
```

Name matching:

```text
startwith:README
endwith:.backup
regex:^[0-9]{4}-
```

Duplicate discovery:

```text
dupe:
sizedupe:
size:>1gb sizedupe:
```

Content searching exists in Everything through `content:`, but it is slow because file content is not indexed. Use it only after narrowing by extension, path, and date:

```text
ext:md dm:thisweek content:关键词
```

Do not use `content:` as a default code or document search strategy. For code content, use normal code search. For document extraction or conversion, locate the file first, then use the relevant document workflow.

## Windows and Trae Notes

- Requires Everything installed and Everything service running.
- If the MCP fails on Windows, check whether `EVERYTHING_SDK_PATH` points to the specific SDK DLL file, not just the SDK folder.
- For a typical Windows setup, the expected SDK DLL path is `C:\Program Files\Everything\SDK\dll\Everything64.dll`.
- Return Windows absolute paths exactly as reported.
- Keep paths in code formatting so they are easy to copy.
- Do not convert Windows paths to WSL, Unix, or URL paths unless the user asks.

## Failure Handling

- If the Everything Search MCP tool is unavailable, say that the MCP is unavailable and continue with a narrower PowerShell or Trae file-search fallback only when the target scope is safe.
- If search calls fail on Windows, check that Everything is installed, the Everything service is running, and `EVERYTHING_SDK_PATH` points to the DLL file such as `C:\Program Files\Everything\SDK\dll\Everything64.dll`.
- If no results are found, report the exact query settings used and ask for one useful narrowing or broadening clue.
- If too many results are returned, reduce `max_results`, add extension/path/date filters, or ask the user for a more specific filename fragment.
- If results include sensitive-looking or unrelated paths, show only the minimal relevant candidates and do not open or read files unless the user asks.

## MCP Configuration Reference

Recommended Trae MCP configuration when `uvx` is available:

```json
{
  "mcpServers": {
    "everything-search": {
      "command": "uvx",
      "args": [
        "mcp-server-everything-search"
      ],
      "env": {
        "EVERYTHING_SDK_PATH": "C:\\Program Files\\Everything\\SDK\\dll\\Everything64.dll"
      }
    }
  }
}
```

Use the Python module form only if the package was installed into the Python environment Trae can access:

```json
{
  "mcpServers": {
    "everything-search": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server_everything_search"
      ],
      "env": {
        "EVERYTHING_SDK_PATH": "C:\\Program Files\\Everything\\SDK\\dll\\Everything64.dll"
      }
    }
  }
}
```

## Workflow

1. Decide between tools: if the user is looking for a file inside the current workspace and the name is clear, try the `Glob` tool first. If it fails, or if the user asks for a global/metadata search, proceed to Everything Search MCP.
2. Parse the user's target: name, extension, likely folder, date clue, size clue, or project clue.
3. Build a focused `search` query.
4. Set `max_results` conservatively.
5. Use `match_path: true` only when path fragments matter.
6. Sort by modified date when the user asks for recent files.
7. Present the best matches with path, type if obvious, size, and modified time when available.
8. If there are multiple plausible matches, ask the user which one to use or choose the most likely one when context is clear.
9. After a path is selected, continue with the relevant workflow for reading, editing, converting, auditing, or opening that file.

## Output Format

When the user only asks to find files, answer in Simplified Chinese:

```markdown
找到以下候选：

| 序号 | 路径 | 备注 |
|---:|---|---|
| 1 | `C:\path\to\file.ext` | 最近修改 / 类型 / 大小 |

建议使用：`C:\path\to\file.ext`
```

When no result is found:

```markdown
没有找到匹配项。

我已尝试的搜索条件：
- `query`: ...
- `match_path`: ...

可以继续收窄或放宽的线索：
- 文件扩展名
- 大概所在目录
- 最近修改时间
- 文件名中的关键词
```

## Safety

- Do not dump large result sets by default.
- Do not expose unrelated sensitive-looking paths when the user asked for a narrow target.
- If a result list includes private-looking directories, show only the minimal path candidates needed to answer.
- Do not open, read, edit, delete, or move found files unless the user asks for that next step.
