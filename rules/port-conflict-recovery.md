---
alwaysApply: false
description: Use when a command fails with EADDRINUSE, port conflict, or zombie process on Windows. Provides step-by-step recovery for zombie process handling, server startup hygiene, and post-recovery logging.
---

# Port Conflict Recovery

## Zombie Process Handling

When a command fails with `EADDRINUSE`, `port already in use`, or `Address already in use`:

1. **Identify the blocking process** — Run on Windows:
   ```
   netstat -ano | Select-String "<PORT_NUMBER>"
   ```
   Extract the PID from the last column.

2. **Kill the zombie process**:
   ```
   taskkill /PID <PID> /F
   ```
   Confirm termination.

3. **Verify the port is free** — Re-run step 1 and confirm the port is gone.

4. **Retry the original command**.

If `taskkill` fails (permission denied, system process):
- Report the PID and process name to the user.
- Suggest manually closing the application.
- Do not use the port while it remains occupied.

## Server Process Hygiene

Before starting a long-running process (dev server, watcher, daemon):
1. Check if the target port is already occupied.
2. If occupied, follow Zombie Process Handling above.
3. Only start after confirming the port is free.

Do not start multiple instances on the same port. Kill the previous instance first.

## Post-Recovery Logging

After successfully recovering from a port conflict, if the resolution required investigation, invoke `self-improvement` to log the experience. If the same failure recurs 2+ times, promote the pattern to a permanent Rule.
