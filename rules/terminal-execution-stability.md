---
alwaysApply: true
description: Core principles for terminal and CLI execution on Windows. Use for any task that depends on terminal output as evidence.
---

# Terminal Execution Stability

- Use this rule for any task that depends on terminal or CLI output as evidence (git state checks, test runs, build results, linter output, file scans, process status, logs, or generated reports).
- **Stable evidence over clever shell**: Prefer simpler command forms that reliably capture output. Prefer one command per conclusion. Prefer fewer terminal calls when a terminal is not the best evidence source.
- **Blocking for short checks, non-blocking only for servers**: Use blocking commands for short decision-critical checks so results can be inspected immediately. Use non-blocking only for web servers, watch processes, daemons.
- **File-backed for long output**: Write large diffs, test logs, stack traces to temporary files and inspect those instead of raw terminal output.
- **IDE tools over terminal parsing**: Prefer `Read`, `Grep`, `Glob`, `GetDiagnostics` when they answer the question more directly than a shell command.
- **Do not guess**: When terminal output is missing, truncated, or ambiguous, re-run with narrower scope first. If still unstable, follow the fallback chain: narrow scope → temp file → dedicated tools → report limitation.
- **Conclusion rules**: Treat output as evidence, not authority. Read exit codes, warnings, and results together. Do not claim success from one green-looking line. When logs are written to disk, prefer the saved artifact over a partially captured terminal stream.
