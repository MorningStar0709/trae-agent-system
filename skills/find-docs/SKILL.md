---
name: find-docs
description: Retrieve current documentation, API references, configuration guidance, migration notes, and code examples for developer technologies through Context7 in Trae. Use when the user asks about a library, framework, SDK, API, CLI tool, or cloud service, including Chinese requests such as 怎么配置, 如何使用, 报错原因, 版本迁移, API 参数, or 安装步骤. Prefer this over general web search for developer documentation.
---

# Documentation Lookup

Retrieve current documentation and code examples for any library using the Context7 CLI.

## Do Not Use

Do not use this skill when:

- The task is refactoring, writing scripts from scratch, business-logic debugging, code review, or general programming concepts.
- The user asks about project-specific code behavior that can be answered by reading local files and does not require current external documentation.
- The user wants non-developer web research, news, prices, laws, products, or general search results.
- The request would require sending secrets, credentials, private code, or proprietary data to the documentation query.
- Context7 quota or network access is unavailable and the user has not accepted an outdated fallback answer.

Make sure the CLI is up to date before running commands:

```powershell
npx ctx7@latest --version
```

Run directly without installing:

```powershell
npx ctx7@latest <command>
```

## Workflow

Two-step process: resolve the library name to an ID, then query docs with that ID.

```powershell
# Step 1: Resolve library ID
npx ctx7@latest library <name> <query>

# Step 2: Query documentation
npx ctx7@latest docs <libraryId> <query>
```

You MUST call `ctx7 library` first to obtain a valid library ID UNLESS the user explicitly provides a library ID in the format `/org/project` or `/org/project/version`.

IMPORTANT: Do not run these commands more than 3 times per question. If you cannot find what you need after 3 attempts, use the best result you have.

## Step 1: Resolve a Library

Resolves a package/product name to a Context7-compatible library ID and returns matching libraries.

```powershell
npx ctx7@latest library React "How to clean up useEffect with async operations"
npx ctx7@latest library Next.js "How to set up app router with middleware"
npx ctx7@latest library Prisma "How to define one-to-many relations with cascade delete"
```

On Windows Trae, prefer `npx ctx7@latest ...` so the latest CLI runs without relying on a stale global install. Use PowerShell syntax for environment variables and command examples. If the user asks in Chinese, keep the query specific but preserve official library names and English API terms, then answer the user in Simplified Chinese unless they requested another language.

Always pass a `query` argument — it is required and directly affects result ranking. Use the user's intent to form the query, which helps disambiguate when multiple libraries share a similar name. Do not include any sensitive or confidential information such as API keys, passwords, credentials, personal data, or proprietary code in your query.

### Result fields

Each result includes:

- **Library ID** — Context7-compatible identifier (format: `/org/project`)
- **Name** — Library or package name
- **Description** — Short summary
- **Code Snippets** — Number of available code examples
- **Source Reputation** — Authority indicator (High, Medium, Low, or Unknown)
- **Benchmark Score** — Quality indicator (100 is the highest score)
- **Versions** — List of versions if available. Use one of those versions if the user provides a version in their query. The format is `/org/project/version`.

### Selection process

1. Analyze the query to understand what library/package the user is looking for
2. Select the most relevant match based on:
   - Name similarity to the query (exact matches prioritized)
   - Description relevance to the query's intent
   - Documentation coverage (prioritize libraries with higher Code Snippet counts)
   - Source reputation (consider libraries with High or Medium reputation more authoritative)
   - Benchmark score (higher is better, 100 is the maximum)
3. If multiple good matches exist, acknowledge this but proceed with the most relevant one
4. If no good matches exist, clearly state this and suggest query refinements
5. For ambiguous queries, request clarification before proceeding with a best-guess match

### Version-specific IDs

If the user mentions a specific version, use a version-specific library ID:

```powershell
# General (latest indexed)
ctx7 docs /vercel/next.js "How to set up app router"

# Version-specific
ctx7 docs /vercel/next.js/v14.3.0-canary.87 "How to set up app router"
```

The available versions are listed in the `ctx7 library` output. Use the closest match to what the user specified.

## Step 2: Query Documentation

Retrieves up-to-date documentation and code examples for the resolved library.

```powershell
ctx7 docs /facebook/react "How to clean up useEffect with async operations"
ctx7 docs /vercel/next.js "How to add authentication middleware to app router"
ctx7 docs /prisma/prisma "How to define one-to-many relations with cascade delete"
```

### Writing good queries

The query directly affects the quality of results. Be specific and include relevant details. Do not include any sensitive or confidential information such as API keys, passwords, credentials, personal data, or proprietary code in your query.

| Quality | Example |
|---------|---------|
| Good | `"How to set up authentication with JWT in Express.js"` |
| Good | `"React useEffect cleanup function with async operations"` |
| Bad | `"auth"` |
| Bad | `"hooks"` |

Use the user's full question as the query when possible, vague one-word queries return generic results.

The output contains two types of content: **code snippets** (titled, with language-tagged blocks) and **info snippets** (prose explanations with breadcrumb context).

### Retry with `--research` if you weren't satisfied

If the default `ctx7 docs` answer didn't satisfy, re-run the same command **with `--research`** before giving up or answering from training data. This retries using sandboxed agents that git-pull the actual source repos plus a live web search, then synthesizes a fresh answer. More costly than the default — use it as a targeted retry.

```powershell
ctx7 docs /vercel/next.js "How does middleware matcher handle dynamic segments in v15?" --research
```

## Authentication

Works without authentication. For higher rate limits:

```powershell
# Option A: environment variable
$env:CONTEXT7_API_KEY = "your_key"

# Option B: OAuth login
ctx7 login
```

## Error Handling

If a command fails with a quota error ("Monthly quota reached" or "quota exceeded"):
1. Inform the user their Context7 quota is exhausted
2. Suggest they authenticate for higher limits: `ctx7 login`
3. If they cannot or choose not to authenticate, answer from training knowledge and clearly note it may be outdated

Do not silently fall back to training data — always tell the user why Context7 was not used.

If a command fails with DNS, host resolution, TLS, or generic fetch errors, retry once after confirming network availability. If it still fails, report the exact failure and do not pretend current docs were fetched.

## Common Mistakes

- Library IDs require a `/` prefix — `/facebook/react` not `facebook/react`
- Always run `ctx7 library` first — `ctx7 docs react "hooks"` will fail without a valid ID
- Use descriptive queries, not single words — `"React useEffect cleanup function"` not `"hooks"`
- Do not include sensitive information (API keys, passwords, credentials) in queries
