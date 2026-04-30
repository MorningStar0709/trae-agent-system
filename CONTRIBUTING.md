# Contributing to Trae Skills

Thank you for your interest in the Trae Skills project! We welcome contributions in various forms, including but not limited to reporting issues, submitting fixes, improving documentation, or creating new Skills.

## Ways to Contribute

### Reporting Issues

If you find a bug or have a feature suggestion, please report it through GitHub Issues. Please include the following information:

- **Issue Description**: Clear description of the problem or suggested feature
- **Reproduction Steps**: If it's a bug, provide detailed reproduction steps
- **Environment Info**: Windows version, Trae version, etc.
- **Expected vs Actual**: Describe the expected behavior and actual behavior

### Submitting Code

#### Fork & Clone

1. Fork this repository
2. Clone your Fork locally
   ```powershell
   git clone https://github.com/MorningStar0709/trae-agent-system.git
cd trae-agent-os
   ```

3. Create a feature branch
   ```powershell
   git checkout -b feature/your-feature-name
   ```

#### Development Standards

##### Skill Structure Standards

All Skills must include:

```
skill-name/
├── SKILL.md                    # Required: Main skill file
├── examples/                  # Optional: Input/output examples
├── templates/                  # Optional: Template files
├── resources/                  # Optional: Resource files
└── scripts/                    # Optional: Helper scripts
```

##### Naming Standards

- **Skill directory name**: kebab-case (e.g., `skill-name`)
- **Skill name**: Lowercase letters, digits, and hyphens
- **Description length**: No more than 1024 characters
- **Chinese priority**: Trigger descriptions use Simplified Chinese

##### Code Standards

- **Python scripts**:
  - Use Python 3 standard library, avoid external dependencies
  - Include failure paths and non-zero exit codes
  - Output machine-readable format (JSON recommended)
  
- **PowerShell examples**:
  - Prioritize cross-platform compatible commands
  - Avoid bash-specific syntax
  - Use forward slashes or correct Windows format for paths

##### Windows/Trae Adaptation Requirements

- Avoid hardcoding Unix paths (`/tmp/`, `~/`)
- Avoid Unix-specific commands (`sudo`, `chmod`, `rm -rf`)
- Avoid `bash` code blocks for host-side guidance
- Use PowerShell-compatible command examples
- Path examples use `%userprofile%` or absolute paths

#### Validation Checklist

Please run the following validations before submitting:

```powershell
# 1. Validate Skill format
python skills/skill-creator/scripts/quick_validate.py skills/<skill-name>

# 2. Run stability scanning
python skills/skill-stability-review/scripts/review_skills.py --skill skills/<skill-name> --json

# 3. Check Windows compatibility
python skills/skill-stability-review/scripts/review_skills.py --root . --markdown
```

#### Submitting Pull Requests

1. Ensure all validations pass
2. Fill in a clear PR description:
   - The problem solved or new feature added
   - Test validation results
   - Screenshots or demos (if applicable)
3. Link related Issues (use `Fixes #issue-number`)

### Improving Documentation

- Use Simplified Chinese, keep terminology consistent
- Verify code examples are executable
- Update cross-references to related files
- Check Windows environment adaptation of documentation

## Development Workflow

### Local Testing

1. **Create a test Skill**
   ```powershell
   mkdir skills/test-skill
   # Create basic SKILL.md
   ```

2. **Run validation**
   ```powershell
   python skills/skill-creator/scripts/quick_validate.py skills/test-skill
   ```

3. **Test scanning**
   ```powershell
   python skills/skill-stability-review/scripts/review_skills.py --skill skills/test-skill --markdown
   ```

### Code Review

All submissions require code review, focusing on:

- **Functional Correctness**: Whether the Skill works as expected
- **Windows Compatibility**: Whether it adapts to Windows environments
- **Trigger Boundaries**: Whether it avoids misfiring
- **Failure Handling**: Whether it has clear error handling
- **Documentation Completeness**: Whether it includes necessary instructions

## FAQ

**Q: How do I know if my Skill needs to be created?**

A: Consider creating a Skill if you find:
- The same task appears multiple times
- Specific trigger conditions and boundaries are needed
- Clear execution workflow and failure handling are required

**Q: What's the difference between Skill and Rule?**

A: 
- **Skill**: Reusable capability module with complete workflow and execution logic
- **Rule**: Lightweight instruction file that controls Trae's behavior in specific scenarios

**Q: How to test Skill performance in real scenarios?**

A:
1. Import the Skill in Trae IDE
2. Test with common trigger phrases
3. Verify boundary cases (should trigger and should not trigger scenarios)
4. Check if output format meets expectations

## Contact

- **GitHub Issues**: [Submit issues](https://github.com/MorningStar0709/trae-agent-os/issues)

## Code of Conduct

Please maintain a friendly and professional attitude, respect others' opinions and suggestions. We welcome diverse contributions, but all contributors should follow basic community conduct guidelines.

---

Thank you again for your contribution! Every contribution is vital to the project's development.
