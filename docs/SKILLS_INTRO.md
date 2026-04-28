# Trae Skills Project Introduction

## Project Overview

This project is a suite of Skills toolsets designed specifically for **Trae IDE on Windows**, focusing on helping users efficiently create, manage, and optimize Trae's Agents and Rules. All Skills have undergone rigorous Windows/Trae adaptation verification to ensure stable operation in Windows environments.

## Directory Structure

```
Trae-skills/
├── docs/                              # Project documentation
│   ├── SKILLS_INTRO.md              # English version
│   └── SKILLS_INTRO_zh.md          # Chinese version
├── skills/                            # Skills core directory
│   ├── agent-blueprint-architect/    # Agent blueprint design tool
│   │   └── SKILL.md
│   ├── creating-trae-rules/          # Trae rules creation tool
│   │   ├── resources/
│   │   │   └── trae-rules-reference.md  # Official rules documentation reference
│   │   ├── templates/
│   │   │   ├── always-apply.md      # Always apply template
│   │   │   ├── git-message.md       # Git commit rules template
│   │   │   ├── intelligent-apply.md # Intelligent trigger template
│   │   │   ├── manual-only.md       # Manual trigger template
│   │   │   └── specific-files.md     # File matching template
│   │   └── SKILL.md
│   ├── skill-creator/                # Skill creation tool
│   │   ├── scripts/
│   │   │   └── quick_validate.py    # Quick validation script
│   │   └── SKILL.md
│   └── skill-stability-review/       # Skill stability review tool
│       ├── scripts/
│       │   └── review_skills.py     # Batch scanning script
│       └── SKILL.md
├── .github/                           # GitHub configuration
│   ├── ISSUE_TEMPLATE/               # Issue templates
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── question.md
│   └── PULL_REQUEST_TEMPLATE.md     # PR template
├── .gitignore                        # Git ignore rules
├── CONTRIBUTING.md                   # Contributing guidelines
├── LICENSE                          # MIT license
├── README.md                        # English entry documentation
└── README_zh.md                     # Chinese entry documentation
```

## Detailed Skills Introduction

### Agent Blueprint Architect

**Purpose**: A dedicated tool for creating and optimizing Trae Agent configurations.

**Core Capabilities**:
- Generate complete configurations directly usable for new Agents
- Define clear English identifiers (kebab-case format)
- Write concise Chinese system prompts
- Design accurate trigger conditions and boundaries
- Configure reasonable capability switches (minimum necessary principle)

**Windows/Trae Adaptation Points**:
- Designed for Windows Trae users by default
- Command examples prioritize PowerShell
- Path examples prioritize Windows paths or `%userprofile%`
- Avoid hardcoding Unix shells, macOS paths, or Linux-only paths
- Ensure local file paths and command execution are compatible with Windows

**Use Cases**:
- Creating new Trae Agents
- Optimizing existing Agent configurations
- Splitting broad Agents into new ones with clear responsibilities
- Designing Agent capability switch configurations

### Creating Trae Rules

**Purpose**: A tool for creating, modifying, and organizing Trae IDE rule files.

**Core Capabilities**:
- Create project rules under `.trae/rules/` directory
- Support module-level rule configuration
- Provide multiple activation modes (global, file matching, intelligent trigger, manual)
- Generate Git commit message rules conforming to Trae specifications
- Work with AGENTS.md and CLAUDE.md

**Windows/Trae Adaptation Points**:
- Use forward slashes as path separator examples
- Provide Windows-accessible path examples
- Ensure frontmatter format conforms to Trae specifications
- Validate rule file nesting levels (no more than 3 levels)
- Support `scene: git_message` for Git commit scenarios

**Template System**:
| Template File | Purpose | Activation Mode |
|---|---|---|
| always-apply.md | Global project constraints | alwaysApply: true |
| specific-files.md | File pattern matching | globs mode |
| intelligent-apply.md | Semantic trigger scenarios | description mode |
| manual-only.md | Manual reference rules | #Rule reference |
| git-message.md | Commit message format | scene: git_message |

**Resource Files**:
- `trae-rules-reference.md`: Local reference of official rules documentation, containing complete activation modes, path specifications, and best practices

### Skill Creator

**Purpose**: A complete workflow tool for creating, modifying, and refactoring Trae Skills.

**Core Capabilities**:
- Design Skill trigger conditions and usage boundaries
- Define clear input/output contracts
- Write executable workflows
- Create auxiliary resources (examples, templates, resources)
- Validate Skill frontmatter format

