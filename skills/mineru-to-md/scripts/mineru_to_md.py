#!/usr/bin/env python3
import argparse
import json
import posixpath
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
from typing import Any


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_BACKEND = "hybrid-auto-engine"
DEFAULT_PARSE_METHOD = "auto"
DEFAULT_LANG = "ch"
DEFAULT_TIMEOUT = 1800
DEFAULT_RETRY_TIMEOUT = 3600
DEFAULT_POLL_INTERVAL = 2.0
MAX_FILES = 2
SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".jp2",
    ".webp",
    ".gif",
    ".bmp",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
}
STATUS_RETRY_COUNT = 3
RESULT_RETRY_COUNT = 3
DEFAULT_CONTAINER_NAME = "mineru-api"
DEFAULT_CONTAINER_OUTPUT_ROOT = "/vllm-workspace/output"
TASK_ID_PATTERN = re.compile(r"^[0-9a-fA-F-]{8,}$")
IMAGE_REF_PATTERN = re.compile(r"(?P<prefix>[\(\"'=])(?:\./)?images/")


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def normalize_input_path(raw_path: str) -> Path:
    value = raw_path.strip().strip('"')
    if not value:
        raise ValueError("输入路径不能为空")

    lower_value = value.lower()
    if lower_value.startswith("/mnt/") and len(value) > 6 and value[5].isalpha() and value[6] == "/":
        drive = value[5].upper() + ":"
        tail = value[7:].replace("/", "\\")
        value = drive + ("\\" + tail if tail else "\\")
    elif value.startswith("/") and not value.startswith("//"):
        raise ValueError(
            f"不支持直接使用 Linux 路径: {raw_path}。"
            " 请改成 Windows 路径，或使用 \\\\wsl$\\发行版名\\... 路径。"
        )

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def normalize_output_dir(raw_path: str, create: bool = True) -> Path:
    path = normalize_input_path(raw_path)
    if path.exists() and not path.is_dir():
        raise ValueError(f"输出路径不是目录: {path}")
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def validate_task_id(task_id: str) -> None:
    if not TASK_ID_PATTERN.match(task_id):
        raise RuntimeError(f"收到可疑 task_id，已拒绝继续操作: {task_id}")


def rewrite_markdown_image_refs(markdown: str) -> str:
    return IMAGE_REF_PATTERN.sub(lambda match: f"{match.group('prefix')}image/", markdown)


def write_text_atomic(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.tmp")
    try:
        temp_path.write_text(content, encoding="utf-8", newline="\n")
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def prompt_output_dir() -> str:
    try:
        value = input("请输入 Markdown 输出目录: ").strip()
    except EOFError as exc:
        raise ValueError("缺少 --output-dir，且当前环境无法交互输入") from exc

    if not value:
        raise ValueError("输出目录不能为空")
    return value


def http_get_json(url: str, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"请求失败 {url}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"接口返回非 JSON 响应: {url}") from exc


def normalize_base_url(raw_url: str) -> str:
    value = raw_url.strip().rstrip("/")
    if not value:
        raise ValueError("base_url 不能为空")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"无效的 base_url: {raw_url}")
    return value


def ensure_service_available(base_url: str) -> None:
    health_url = f"{base_url}/health"
    try:
        payload = http_get_json(health_url, timeout=5)
    except (RuntimeError, TimeoutError) as exc:
        raise RuntimeError(
            "无法连接到 MinerU API。"
            f" 请先确认 WSL 中的 Docker 服务已启动，并且 Windows 可访问 {base_url}。"
            " 建议先在 WSL 中执行 `mineru api`。"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"健康检查返回异常内容: {payload!r}")


def run_curl_json(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError as exc:
        raise RuntimeError("未找到 curl.exe，请确认当前 Windows 系统可使用 curl.exe") from exc

    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"调用 MinerU API 失败: {stderr}")

    body = completed.stdout.strip()
    if not body:
        raise RuntimeError("MinerU API 返回了空响应")

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"MinerU API 返回了无法解析的 JSON: {body}") from exc


def submit_task(
    base_url: str,
    file_path: Path,
    backend: str,
    parse_method: str,
    lang: str,
) -> dict[str, Any]:
    command = [
        "curl.exe",
        "-sS",
        "-X",
        "POST",
        f"{base_url}/tasks",
        "-F",
        f"files=@{file_path}",
        "-F",
        f"backend={backend}",
        "-F",
        f"parse_method={parse_method}",
        "-F",
        f"lang_list={lang}",
        "-F",
        "return_md=true",
    ]
    return run_curl_json(command)


