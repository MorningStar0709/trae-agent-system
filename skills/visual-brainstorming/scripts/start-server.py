#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def build_screen_dir(project_dir: str | None) -> Path:
    session_id = f"{os.getpid()}-{int(time.time())}"
    if project_dir:
        return Path(project_dir) / ".superpowers" / "brainstorm" / session_id
    return Path(tempfile.gettempdir()) / "brainstorm" / session_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", dest="project_dir", default="")
    parser.add_argument("--host", dest="bind_host", default="127.0.0.1")
    parser.add_argument("--url-host", dest="url_host", default="")
    parser.add_argument("--foreground", action="store_true")
    args = parser.parse_args()

    url_host = args.url_host or ("localhost" if args.bind_host in {"127.0.0.1", "localhost"} else args.bind_host)
    script_dir = Path(__file__).resolve().parent
    server_script = script_dir / "server.cjs"
    screen_dir = build_screen_dir(args.project_dir or None)
    screen_dir.mkdir(parents=True, exist_ok=True)

    pid_file = screen_dir / ".server.pid"
    log_file = screen_dir / ".server.log"
    err_file = screen_dir / ".server.err.log"
    info_file = screen_dir / ".server-info"

    env = os.environ.copy()
    env["BRAINSTORM_DIR"] = str(screen_dir)
    env["BRAINSTORM_HOST"] = args.bind_host
    env["BRAINSTORM_URL_HOST"] = url_host
    env["BRAINSTORM_OWNER_PID"] = ""

    if args.foreground:
        proc = subprocess.run(["node", str(server_script)], cwd=str(script_dir), env=env)
        return proc.returncode

    creationflags = 0
    popen_kwargs: dict = {
        "cwd": str(script_dir),
        "env": env,
        "stdout": log_file.open("a", encoding="utf-8"),
        "stderr": err_file.open("a", encoding="utf-8"),
        "stdin": subprocess.DEVNULL,
        "start_new_session": True,
    }
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
        popen_kwargs["creationflags"] = creationflags

    try:
        proc = subprocess.Popen(["node", str(server_script)], **popen_kwargs)
    except FileNotFoundError:
        print(json.dumps({"error": "node executable not found"}))
        return 1

    pid_file.write_text(str(proc.pid), encoding="ascii")

    for _ in range(50):
        if info_file.exists():
            try:
                info = info_file.read_text(encoding="utf-8").strip()
            except OSError:
                info = ""
            if info:
                print(info)
                return 0
        if proc.poll() is not None:
            break
        time.sleep(0.1)

    if proc.poll() is None:
        proc.terminate()
        time.sleep(0.2)
        if proc.poll() is None:
            proc.kill()

    try:
        err_text = err_file.read_text(encoding="utf-8").strip()
    except OSError:
        err_text = ""
    if err_text:
        print(json.dumps({"error": "Server failed to start", "details": err_text[-500:]}))
    else:
        print(json.dumps({"error": "Server failed to start within 5 seconds"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
