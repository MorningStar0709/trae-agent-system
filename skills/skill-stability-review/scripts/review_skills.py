#!/usr/bin/env python3
"""Lightweight Trae Skill stability scanner.

The script finds repeatable review leads for Windows/Trae, Chinese-user fit,
script synchronization, and packaging stability across agent-facing Skill
assets such as `SKILL.md`, templates, examples, references, and scripts.
It does not replace agent judgment: scan hits such as container-side POSIX
commands, anti-pattern examples, or mostly Chinese reference files still need
context review before becoming final findings.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".env",
    ".example",
    ".py",
    ".js",
    ".ts",
    ".mjs",
    ".cjs",
    ".ps1",
    ".bat",
    ".cmd",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".rb",
    ".php",
    ".pl",
    ".lua",
    ".r",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".cs",
    ".fsx",
    ".groovy",
    ".gradle",
    ".dockerfile",
    ".mk",
    ".make",
}

EXEC_SUFFIXES = {
    ".py",
    ".js",
    ".ts",
    ".mjs",
    ".cjs",
    ".ps1",
    ".bat",
    ".cmd",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".rb",
    ".php",
    ".pl",
    ".lua",
    ".r",
}
RELATED_DIRS = {"scripts", "references", "resources", "templates"}

DIMENSIONS = {
    "agent_executability": 0.25,
    "windows_trae": 0.20,
    "script_sync": 0.20,
    "trigger_boundary": 0.15,
    "chinese_fit": 0.10,
    "maintainability": 0.10,
}

SEVERITY_DEDUCTION = {
    "blocking": 2.5,
    "high": 1.5,
    "medium": 0.75,
    "low": 0.35,
}


@dataclass
class Finding:
    severity: str
    rule_id: str
    path: str
    line: int | None
    message: str
    dimension: str
    needs_context_review: bool = False


@dataclass
class SkillReview:
    name: str
    path: Path
    findings: list[Finding] = field(default_factory=list)
    validation: dict[str, object] = field(default_factory=dict)
    dimensions: dict[str, float] = field(default_factory=lambda: {key: 5.0 for key in DIMENSIONS})
    weighted_score: float = 5.0
    preliminary_rating: str = "A"


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            return None
    except OSError:
        return None


def iter_review_files(skill_dir: Path) -> Iterable[Path]:
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        if is_generated_path(path):
            continue
        if (
            path.suffix.lower() in TEXT_SUFFIXES
            or path.name.lower().endswith(".env.example")
            or path.name.lower() in {"dockerfile", "makefile", "justfile", "taskfile"}
            or is_under_related_dir(skill_dir, path)
        ):
            yield path


def is_under_related_dir(skill_dir: Path, path: Path) -> bool:
    try:
        relative_parts = path.relative_to(skill_dir).parts
    except ValueError:
        return False
    return any(part in RELATED_DIRS for part in relative_parts[:-1])


def is_under_dir(skill_dir: Path, path: Path, dirname: str) -> bool:
    try:
        relative_parts = path.relative_to(skill_dir).parts
    except ValueError:
        return False
    return dirname in relative_parts[:-1]


def should_scan_structural_keys(skill_dir: Path, path: Path) -> bool:
    if is_under_dir(skill_dir, path, "examples") or is_under_dir(skill_dir, path, "references"):
        return False
    lower_name = path.name.lower()
    if lower_name.endswith("-prompt.md") or lower_name.endswith("-reviewer.md"):
        return True
    if lower_name in {"code-reviewer.md"}:
        return True
    try:
        relative_parts = path.relative_to(skill_dir).parts
    except ValueError:
        return False
    return relative_parts[:2] == ("resources", "sample-agents")


def is_generated_path(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"}


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def index_at_line(text: str, line: int) -> int:
    if line <= 1:
        return 0
    index = 0
    for _ in range(line - 1):
        next_index = text.find("\n", index)
        if next_index == -1:
            return len(text)
        index = next_index + 1
    return index


def in_named_span(text: str, line: int, start_marker: str, end_markers: tuple[str, ...]) -> bool:
    line_index = index_at_line(text, line)
    start_index = text.rfind(start_marker, 0, line_index + 1)
    if start_index == -1:
        return False
    end_positions = [text.find(marker, start_index + len(start_marker)) for marker in end_markers]
    end_positions = [position for position in end_positions if position != -1]
    return not end_positions or line_index < min(end_positions)


def is_self_documentation_pattern(review: SkillReview, path: Path, text: str, line: int) -> bool:
    if review.name != "skill-stability-review" or path.name != "SKILL.md":
        return False
    spans = [
        ("High-risk host-side patterns in Windows Trae:", ("Container-side POSIX commands",)),
        ("Container-side POSIX commands may be acceptable", ("Path conversion rules:",)),
        ("Path conversion rules:", ("Stable pattern:",)),
        ("## Review Script", ("## Useful Windows Scan Commands",)),
        ("## Useful Windows Scan Commands", ("## Rating Scale",)),
        ("### Red Lines", ("When rating, separate:",)),
    ]
    return any(in_named_span(text, line, start, ends) for start, ends in spans)


def add_finding(
    review: SkillReview,
    severity: str,
    rule_id: str,
    path: Path,
    message: str,
    dimension: str,
    line: int | None = None,
    needs_context_review: bool = False,
) -> None:
    review.findings.append(
        Finding(
            severity=severity,
            rule_id=rule_id,
            path=str(path),
            line=line,
            message=message,
            dimension=dimension,
            needs_context_review=needs_context_review,
        )
    )


def severity_rank(severity: str) -> int:
    order = {"low": 0, "medium": 1, "high": 2, "blocking": 3}
    return order.get(severity, 0)


def has_finding(review: SkillReview, rule_id: str, path: Path) -> bool:
    path_text = str(path)
    return any(finding.rule_id == rule_id and finding.path == path_text for finding in review.findings)


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def frontmatter_description(skill_md: str) -> str:
    match = re.match(r"---\s*\n(.*?)\n---", skill_md, flags=re.S)
    if not match:
        return ""
    desc = re.search(r"^description:\s*(.+)$", match.group(1), flags=re.M)
    return desc.group(1).strip() if desc else ""


def quick_validate_covers_rule(rule_id: str) -> bool:
    return rule_id in {
        "missing_skill_md",
        "missing_frontmatter",
        "invalid_frontmatter_format",
        "invalid_frontmatter",
        "unexpected_frontmatter_keys",
        "missing_name",
        "missing_description",
        "invalid_name_format",
        "invalid_name_hyphen_usage",
        "name_too_long",
        "description_contains_angle_brackets",
        "description_too_long",
        "policy_missing_chinese_trigger",
        "policy_chinese_heading",
    }


def scan_skill_md(review: SkillReview, skill_md_path: Path, text: str) -> None:
    desc = frontmatter_description(text)
    if not desc:
        add_finding(
            review,
            "high",
            "missing_description",
            skill_md_path,
            "SKILL.md frontmatter is missing a concrete description.",
            "trigger_boundary",
        )
    else:
        if not re.search(r"\bUse\b.{0,80}\b(when|whenever|for|to)\b", desc, flags=re.I):
            add_finding(
                review,
                "medium",
                "weak_trigger_description",
                skill_md_path,
                "description does not contain an explicit use trigger.",
                "trigger_boundary",
            )
    if not re.search(r"Do Not Use|Do not use|do not use", text):
        add_finding(
            review,
            "medium",
            "missing_negative_boundary",
            skill_md_path,
            "Skill lacks an explicit negative boundary such as Do Not Use.",
            "trigger_boundary",
        )

    execution_oriented = bool(re.search(r"\b(script|MCP|CLI|command|tool|workflow|execute|run)\b", text, re.I))
    if execution_oriented and not re.search(r"Failure Handling|Troubleshooting|fallback|失败|故障", text, re.I):
        add_finding(
            review,
            "low",
            "missing_failure_handling",
            skill_md_path,
            "Execution-oriented Skill lacks a clear Failure Handling or Troubleshooting section.",
            "agent_executability",
        )


def remove_markdown_fences(text: str) -> str:
    """Replace all ```...``` blocks with blank lines to preserve line numbers."""
    return re.sub(r"```[\s\S]*?```", lambda m: "\n" * m.group(0).count("\n"), text)


def scan_text_patterns(review: SkillReview, path: Path, text: str) -> None:
    if review.name == "skill-stability-review" and path.name == "review_skills.py":
        return
    reference_asset = has_review_override(text, "reference-asset")

    patterns = [
        ("unix_bash_fence", "medium", r"```bash", "Markdown uses a bash fence; confirm this is not host-side Windows guidance."),
        ("unix_export", "high", r"\bexport\s+\w+=", "Host-side export syntax is Unix shell specific."),
        ("unix_heredoc", "high", r"cat\s+<<", "Heredoc examples are Unix shell specific."),
        ("unix_sudo", "high", r"\bsudo\b", "sudo is not a Windows PowerShell command."),
        ("unix_chmod", "high", r"\bchmod\b", "chmod is usually not valid host-side Windows guidance."),
        ("unix_rm_rf", "high", r"rm\s+-rf", "rm -rf is risky or invalid on Windows host; confirm whether it is container-side."),
        ("unix_home_tmp", "medium", r"(?<![\w:])(~\/|\/tmp\/)", "Unix-style host path appears; confirm whether it should be Windows or container-only."),
        ("ask_user_question", "medium", r"AskUserQuestion", "Legacy AskUserQuestion-style workflow may not fit current Trae execution."),
        ("chinese_structural_key", "medium", r"^\s*\*\*(.*?)[\uff1a:]\*\*", "Markdown contains a structural key that may be Chinese; structural keys should be English."),
    ]
    for rule_id, severity, pattern, message in patterns:
        scan_target = remove_markdown_fences(text) if rule_id == "chinese_structural_key" else text
        for match in re.finditer(pattern, scan_target, flags=re.M):
            if rule_id == "chinese_structural_key":
                if not should_scan_structural_keys(review.path, path):
                    continue
                if not has_cjk(match.group(1)):
                    continue
            if reference_asset and rule_id.startswith("unix_"):
                continue
            line = line_number(text, match.start())
            if is_self_documentation_pattern(review, path, text, line):
                continue
            add_finding(
                review,
                severity,
                rule_id,
                path,
                message,
                "windows_trae",
                line,
                needs_context_review=True,
            )

    if path.suffix.lower() == ".json":
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            add_finding(
                review,
                "high",
                "invalid_json_config",
                path,
                f"JSON config is invalid: {exc.msg}.",
                "script_sync",
                exc.lineno,
            )


def is_script_like(skill_dir: Path, path: Path, text: str) -> bool:
    suffix = path.suffix.lower()
    if suffix in EXEC_SUFFIXES:
        return True
    if path.name.lower() in {"dockerfile", "makefile", "justfile", "taskfile"}:
        return True
    first_line = text.splitlines()[0] if text.splitlines() else ""
    if first_line.startswith("#!"):
        return True
    if is_under_dir(skill_dir, path, "scripts"):
        return bool(
            re.search(
                r"\b(python|node|npm|npx|pnpm|yarn|uv|uvx|pip|docker|git|pwsh|powershell|cmd\.exe|bash|sh)\b",
                text,
                flags=re.I,
            )
        )
    return False


def has_failure_path(text: str) -> bool:
    return bool(
        re.search(
            r"sys\.exit|raise\s+SystemExit|process\.exit|process\.exitCode|exit\s+/b|exit\s+1|throw\s+|raise\s+|set\s+-e|\$LASTEXITCODE|try\s*:|catch\s*\(|except\s+|trap\s+",
            text,
            flags=re.I,
        )
    )


def has_structured_output(text: str) -> bool:
    return bool(re.search(r"json\.dumps|JSON\.stringify|ConvertTo-Json|Write-Output|print\s*\(", text))


def has_review_override(text: str, marker: str) -> bool:
    return bool(re.search(rf"review:\s*{re.escape(marker)}\b", text, flags=re.I))


def scan_scripts(review: SkillReview, skill_dir: Path, max_file_bytes: int) -> None:
    script_files: list[Path] = []
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        if is_generated_path(path):
            continue
        if path.suffix.lower() in EXEC_SUFFIXES or path.name.lower() in {"dockerfile", "makefile", "justfile", "taskfile"}:
            script_files.append(path)
        elif is_under_dir(skill_dir, path, "scripts"):
            script_files.append(path)
    if not script_files:
        return

    for path in script_files:
        try:
            file_size = path.stat().st_size
        except OSError:
            add_finding(
                review,
                "low",
                "script_stat_failed",
                path,
                "Could not stat script file.",
                "maintainability",
            )
            continue
        if file_size > max_file_bytes:
            if not has_finding(review, "file_skipped_too_large", path):
                add_finding(
                    review,
                    "low",
                    "script_skipped_too_large",
                    path,
                    f"Script is larger than max_file_bytes ({file_size} > {max_file_bytes}) and was skipped.",
                    "maintainability",
                )
            continue
        text = read_text(path)
        if text is None:
            add_finding(
                review,
                "low",
                "script_not_text_readable",
                path,
                "Script matched executable suffixes but could not be decoded as UTF-8 text.",
                "maintainability",
            )
            continue
        if not is_script_like(skill_dir, path, text):
            continue
        skip_failure_path = has_review_override(text, "reference-asset") or has_review_override(
            text, "skip-failure-path"
        )
        skip_structured_output = has_review_override(
            text, "reference-asset"
        ) or has_review_override(text, "allow-human-readable-output")
        if not skip_failure_path and not has_failure_path(text):
            add_finding(
                review,
                "medium",
                "script_missing_failure_path",
                path,
                "Script-like file does not show an explicit failure path or exception handling.",
                "script_sync",
                needs_context_review=True,
            )
        if not skip_structured_output and not has_structured_output(text):
            add_finding(
                review,
                "low",
                "script_no_structured_output",
                path,
                "Script-like file does not show structured or clearly intentional output; confirm prose output is intentional.",
                "script_sync",
                needs_context_review=True,
            )


def scan_generated_noise(review: SkillReview, skill_dir: Path) -> None:
    for path in skill_dir.rglob("*"):
        if path.is_dir() and path.name == "__pycache__":
            add_finding(
                review,
                "low",
                "generated_pycache",
                path,
                "__pycache__ directory is generated packaging noise.",
                "maintainability",
            )
        elif path.is_file() and path.suffix == ".pyc":
            add_finding(
                review,
                "low",
                "generated_pyc",
                path,
                ".pyc file is generated packaging noise.",
                "maintainability",
            )


def run_quick_validate(review: SkillReview, quick_validate: Path | None, timeout_seconds: float) -> None:
    if quick_validate is None or not quick_validate.exists():
        review.validation = {"quick_validate": "not_found"}
        return
    try:
        completed = subprocess.run(
            [sys.executable, str(quick_validate), "--json", str(review.path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        review.validation = {
            "quick_validate": "timeout",
            "timeout_seconds": timeout_seconds,
        }
        add_finding(
            review,
            "high",
            "quick_validate_timeout",
            review.path,
            "Skill quick_validate timed out.",
            "agent_executability",
        )
        return
    parsed: dict[str, Any] | None = None
    output_text = completed.stdout.strip()
    try:
        parsed = json.loads(output_text) if output_text else None
    except json.JSONDecodeError:
        parsed = None

    review.validation = {
        "quick_validate": "pass" if completed.returncode == 0 else "fail",
        "returncode": completed.returncode,
        "output": output_text,
        "parsed": parsed,
    }

    if parsed and isinstance(parsed.get("issues"), list):
        for issue in parsed["issues"]:
            if not isinstance(issue, dict):
                continue
            add_finding(
                review,
                str(issue.get("severity", "medium")),
                str(issue.get("rule_id", "quick_validate_issue")),
                review.path / "SKILL.md",
                str(issue.get("message", "quick_validate reported an issue.")),
                str(issue.get("dimension", "agent_executability")),
                issue.get("line") if isinstance(issue.get("line"), int) else None,
                needs_context_review=False,
            )

    if completed.returncode != 0 and not (parsed and isinstance(parsed.get("issues"), list) and parsed["issues"]):
        add_finding(
            review,
            "blocking",
            "quick_validate_failed",
            review.path,
            "Skill failed quick_validate.",
            "agent_executability",
        )


def compute_scores(review: SkillReview) -> None:
    deduped_findings: dict[tuple[str, str, int | None], Finding] = {}
    for finding in review.findings:
        key = (finding.rule_id, finding.path, finding.line)
        existing = deduped_findings.get(key)
        if existing is None or severity_rank(finding.severity) > severity_rank(existing.severity):
            deduped_findings[key] = finding
    review.findings = list(deduped_findings.values())

    for finding in review.findings:
        if finding.needs_context_review:
            continue
        deduction = SEVERITY_DEDUCTION[finding.severity]
        review.dimensions[finding.dimension] = max(0.0, review.dimensions[finding.dimension] - deduction)

    review.weighted_score = round(
        sum(review.dimensions[key] * weight for key, weight in DIMENSIONS.items()),
        2,
    )
    rating = rating_from_score(review.weighted_score)
    severities = {finding.severity for finding in review.findings if not finding.needs_context_review}
    if "blocking" in severities:
        rating = max_downgrade(rating, "C")
    elif "high" in severities:
        rating = max_downgrade(rating, "B")
    review.preliminary_rating = rating


def rating_from_score(score: float) -> str:
    if score >= 4.5:
        return "A"
    if score >= 4.0:
        return "A-"
    if score >= 3.25:
        return "B"
    if score >= 2.25:
        return "C"
    return "D"


def max_downgrade(current: str, ceiling: str) -> str:
    order = ["A", "A-", "B", "C", "D"]
    return order[max(order.index(current), order.index(ceiling))]


def review_skill(
    skill_dir: Path,
    quick_validate: Path | None,
    include_generated: bool,
    quick_validate_timeout: float,
    max_file_bytes: int,
) -> SkillReview:
    review = SkillReview(name=skill_dir.name, path=skill_dir)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        add_finding(review, "blocking", "missing_skill_md", skill_dir, "Skill directory lacks SKILL.md.", "agent_executability")
    else:
        try:
            skill_md_size = skill_md.stat().st_size
        except OSError:
            add_finding(
                review,
                "blocking",
                "skill_md_stat_failed",
                skill_md,
                "Could not stat SKILL.md.",
                "agent_executability",
            )
            skill_md_size = None
        if skill_md_size is None:
            pass
        elif skill_md_size > max_file_bytes:
            add_finding(
                review,
                "high",
                "skill_md_too_large",
                skill_md,
                f"SKILL.md is larger than max_file_bytes ({skill_md_size} > {max_file_bytes}) and was not fully scanned.",
                "agent_executability",
            )
        else:
            text = read_text(skill_md)
            if text is None:
                add_finding(review, "blocking", "unreadable_skill_md", skill_md, "SKILL.md is not UTF-8 readable.", "agent_executability")
            else:
                scan_skill_md(review, skill_md, text)

    for path in iter_review_files(skill_dir):
        try:
            file_size = path.stat().st_size
        except OSError:
            add_finding(
                review,
                "low",
                "file_stat_failed",
                path,
                "Could not stat review file.",
                "maintainability",
            )
            continue
        if file_size > max_file_bytes:
            if path == skill_md:
                continue
            add_finding(
                review,
                "low",
                "file_skipped_too_large",
                path,
                f"File is larger than max_file_bytes ({file_size} > {max_file_bytes}) and was skipped.",
                "maintainability",
            )
            continue
        text = read_text(path)
        if text is None:
            add_finding(
                review,
                "low",
                "file_not_text_readable",
                path,
                "File matched review suffixes but could not be decoded as UTF-8 text.",
                "maintainability",
            )
            continue
        scan_text_patterns(review, path, text)

    scan_scripts(review, skill_dir, max_file_bytes)
    if include_generated:
        scan_generated_noise(review, skill_dir)
    run_quick_validate(review, quick_validate, quick_validate_timeout)
    compute_scores(review)
    return review


def discover_skills(root: Path, single_skill: Path | None) -> list[Path]:
    if single_skill:
        return [single_skill.resolve()]
    if (root / "SKILL.md").exists():
        return [root.resolve()]
    return sorted([p.resolve() for p in root.iterdir() if p.is_dir() and (p / "SKILL.md").exists()])


def find_quick_validate(root: Path) -> Path | None:
    candidates = [
        root / "skill-creator" / "scripts" / "quick_validate.py",
        Path(__file__).resolve().parents[2] / "skill-creator" / "scripts" / "quick_validate.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def to_jsonable(review: SkillReview) -> dict[str, object]:
    return {
        "name": review.name,
        "path": str(review.path),
        "preliminary_rating": review.preliminary_rating,
        "weighted_score": review.weighted_score,
        "dimensions": review.dimensions,
        "validation": review.validation,
        "findings": [
            {
                "severity": finding.severity,
                "rule_id": finding.rule_id,
                "path": finding.path,
                "line": finding.line,
                "message": finding.message,
                "dimension": finding.dimension,
                "needs_context_review": finding.needs_context_review,
            }
            for finding in review.findings
        ],
    }


def render_markdown(reviews: list[SkillReview]) -> str:
    lines = [
        "**自动扫描摘要**",
        "",
        "脚本输出的是初步评分和审查线索；`needs_context_review` 的命中需要 agent 结合上下文确认。",
        "",
        "| Skill | Score | Preliminary | Findings | Validation |",
        "|---|---:|---|---:|---|",
    ]
    for review in reviews:
        validation = review.validation.get("quick_validate", "not_run")
        lines.append(
            f"| {review.name} | {review.weighted_score:.2f} | {review.preliminary_rating} | {len(review.findings)} | {validation} |"
        )

    grouped: dict[str, list[tuple[SkillReview, Finding]]] = {key: [] for key in ["blocking", "high", "medium", "low"]}
    for review in reviews:
        for finding in review.findings:
            if finding.rule_id == "quick_validate_failed" and review.validation.get("parsed"):
                continue
            grouped[finding.severity].append((review, finding))

    for severity in ["blocking", "high", "medium", "low"]:
        items = grouped[severity]
        if not items:
            continue
        lines.extend(["", f"**{severity.title()} Findings**"])
        for review, finding in items:
            line = f":{finding.line}" if finding.line else ""
            context = " needs_context_review" if finding.needs_context_review else ""
            lines.append(
                f"- `{review.name}` `{finding.rule_id}` `{finding.path}{line}`{context}: {finding.message}"
            )
    return "\n".join(lines)


def emit_cli_error(message: str, markdown: bool) -> None:
    if markdown:
        print("**扫描失败**")
        print("")
        print(f"- {message}")
    else:
        print(
            json.dumps(
                {
                    "scanner": "skill-stability-review/scripts/review_skills.py",
                    "schema_version": 1,
                    "error": message,
                },
                ensure_ascii=False,
                indent=2,
            )
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan Trae Skills for stability review leads.")
    parser.add_argument("--root", default=".", help="Root skills directory or a single Skill directory.")
    parser.add_argument("--skill", help="Single Skill directory to review.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default unless --markdown is used.")
    parser.add_argument("--markdown", action="store_true", help="Emit a Markdown summary.")
    parser.add_argument("--include-generated", action="store_true", help="Report generated files such as __pycache__ and .pyc.")
    parser.add_argument("--no-quick-validate", action="store_true", help="Skip skill-creator quick_validate.")
    parser.add_argument(
        "--quick-validate-timeout",
        type=float,
        default=30.0,
        help="Seconds to wait for each quick_validate run before reporting a timeout.",
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=2_000_000,
        help="Maximum size for a text file scan. Larger files are reported and skipped.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    single_skill = Path(args.skill).resolve() if args.skill else None
    if single_skill is not None and (not single_skill.exists() or not single_skill.is_dir()):
        emit_cli_error(f"--skill must point to an existing Skill directory: {single_skill}", args.markdown)
        return 2
    if single_skill is None and (not root.exists() or not root.is_dir()):
        emit_cli_error(f"--root must point to an existing directory: {root}", args.markdown)
        return 2
    quick_validate = None if args.no_quick_validate else find_quick_validate(root)
    skills = discover_skills(root, single_skill)

    reviews = [
        review_skill(
            skill,
            quick_validate,
            args.include_generated,
            args.quick_validate_timeout,
            args.max_file_bytes,
        )
        for skill in skills
    ]
    payload = {
        "scanner": "skill-stability-review/scripts/review_skills.py",
        "schema_version": 1,
        "root": str(root),
        "review_count": len(reviews),
        "note": "Automated scan provides review leads and preliminary ratings; agent context review is required.",
        "reviews": [to_jsonable(review) for review in reviews],
    }

    if args.markdown:
        print(render_markdown(reviews))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