def wait_for_task(base_url: str, task_id: str, timeout_seconds: int, poll_interval: float) -> dict[str, Any]:
    status_url = f"{base_url}/tasks/{task_id}"
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        payload = None
        last_error: Exception | None = None
        for _ in range(STATUS_RETRY_COUNT):
            try:
                payload = http_get_json(status_url, timeout=30)
                last_error = None
                break
            except RuntimeError as exc:
                last_error = exc
                time.sleep(min(1.0, poll_interval))
        if payload is None:
            raise RuntimeError(f"获取任务状态失败: {task_id}: {last_error}")
        status = str(payload.get("status", "")).lower()
        if status in {"completed", "failed"}:
            return payload
        if status and status not in {"pending", "processing", "running", "queued"}:
            raise RuntimeError(f"收到未知任务状态 {status!r}: {task_id}")
        time.sleep(poll_interval)

    raise TimeoutError(f"任务超时: {task_id}")


def fetch_task_result(base_url: str, task_id: str) -> dict[str, Any]:
    result_url = f"{base_url}/tasks/{task_id}/result"
    last_error: Exception | None = None
    for _ in range(RESULT_RETRY_COUNT):
        try:
            return http_get_json(result_url, timeout=60)
        except RuntimeError as exc:
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"获取任务结果失败: {task_id}: {last_error}")


def cleanup_container_task(container_name: str, output_root: str, task_id: str) -> dict[str, str]:
    cleaned_root = output_root.rstrip("/")
    validate_task_id(task_id)
    if not cleaned_root.startswith("/"):
        raise RuntimeError(f"拒绝清理非绝对容器路径: {output_root}")

    target_dir = f"{cleaned_root}/{task_id}"
    # Cleanup runs inside the container shell, not on the Windows host.
    shell_command = f"test ! -e {shlex.quote(target_dir)} || rm -r -f -- {shlex.quote(target_dir)}"
    command = ["docker", "exec", container_name, "/bin/sh", "-lc", shell_command]

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError as exc:
        raise RuntimeError("未找到 docker 命令，无法清理容器内任务目录") from exc

    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(
            f"清理容器任务目录失败: container={container_name}, path={target_dir}, detail={stderr}"
        )

    return {
        "container": container_name,
        "path": target_dir,
        "task_id": task_id,
    }


def _run_docker_command(command: list[str], error_prefix: str) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError as exc:
        raise RuntimeError("未找到 docker 命令") from exc

    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"{error_prefix}: {stderr}")
    return completed


def locate_container_markdown(
    container_name: str,
    output_root: str,
    task_id: str,
    preferred_key: str,
) -> str:
    cleaned_root = output_root.rstrip("/")
    validate_task_id(task_id)
    task_root = f"{cleaned_root}/{task_id}"
    preferred_md_name = f"{preferred_key}.md"

    commands = [
        f"find {shlex.quote(task_root)} -type f -name {shlex.quote(preferred_md_name)} | head -n 1",
        f"find {shlex.quote(task_root)} -type f -name '*.md' | head -n 1",
    ]

    for shell_command in commands:
        completed = _run_docker_command(
            ["docker", "exec", container_name, "/bin/sh", "-lc", shell_command],
            "查找容器内 Markdown 失败",
        )
        candidate = completed.stdout.strip().splitlines()
        if candidate:
            return candidate[0].strip()

    raise RuntimeError(f"未找到容器任务目录中的 Markdown 文件: task_id={task_id}")


