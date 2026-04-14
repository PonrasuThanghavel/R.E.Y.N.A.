# GitHub Workflows Documentation

This project uses GitHub Actions for continuous integration and code quality checks. All workflows are located in `.github/workflows/`.

## Available Workflows

### 1. **CI Pipeline** (`ci.yaml`)
**Comprehensive quality gate** - Runs all checks together
- Triggers: Push to `main`/`develop`, Pull requests
- Steps:
  - Code formatting check (Black)
  - Import sorting check (isort)
  - Linting (Flake8)
  - Type checking (mypy)
  - Unit tests (pytest)
  - Security scan (Bandit)
- **Best for**: Before merging PRs

### 2. **Tests** (`tests.yaml`)
**Multi-version testing** - Tests across multiple Python versions
- Triggers: Push to `main`/`develop`, Pull requests
- Versions: 3.9, 3.10, 3.11, 3.12
- Steps:
  - Installs dependencies
  - Runs pytest with coverage
  - Uploads coverage to Codecov
- **Best for**: Ensuring compatibility and coverage

### 3. **Code Formatting** (`black.yaml`)
**Black formatter compliance** - Ensures consistent code style
- Triggers: Push to `main`/`develop`, Pull requests
- Steps:
  - Checks if code meets Black formatting standards
  - Shows diff if formatting issues found
- **Best for**: Maintaining code style consistency

### 4. **Linting** (`linting.yaml`)
**Code quality analysis** - Static code analysis
- Triggers: Push to `main`/`develop`, Pull requests
- Tools:
  - Flake8: PEP 8 style guide enforcement
  - Pylint: Code complexity and errors
  - isort: Import organization
- **Best for**: Finding potential bugs and style issues

### 5. **Type Checking** (`type-check.yaml`)
**Static type analysis** - Python type hints validation
- Triggers: Push to `main`/`develop`, Pull requests
- Tools:
  - mypy: Optional type checking
  - pyright: Alternative type checker
- **Best for**: Catching type-related bugs early

### 6. **Security Scan** (`bandit.yaml`)
**Security vulnerability detection** - Identifies security issues
- Triggers: Push to `main`/`develop`, Pull requests
- Steps:
  - Scans for common security problems
  - Checks patterns like hardcoded passwords, SQL injection risks
- **Best for**: Maintaining code security

### 7. **Dependency Check** (`dependencies.yaml`)
**Dependency vulnerability scanning** - Weekly security checks
- Triggers: Push to `main`/`develop`, Pull requests, Weekly (Sunday 00:00 UTC)
- Tools:
  - Safety: Known vulnerability database
  - pip-audit: Audits installed packages
  - pip list: Shows outdated packages
- **Best for**: Keeping dependencies secure and up-to-date

## Workflow Triggers

| Workflow | Push | PR | Schedule |
|----------|------|----|---------:|
| CI Pipeline | main, develop | main, develop | - |
| Tests | main, develop | main, develop | - |
| Code Formatting | main, develop | main, develop | - |
| Linting | main, develop | main, develop | - |
| Type Checking | main, develop | main, develop | - |
| Security Scan | main, develop | main, develop | - |
| Dependency Check | main, develop | main, develop | Weekly |

## Workflow Status

Check the **Actions** tab in your GitHub repository to see:
- Workflow run history
- Individual step results
- Logs and error messages
- Artifact downloads

## Local Testing

Run checks locally before pushing:

```bash
# Code formatting
black src/ tests/ tools/

# Import sorting
isort src/ tests/ tools/

# Linting
flake8 src/ tests/ tools/

# Type checking
mypy src/ --ignore-missing-imports

# Tests with coverage
pytest tests/ --cov=src

# Security check
bandit -r src/
```

## Customizing Workflows

To modify a workflow:
1. Edit the `.yaml` file in `.github/workflows/`
2. Push to trigger a test run
3. Check results in the Actions tab

Common customizations:
- Add/remove Python versions in `tests.yaml`
- Adjust linting rules in `linting.yaml`
- Add more steps as needed

## CI Status Badge

Add this to your README.md to display CI status:

```markdown
![CI Pipeline](https://github.com/<owner>/<repo>/actions/workflows/ci.yaml/badge.svg)
```

## Troubleshooting

### Workflow not triggering?
- Check branch is `main` or `develop`
- Verify YAML syntax correctness
- Clear your local cache: `git pull --rebase origin`

### Tests failing?
- Check Python version compatibility
- Review test output in Actions tab logs
- Run tests locally: `pytest tests/ -v`

### Security scan reporting false positives?
- Review bandit recommendations
- Suppress false positives with bandit comments if needed
- Run locally: `bandit -r src/ -l`

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [mypy Documentation](https://mypy.readthedocs.io/)
