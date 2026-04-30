#!/usr/bin/env python3
"""Quick validation script for Trae Skills.

This validator keeps the original lightweight frontmatter checks and now also
executes the repository language policy defined in `skill-language-policy`.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ALLOWED_PROPERTIES = {"name", "description"}
DEFAULT_POLICY_RULES = {
    "require_chinese_in_description": True,
    "forbid_cjk_in_skill_headings": True,
}


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def make_issue(rule_id: str, message: str, *, line: int | None = None, severity: str = "high", dimension: str = "agent_executability") -> dict[str, object]:
    return {
        "rule_id": rule_id,
        "message": message,
        "line": line,
        "severity": severity,
        "dimension": dimension,
    }


def parse_simple_frontmatter(frontmatter_text: str) -> tuple[dict[str, str], dict[str, int]]:
    """Parse Trae Skill frontmatter and keep source line numbers."""
    frontmatter: dict[str, str] = {}
    line_numbers: dict[str, int] = {}
    for line_number, raw_line in enumerate(frontmatter_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-") or ":" not in line:
            raise ValueError(f"line {line_number}: expected 'key: value'")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"line {line_number}: empty key")
        if key in frontmatter:
            raise ValueError(f"line {line_number}: duplicate key '{key}'")
        if value.startswith(("|", ">")):
            raise ValueError(f"line {line_number}: multiline values are not supported")
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        frontmatter[key] = value
        line_numbers[key] = line_number + 1  # account for opening ---
    return frontmatter, line_numbers


def find_policy_path() -> Path | None:
    candidate = Path(__file__).resolve().parents[2] / "skill-language-policy" / "SKILL.md"
    return candidate if candidate.exists() else None


def load_policy_rules() -> tuple[dict[str, bool], list[dict[str, object]], str | None]:
    issues: list[dict[str, object]] = []
    policy_path = find_policy_path()
    if policy_path is None:
        issues.append(
            make_issue(
                "missing_policy_file",
                "Repository language policy file was not found.",
                severity="medium",
                dimension="maintainability",
            )
        )
        return DEFAULT_POLICY_RULES.copy(), issues, None

    try:
        policy_text = policy_path.read_text(encoding="utf-8")
    except OSError as exc:
        issues.append(
            make_issue(
                "policy_read_failed",
                f"Could not read language policy file: {exc}",
                severity="medium",
                dimension="maintainability",
            )
        )
        return DEFAULT_POLICY_RULES.copy(), issues, str(policy_path)

    rules = DEFAULT_POLICY_RULES.copy()
    english_required_match = re.search(r"## English-Required Layers(.*?)(?:\n## |\Z)", policy_text, flags=re.S)
    chinese_retained_match = re.search(r"## Chinese-Retained Layers(.*?)(?:\n## |\Z)", policy_text, flags=re.S)

    if english_required_match is None:
        issues.append(
            make_issue(
                "policy_missing_english_required_section",
                "Language policy is missing the English-Required Layers section.",
                severity="medium",
                dimension="maintainability",
            )
        )
    if chinese_retained_match is None:
        issues.append(
            make_issue(
                "policy_missing_chinese_retained_section",
                "Language policy is missing the Chinese-Retained Layers section.",
                severity="medium",
                dimension="maintainability",
            )
        )

    if english_required_match is not None:
        rules["forbid_cjk_in_skill_headings"] = "Section headings in `SKILL.md`" in english_required_match.group(1)
    if chinese_retained_match is not None:
        retained_text = chinese_retained_match.group(1)
        rules["require_chinese_in_description"] = (
            "Trigger phrases and natural use cases inside the `description` frontmatter" in retained_text
        )

    return rules, issues, str(policy_path)


def remove_markdown_fences(text: str) -> str:
    """Replace all ```...``` blocks with blank lines to preserve line numbers."""
    return re.sub(r"```[\s\S]*?```", lambda m: "\n" * m.group(0).count("\n"), text)

def iter_heading_matches(body_text: str) -> list[tuple[int, str]]:
    cleaned_text = remove_markdown_fences(body_text)
    return [(match.start(), match.group(1)) for match in re.finditer(r"^#+\s+(.*)$", cleaned_text, flags=re.M)]


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def validate_skill(skill_path: str | Path) -> dict[str, object]:
    """Validate a skill and return structured diagnostics."""
    skill_path = Path(skill_path).resolve()
    skill_md = skill_path / "SKILL.md"
    issues: list[dict[str, object]] = []
    policy_rules, policy_issues, policy_path = load_policy_rules()
    issues.extend(policy_issues)

    if not skill_md.exists():
        issues.append(make_issue("missing_skill_md", "SKILL.md not found", severity="blocking"))
        return {
            "valid": False,
            "message": "SKILL.md not found",
            "issues": issues,
            "policy_path": policy_path,
            "skill_path": str(skill_path),
        }

    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        issues.append(make_issue("skill_md_read_failed", f"Could not read SKILL.md: {exc}", severity="blocking"))
        return {
            "valid": False,
            "message": f"Could not read SKILL.md: {exc}",
            "issues": issues,
            "policy_path": policy_path,
            "skill_path": str(skill_path),
        }

    if not content.startswith("---"):
        issues.append(make_issue("missing_frontmatter", "No YAML frontmatter found", severity="blocking"))
        return {
            "valid": False,
            "message": "No YAML frontmatter found",
            "issues": issues,
            "policy_path": policy_path,
            "skill_path": str(skill_path),
        }

    match = re.match(r"^---\n(.*?)\n---\n?", content, re.DOTALL)
    if not match:
        issues.append(make_issue("invalid_frontmatter_format", "Invalid frontmatter format", severity="blocking"))
        return {
            "valid": False,
            "message": "Invalid frontmatter format",
            "issues": issues,
            "policy_path": policy_path,
            "skill_path": str(skill_path),
        }

    frontmatter_text = match.group(1)
    body_text = content[match.end():]

    try:
        frontmatter, frontmatter_lines = parse_simple_frontmatter(frontmatter_text)
    except ValueError as exc:
        issues.append(make_issue("invalid_frontmatter", f"Invalid frontmatter: {exc}", severity="blocking"))
        return {
            "valid": False,
            "message": f"Invalid frontmatter: {exc}",
            "issues": issues,
            "policy_path": policy_path,
            "skill_path": str(skill_path),
        }

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        issues.append(
            make_issue(
                "unexpected_frontmatter_keys",
                (
                    f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
                    f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
                ),
                severity="blocking",
            )
        )

    for required in ("name", "description"):
        if required not in frontmatter:
            issues.append(
                make_issue(
                    f"missing_{required}",
                    f"Missing '{required}' in frontmatter",
                    line=frontmatter_lines.get(required),
                    severity="blocking",
                )
            )

    name = frontmatter.get("name", "").strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            issues.append(
                make_issue(
                    "invalid_name_format",
                    f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)",
                    line=frontmatter_lines.get("name"),
                    severity="blocking",
                )
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            issues.append(
                make_issue(
                    "invalid_name_hyphen_usage",
                    f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
                    line=frontmatter_lines.get("name"),
                    severity="blocking",
                )
            )
        if len(name) > 64:
            issues.append(
                make_issue(
                    "name_too_long",
                    f"Name is too long ({len(name)} characters). Maximum is 64 characters.",
                    line=frontmatter_lines.get("name"),
                    severity="blocking",
                )
            )

    description = frontmatter.get("description", "").strip()
    if description:
        if "<" in description or ">" in description:
            issues.append(
                make_issue(
                    "description_contains_angle_brackets",
                    "Description cannot contain angle brackets (< or >)",
                    line=frontmatter_lines.get("description"),
                    severity="blocking",
                )
            )
        if len(description) > 1024:
            issues.append(
                make_issue(
                    "description_too_long",
                    f"Description is too long ({len(description)} characters). Maximum is 1024 characters.",
                    line=frontmatter_lines.get("description"),
                    severity="blocking",
                )
            )
        if policy_rules["require_chinese_in_description"] and not contains_cjk(description):
            issues.append(
                make_issue(
                    "policy_missing_chinese_trigger",
                    "description has no Chinese trigger phrase for Chinese-speaking users.",
                    line=frontmatter_lines.get("description"),
                    severity="low",
                    dimension="chinese_fit",
                )
            )

    if policy_rules["forbid_cjk_in_skill_headings"]:
        for heading_index, heading_text in iter_heading_matches(body_text):
            if contains_cjk(heading_text):
                issues.append(
                    make_issue(
                        "policy_chinese_heading",
                        f"SKILL.md header contains Chinese and should use English structure keys: '{heading_text}'.",
                        line=line_number(content, match.end() + heading_index),
                        severity="medium",
                        dimension="script_sync",
                    )
                )

    valid = not issues
    message = "Skill is valid!" if valid else issues[0]["message"]
    return {
        "valid": valid,
        "message": message,
        "issues": issues,
        "policy_path": policy_path,
        "skill_path": str(skill_path),
        "policy_rules": policy_rules,
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    as_json = False
    if "--json" in args:
        as_json = True
        args.remove("--json")

    if len(args) != 1:
        usage = "Usage: python scripts/quick_validate.py [--json] <skill_directory>"
        if as_json:
            print(json.dumps({"valid": False, "message": usage, "issues": []}, ensure_ascii=False, indent=2))
        else:
            print(usage)
        sys.exit(1)

    result = validate_skill(args[0])
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["message"])
    sys.exit(0 if result["valid"] else 1)