def export_task_artifacts(
    container_name: str,
    container_md_path: str,
    output_dir: Path,
    preferred_key: str,
    overwrite: bool,
) -> dict[str, str]:
    parse_dir = posixpath.dirname(container_md_path)

    with tempfile.TemporaryDirectory(prefix="mineru_export_") as temp_dir:
        staging_dir = Path(temp_dir)
        _run_docker_command(
            ["docker", "cp", f"{container_name}:{parse_dir}/.", str(staging_dir)],
            "从容器复制解析结果失败",
        )

        md_candidates = sorted(staging_dir.rglob("*.md"))
        if not md_candidates:
            raise RuntimeError(f"复制结果中没有找到 Markdown 文件: {parse_dir}")

        preferred_name = f"{preferred_key}.md"
        stage_md = next((path for path in md_candidates if path.name == preferred_name), md_candidates[0])
        markdown = stage_md.read_text(encoding="utf-8")

        output_stem = unique_output_stem(output_dir, preferred_key, overwrite)
        document_dir = output_dir / output_stem
        if document_dir.exists() and not document_dir.is_dir():
            raise RuntimeError(f"目标文档路径已存在但不是目录: {document_dir}")
        document_dir.mkdir(parents=True, exist_ok=True)

        output_file = document_dir / f"{output_stem}.md"
        images_src = staging_dir / "images"
        output_image_dir: Path | None = None

        if images_src.exists() and images_src.is_dir():
            output_image_dir = document_dir / "image"
            if output_image_dir.exists():
                shutil.rmtree(output_image_dir)
            shutil.copytree(images_src, output_image_dir)

            markdown = rewrite_markdown_image_refs(markdown)
        elif overwrite:
            stale_image_dir = document_dir / "image"
            if stale_image_dir.exists():
                shutil.rmtree(stale_image_dir)

        write_text_atomic(output_file, markdown)

        exported = {
            "output": str(output_file),
            "document_dir": str(document_dir),
            "container_parse_dir": parse_dir,
        }
        if output_image_dir is not None:
            exported["images_dir"] = str(output_image_dir)
        return exported