**Windows/Trae Adaptation Points**:
- Clearly distinguish between project-level Skills and global Skills
- Global Skill path: `%userprofile%\.trae\skills\` (Windows)
- Project Skill path: `<project>\.trae\skills\`
- Use forward slashes in Skill examples, avoid Windows hardcoding
- Dependencies must verify Trae IDE/Trae CLI/MCP availability

**Helper Scripts**:
- `quick_validate.py`: Lightweight Skill validation script
  - Validate frontmatter format
  - Check required fields (name, description)
  - Validate naming conventions (kebab-case)
  - Check description length limit (≤1024 characters)
  - Pure Python standard library implementation, no external dependencies

**Creation Workflow**:
1. Capture intent: Identify repeated tasks and trigger scenarios
2. Establish baseline: Understand Trae's default behavior without Skills
3. Define evaluation cases: Cover normal paths, boundary paths, and negative paths
4. Write minimal Skill: Include only necessary content
5. Add resources: Create only when directly reducing ambiguity
6. Validate and iterate: Run validation scripts and test

### Skill Stability Review

**Purpose**: A complete tool for reviewing and optimizing Trae Skill stability, with focus on Windows/Trae compatibility.

**Core Capabilities**:
- Scan complete Skill package contents (SKILL.md + scripts + resources + templates)
- Detect Windows/Trae risk patterns
- Evaluate Chinese user adaptation quality
- Verify script synchronization and execution stability
- Generate quantifiable scoring reports

**Windows/Trae Adaptation Points**:
- Detect PowerShell-incompatible commands (bash, export, sudo, chmod)
- Detect Unix path patterns (~/, /tmp/)
- Detect container commands that may fail in Windows environments
- Path conversion rules:
  - Windows host examples use Windows paths
  - Container/remote/URL paths keep native form
  - Paths in JSON/config correctly escaped
- Verify script exit code behavior (non-zero indicates failure)
- Ensure stdout/stderr output is machine-readable

**Helper Scripts**:
- `review_skills.py`: Lightweight batch scanning script
  - Discover Skill folders and SKILL.md files
  - Run quick_validate.py for basic validation
  - Scan Windows/Trae risk patterns
  - Generate preliminary scores and review leads
  - Support JSON and Markdown format output
  - Support single Skill or batch scanning

**Scoring Dimensions**:
| Dimension | Weight | Content |
|---|---|---|
| Agent Executability | 25% | Clarity of steps, inputs, outputs, failure handling |
| Windows/Trae Fit | 20% | Command, path, shell assumption compatibility |
| Script Sync | 20% | Script consistency with SKILL.md |
| Trigger and Boundary | 15% | Correct triggering, avoiding overlap, Chinese/English anchors |
| Chinese User Fit | 10% | Natural Simplified Chinese communication |
| Maintainability | 10% | Conciseness, scope, update difficulty |

**Severity Levels**:
- **Blocking**: Breaks execution, risks destructive behavior, corrupts output
- **High**: May cause wrong shell, wrong path, false success
- **Medium**: Causes avoidable ambiguity, manual friction, occasional misfire
- **Low**: Polish, maintainability, packaging noise

**Recommended Scan Commands**:
```powershell
# Full directory scan
python .\skill-stability-review\scripts\review_skills.py --root "C:\Users\skyler\.trae\skills" --markdown --include-generated

# Single Skill JSON scan
python .\skill-stability-review\scripts\review_skills.py --skill "C:\Users\skyler\.trae\skills\everything-search" --json
```

## Windows/Trae Adaptation Highlights

### Unified Platform Strategy

| Feature | Windows Adaptation Implementation |
|---|---|
| Path Specification | Prioritize `%userprofile%` and absolute paths, avoid Unix-style `~/` and `/tmp/` |
| Command Syntax | PowerShell native commands, avoid bash-specific syntax |
| Path Separators | Use forward slashes internally (`/`), adapt to Windows when outputting |
| File Operations | Avoid `rm -rf`, use safe file operations |
| Environment Variables | Use `%VAR%` format instead of `$VAR` |
| Shell Types | Clearly distinguish between host shell and container shell |

### Path Conversion Rules

```
Host-side commands, input paths, output paths → Windows accessible paths
Container paths, URLs, API paths → Keep native form
Paths in JSON/config → Correctly escaped (e.g., `D:\\APP\\Tools\\...`)
```

### Risk Pattern Detection

Automatically detect the following Windows/Trae-unfriendly patterns:
- ````bash``` code blocks (host-side guidance)
- `export KEY=value` (Unix-specific)
- `cat <<'EOF'` (Heredoc)
- `sudo`, `chmod` (Unix admin commands)
- `rm -rf` (host-side risky operations)
- `/tmp/`, `~/` (Unix paths)
- Unescaped Windows paths

## File Checklist

| File Path | Type | Description |
|---|---|---|
| agent-blueprint-architect/SKILL.md | Required | Complete Agent blueprint design specification |
| creating-trae-rules/SKILL.md | Required | Trae rules creation workflow |
| creating-trae-rules/resources/trae-rules-reference.md | Reference | Official rules documentation local reference |
| creating-trae-rules/templates/always-apply.md | Template | Always apply template |
| creating-trae-rules/templates/git-message.md | Template | Git commit rules template |
| creating-trae-rules/templates/intelligent-apply.md | Template | Intelligent trigger template |
| creating-trae-rules/templates/manual-only.md | Template | Manual trigger template |
| creating-trae-rules/templates/specific-files.md | Template | File matching template |
| skill-creator/SKILL.md | Required | Complete Skill creation guide |
| skill-creator/scripts/quick_validate.py | Script | Skill quick validation tool |
| skill-stability-review/SKILL.md | Required | Skill stability review specification |
| skill-stability-review/scripts/review_skills.py | Script | Batch scanning and scoring tool |

## Usage Recommendations

### Beginner Path

1. Start with **skill-creator** to understand basic Skill structure
2. Use **creating-trae-rules** to create project rules
3. Reference **agent-blueprint-architect** to design custom Agents
4. Use **skill-stability-review** to validate and optimize

### Advanced Optimization Path

1. Run `review_skills.py` to scan existing Skills
2. Fix High/Blocking issues based on scoring reports
3. Verify scripts are actually executable in Windows environments
4. Update trigger conditions to improve natural language matching

### Best Practices

- Run quick_validate.py before creating new Skills
- Scan with review_skills.py before batch deployment
- Maintain balance of Chinese and English in trigger descriptions
- Prioritize PowerShell command examples
- Avoid hardcoding platform assumptions in Skills
