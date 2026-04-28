# Trae Skills Collection

[![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)](https://www.trae.ai/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

## About This Project

**Trae Skills** is a curated collection of custom skills designed specifically for [Trae IDE](https://www.trae.ai/) on Windows. These skills help developers automate repetitive tasks, establish development rules, and optimize coding workflows with a focus on Windows environment compatibility.

## Core Features

- **Windows-First Design**: Thoroughly tested and optimized for Windows environments
- **Chinese User Support**: Native Simplified Chinese with balanced English technical anchors
- **Stable Execution**: Comprehensive validation scripts ensure reliable agent behavior
- **Production-Ready**: Built-in stability review tools and validation workflows

## Skills Included

| Skill | Description |
|---|---|
| **agent-blueprint-architect** | Create and optimize Trae agent configurations with clear boundaries and triggers |
| **creating-trae-rules** | Define and organize Trae project rules with multiple activation modes |
| **skill-creator** | Scaffold, review, and iterate on new Trae skills |
| **skill-stability-review** | Audit skills for Windows/Trae compatibility and execution stability |

## Quick Start

### Installation

```powershell
# Clone the repository
git clone https://github.com/MorningStar0709/trae-skills.git
cd trae-skills

# Import to Trae
# Open Trae IDE → Settings → Skills Management → Import from skills/ directory
```

### Validation

```powershell
# Validate a specific skill
python skills/skill-creator/scripts/quick_validate.py skills/<skill-name>

# Scan for Windows compatibility
python skills/skill-stability-review/scripts/review_skills.py --skill skills/<skill-name> --markdown
```

## Documentation

For detailed technical documentation, see [docs/SKILLS_INTRO.md](docs/SKILLS_INTRO.md).

For Chinese documentation, see [docs/SKILLS_INTRO_zh.md](docs/SKILLS_INTRO_zh.md).

## Windows/Trae Adaptation

All skills follow these principles:

- **PowerShell Commands**: Primary command syntax for Windows environments
- **Windows Paths**: Uses `%userprofile%` and absolute paths
- **Risk Detection**: Automatic detection of Unix-specific patterns
- **Path Conversion**: Clear rules for host/container/URL path handling

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the [MIT License](LICENSE).