def find_markdown(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("md_content", "markdown", "md"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate
        for child in value.values():
            found = find_markdown(child)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_markdown(item)
            if found:
                return found
    return None


def extract_markdown(result_payload: dict[str, Any], preferred_key: str) -> str:
    results = result_payload.get("results")
    if isinstance(results, dict):
        preferred = results.get(preferred_key)
        if preferred is not None:
            found = find_markdown(preferred)
            if found:
                return found

        for item in results.values():
            found = find_markdown(item)
            if found:
                return found

    found = find_markdown(result_payload)
    if found:
        return found

    raise RuntimeError("任务已完成，但结果中没有找到 Markdown 内容")


def unique_output_stem(output_dir: Path, stem: str, overwrite: bool) -> str:
    candidate = output_dir / stem
    if overwrite or not candidate.exists():
        return stem

    index = 2
    while True:
        candidate_stem = f"{stem}_{index}"
        candidate = output_dir / candidate_stem
        if not candidate.exists():
            return candidate_stem
        index += 1


def existing_output_for(output_dir: Path, stem: str) -> Path | None:
    output_file = output_dir / stem / f"{stem}.md"
    return output_file if output_file.is_file() else None


def collect_input_files(args: argparse.Namespace) -> tuple[list[Path], list[dict[str, str]]]:
    source_count = sum(
        1
        for enabled in (
            bool(args.files),
            bool(args.input_dir),
            bool(args.list_file),
        )
        if enabled
    )
    if source_count != 1:
        raise ValueError("请只使用一种输入方式：直接文件路径、--input-dir 或 --list-file")

    if args.files:
        if len(args.files) > MAX_FILES:
            raise ValueError(
                f"直接传参模式单次最多处理 {MAX_FILES} 个文件。"
                " 批量转换请使用 --input-dir 或 --list-file，避免 shell 参数解析问题。"
            )
        return [normalize_input_path(item) for item in args.files], []

    if args.input_dir:
        input_dir = normalize_input_path(args.input_dir)
        if not input_dir.is_dir():
            raise ValueError(f"输入目录不存在或不是目录: {input_dir}")
        iterator = input_dir.rglob("*") if args.recursive else input_dir.iterdir()
        files: list[Path] = []
        skipped: list[dict[str, str]] = []
        for path in iterator:
            if not path.is_file():
                continue
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(path)
            else:
                skipped.append({"path": str(path), "reason": "unsupported_extension"})
        return sorted(
            files,
            key=lambda path: str(path).casefold(),
        ), sorted(
            skipped,
            key=lambda item: item["path"].casefold(),
        )

    list_file = normalize_input_path(args.list_file)
    if not list_file.is_file():
        raise ValueError(f"清单文件不存在或不可读取: {list_file}")
    input_files: list[Path] = []
    list_base_dir = list_file.parent
    for line_number, raw_line in enumerate(list_file.read_text(encoding="utf-8-sig").splitlines(), start=1):
        value = raw_line.strip()
        if not value or value.startswith("#"):
            continue
        try:
            cleaned_value = value.strip().strip('"')
            if is_relative_list_path(cleaned_value):
                input_files.append(normalize_input_path(str(list_base_dir / cleaned_value)))
            else:
                input_files.append(normalize_input_path(cleaned_value))
        except ValueError as exc:
            raise ValueError(f"清单文件第 {line_number} 行无效: {exc}") from exc
    return input_files, []


def is_relative_list_path(value: str) -> bool:
    cleaned = value.strip().strip('"')
    if not cleaned:
        return False
    if cleaned.startswith(("/", "\\")):
        return False
    if re.match(r"^[a-zA-Z]:[\\/]", cleaned):
        return False
    return True


def make_result(
    saved: list[dict[str, Any]],
    cleaned: list[dict[str, str]],
    errors: list[dict[str, str]],
    cleanup_errors: list[dict[str, str]],
    skipped: list[dict[str, str]],
    skipped_existing: list[dict[str, str]],
) -> dict[str, Any]:
    result: dict[str, Any] = {"saved": saved}
    if cleaned:
        result["cleaned"] = cleaned
    if errors:
        result["errors"] = errors
    if cleanup_errors:
        result["cleanup_errors"] = cleanup_errors
    if skipped:
        result["skipped"] = skipped
    if skipped_existing:
        result["skipped_existing"] = skipped_existing
    return result


def write_json_result(result_path: Path, result: dict[str, Any]) -> None:
    result_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_atomic(
        result_path,
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
    )


def emit_result(args: argparse.Namespace, result: dict[str, Any]) -> None:
    if args.result_file:
        try:
            result_path = normalize_input_path(args.result_file)
            result["result_file"] = str(result_path)
            write_json_result(result_path, result)
        except Exception as result_file_exc:  # noqa: BLE001
            result["result_file_error"] = str(result_file_exc)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def dry_run_result(
    input_files: list[Path],
    skipped: list[dict[str, str]],
    output_dir: Path | None,
    skip_existing: bool,
) -> dict[str, Any]:
    skipped_existing: list[dict[str, str]] = []
    planned_inputs: list[str] = []
    for path in input_files:
        existing_output = existing_output_for(output_dir, path.stem) if output_dir and skip_existing else None
        if existing_output:
            skipped_existing.append(
                {
                    "input": str(path),
                    "output": str(existing_output),
                    "reason": "output_exists",
                }
            )
        else:
            planned_inputs.append(str(path))

    return {
        "dry_run": True,
        "count": len(planned_inputs),
        "inputs": planned_inputs,
        **({"skipped": skipped} if skipped else {}),
        **({"skipped_existing": skipped_existing} if skipped_existing else {}),
    }


def validate_runtime_options(args: argparse.Namespace) -> None:
    if args.timeout <= 0:
        raise ValueError("--timeout 必须大于 0")
    if args.retry_timeout < 0:
        raise ValueError("--retry-timeout 不能小于 0")
    if args.poll_interval <= 0:
        raise ValueError("--poll-interval 必须大于 0")
    if args.recursive and not args.input_dir:
        raise ValueError("--recursive 只能与 --input-dir 一起使用")
    if args.skip_existing and args.overwrite:
        raise ValueError("--skip-existing 不能与 --overwrite 同时使用")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从 Windows 宿主机调用本地 MinerU API，把文件转换为 Markdown 并保存到指定目录。"
    )
    parser.add_argument("files", nargs="*", help="待转换文件路径；直接传参模式单次最多 2 个")
    parser.add_argument(
        "--input-dir",
        help="待转换文件目录；脚本会在目录内枚举受支持文件并串行转换，适合批量任务和特殊文件名",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="配合 --input-dir 使用，递归枚举子目录中的受支持文件",
    )
    parser.add_argument(
        "--list-file",
        help="UTF-8 文本清单文件；每行一个待转换文件路径，适合文件名含特殊引号或批量重试",
    )
    parser.add_argument(
        "--failure-list",
        help="如果存在转换失败文件，将失败输入路径写入这个 UTF-8 文本文件，便于后续用 --list-file 重试",
    )
    parser.add_argument(
        "--result-file",
        help="将最终 JSON 结果同时写入指定文件，适合长批量任务和后续自动检查",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只收集并校验输入文件，输出将处理的文件列表，不连接 MinerU API",
    )
    parser.add_argument("--output-dir", help="主题输出目录；每个输入文档会导出到独立子目录")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"MinerU API 地址，默认 {DEFAULT_BASE_URL}")
    parser.add_argument("--backend", default=DEFAULT_BACKEND, help=f"解析后端，默认 {DEFAULT_BACKEND}")
    parser.add_argument(
        "--parse-method",
        default=DEFAULT_PARSE_METHOD,
        help=f"解析方式，默认 {DEFAULT_PARSE_METHOD}",
    )
    parser.add_argument("--lang", default=DEFAULT_LANG, help=f"OCR 语言参数，默认 {DEFAULT_LANG}")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"单个任务超时时间（秒），默认 {DEFAULT_TIMEOUT}",
    )
    parser.add_argument(
        "--retry-timeout",
        type=int,
        default=DEFAULT_RETRY_TIMEOUT,
        help=(
            "单个任务首次超时后的重试超时时间（秒）；"
            f"默认 {DEFAULT_RETRY_TIMEOUT}，设置为 0 可禁用超时重试"
        ),
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=DEFAULT_POLL_INTERVAL,
        help=f"轮询间隔（秒），默认 {DEFAULT_POLL_INTERVAL}",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="允许复用并覆盖已存在的同名文档目录",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="如果目标文档 Markdown 已存在，则跳过该输入文件，适合断点续跑",
    )
    parser.add_argument(
        "--container-name",
        default=DEFAULT_CONTAINER_NAME,
        help=f"Docker 容器名称，默认 {DEFAULT_CONTAINER_NAME}",
    )
    parser.add_argument(
        "--container-output-root",
        default=DEFAULT_CONTAINER_OUTPUT_ROOT,
        help=f"容器内任务输出根目录，默认 {DEFAULT_CONTAINER_OUTPUT_ROOT}",
    )
    parser.add_argument(
        "--keep-container-artifacts",
        action="store_true",
        help="保留容器内任务目录，不在成功后自动清理",
    )
    return parser.parse_args()


