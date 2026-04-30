---
alwaysApply: true
description: Never treat a task as Small (S) if it touches core config, public APIs, auth/security, CI/CD/deployment, destructive operations, unvalidated bugs, or regression-prone changes. Must escalate to at least Medium (M). Applies to all tasks.
---

# Forced Escalation Guardrails

Never categorize a task as Small (S) if it involves any of the following:

- Modifying core configuration files (e.g., `package.json`, build configs), database schemas, or global state management.
- Changes that alter public APIs, shared components, or interfaces relied upon by other modules.
- "Simple" bug fixes where the root cause is not definitively proven by evidence (must route to `systematic-debugging` first).
- Changes with foreseeable side effects or regression risks that could break existing tests (must route to `test-driven-development`).
- Changes that affect authentication, authorization, or security-sensitive logic (e.g., JWT handling, API key processing, permission checks).
- Changes to CI/CD pipelines, deployment scripts, Dockerfiles, or infrastructure-as-code files.
- Changes involving destructive operations (data migration, batch deletion, file system manipulation, database schema changes).

See also: `skill-routing-and-execution-path.md` for T-Shirt Sizing and routing decision rules. For when to ask vs deduce, see `question-threshold.md`.
