#!/usr/bin/env python3
import json
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def pid_alive(pid: int) -> bool:
    try:
        import os

        os.kill(pid, 0)
        return True
    except OSError:
        return False


def terminate_process(pid: int) -> bool:
    try:
        import os

        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            os.kill(pid, signal.SIGTERM)
    except OSError:
        return True

    if sys.platform == "win32":
        time.sleep(0.3)
        return not pid_alive(pid)

    for _ in range(20):
        if not pid_alive(pid):
            return True
        time.sleep(0.1)

    try:
        import os

        os.kill(pid, signal.SIGKILL)
    except OSError:
        return True

    time.sleep(0.2)
    return not pid_alive(pid)


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: stop-server.py <screen_dir>"}))
        return 1

    screen_dir = Path(sys.argv[1]).resolve()
    pid_file = screen_dir / ".server.pid"
    log_file = screen_dir / ".server.log"
    err_file = screen_dir / ".server.err.log"

    if not pid_file.exists():
        print(json.dumps({"status": "not_running"}))
        return 0

    try:
        pid = int(pid_file.read_text(encoding="ascii").strip())
    except (OSError, ValueError):
        print(json.dumps({"status": "failed", "error": "pid file is invalid"}))
        return 1

    if not terminate_process(pid):
        print(json.dumps({"status": "failed", "error": "process still running"}))
        return 1

    for path in (pid_file, log_file, err_file):
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    temp_root = Path(tempfile.gettempdir()).resolve()
    if temp_root in screen_dir.parents:
        shutil.rmtree(screen_dir, ignore_errors=True)

    print(json.dumps({"status": "stopped"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