def validate_input_files(input_files: list[Path]) -> None:
    if not input_files:
        raise ValueError("没有发现可转换的输入文件")

    missing_files = [str(path) for path in input_files if not path.is_file()]
    if missing_files:
        raise ValueError(
            "以下输入文件不存在或不可读取:\n" + "\n".join(f"  - {file_path}" for file_path in missing_files)
        )

    unsupported_files = [
        str(path) for path in input_files if path.suffix.lower() not in SUPPORTED_EXTENSIONS
    ]
    if unsupported_files:
        raise ValueError(
            "以下文件类型当前不受此 skill 支持:\n"
            + "\n".join(f"  - {file_path}" for file_path in unsupported_files)
        )


def convert_one_file(
    args: argparse.Namespace,
    base_url: str,
    output_dir: Path,
    file_path: Path,
    timeout_seconds: int,
) -> tuple[dict[str, Any], dict[str, str] | None, dict[str, str] | None]:
    display_path = str(file_path)
    preferred_key = file_path.stem

    submit_payload = submit_task(
        base_url=base_url,
        file_path=file_path,
        backend=args.backend,
        parse_method=args.parse_method,
        lang=args.lang,
    )

    task_id = str(submit_payload.get("task_id", "")).strip()
    if not task_id:
        raise RuntimeError(f"提交成功但未返回 task_id: {submit_payload}")
    validate_task_id(task_id)

    eprint(f"等待任务完成: {task_id} (timeout={timeout_seconds}s)")
    status_payload = wait_for_task(
        base_url=base_url,
        task_id=task_id,
        timeout_seconds=timeout_seconds,
        poll_interval=args.poll_interval,
    )

    if str(status_payload.get("status", "")).lower() == "failed":
        raise RuntimeError(str(status_payload.get("error") or "任务执行失败"))

    _ = fetch_task_result(base_url, task_id)
    container_md_path = locate_container_markdown(
        container_name=args.container_name,
        output_root=args.container_output_root,
        task_id=task_id,
        preferred_key=preferred_key,
    )
    exported = export_task_artifacts(
        container_name=args.container_name,
        container_md_path=container_md_path,
        output_dir=output_dir,
        preferred_key=preferred_key,
        overwrite=args.overwrite,
    )

    saved_item = {
        "input": display_path,
        "output": exported["output"],
        "document_dir": exported["document_dir"],
        "container_parse_dir": exported["container_parse_dir"],
        "task_id": task_id,
        **({"images_dir": exported["images_dir"]} if "images_dir" in exported else {}),
    }

    cleanup_info: dict[str, str] | None = None
    cleanup_error: dict[str, str] | None = None
    if not args.keep_container_artifacts:
        try:
            cleanup_info = cleanup_container_task(
                container_name=args.container_name,
                output_root=args.container_output_root,
                task_id=task_id,
            )
        except Exception as cleanup_exc:  # noqa: BLE001
            cleanup_error = {
                "input": display_path,
                "task_id": task_id,
                "error": str(cleanup_exc),
            }

    return saved_item, cleanup_info, cleanup_error


def main() -> int:
    args = parse_args()

    try:
        validate_runtime_options(args)
        base_url = normalize_base_url(args.base_url)
        input_files, skipped = collect_input_files(args)
        validate_input_files(input_files)
        output_dir_value = args.output_dir or (None if args.dry_run and not args.skip_existing else prompt_output_dir())
        output_dir = normalize_output_dir(output_dir_value, create=not args.dry_run) if output_dir_value else None
        if args.dry_run:
            emit_result(args, dry_run_result(input_files, skipped, output_dir, args.skip_existing))
            return 0
        if output_dir is None:
            raise ValueError("缺少 --output-dir，且当前环境无法交互输入")
    except ValueError as exc:
        eprint(f"错误: {exc}")
        return 2

    try:
        ensure_service_available(base_url)
    except RuntimeError as exc:
        eprint(f"错误: {exc}")
        return 3

    saved: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    cleaned: list[dict[str, str]] = []
    cleanup_errors: list[dict[str, str]] = []
    skipped_existing: list[dict[str, str]] = []

    total_files = len(input_files)

    for index, file_path in enumerate(input_files, start=1):
        display_path = str(file_path)
        try:
            if args.skip_existing:
                existing_output = existing_output_for(output_dir, file_path.stem)
                if existing_output:
                    skipped_existing.append(
                        {
                            "input": display_path,
                            "output": str(existing_output),
                            "reason": "output_exists",
                        }
                    )
                    eprint(f"[{index}/{total_files}] 已存在，跳过: {existing_output}")
                    continue

            eprint(f"[{index}/{total_files}] 提交任务: {display_path}")
            try:
                saved_item, cleanup_info, cleanup_error = convert_one_file(
                    args=args,
                    base_url=base_url,
                    output_dir=output_dir,
                    file_path=file_path,
                    timeout_seconds=args.timeout,
                )
            except TimeoutError as timeout_exc:
                if args.retry_timeout > args.timeout:
                    eprint(f"任务首次超时，准备重新提交并延长等待: {display_path}")
                    eprint(f"首次超时原因: {timeout_exc}")
                    saved_item, cleanup_info, cleanup_error = convert_one_file(
                        args=args,
                        base_url=base_url,
                        output_dir=output_dir,
                        file_path=file_path,
                        timeout_seconds=args.retry_timeout,
                    )
                    saved_item["retried_after_timeout"] = True
                else:
                    raise

            saved.append(saved_item)
            eprint(f"已保存: {saved_item['output']}")
            if "images_dir" in saved_item:
                eprint(f"已保存图片目录: {saved_item['images_dir']}")

            if cleanup_info is not None:
                cleaned.append(cleanup_info)
                eprint(f"已清理容器任务目录: {cleanup_info['path']}")
            if cleanup_error is not None:
                cleanup_errors.append(cleanup_error)
                eprint(f"警告: 容器任务目录清理失败: {cleanup_error['task_id']}")
                eprint(f"原因: {cleanup_error['error']}")
        except Exception as exc:  # noqa: BLE001
            errors.append({"input": display_path, "error": str(exc)})
            eprint(f"失败: {display_path}")
            eprint(f"原因: {exc}")

    result = make_result(
        saved=saved,
        cleaned=cleaned,
        errors=errors,
        cleanup_errors=cleanup_errors,
        skipped=skipped,
        skipped_existing=skipped_existing,
    )
    if errors and args.failure_list:
        try:
            failure_list_path = normalize_input_path(args.failure_list)
            failure_list_path.parent.mkdir(parents=True, exist_ok=True)
            write_text_atomic(
                failure_list_path,
                "\n".join(error["input"] for error in errors) + "\n",
            )
            result["failure_list"] = str(failure_list_path)
        except Exception as failure_list_exc:  # noqa: BLE001
            result["failure_list_error"] = str(failure_list_exc)

    emit_result(args, result)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
