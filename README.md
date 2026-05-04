# Project Name

Production-grade Python project template.

## Setup

**macOS/Linux:**
```bash
pyenv install 3.12.10
pyenv local 3.12.10
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

**Windows:**
```powershell
pyenv install 3.12.10
pyenv local 3.12.10
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
```

> **VS Code:** Select your interpreter via the Command Palette (`Python: Select Interpreter`)
> and point it at `venv/bin/python` (macOS/Linux) or `venv\Scripts\python` (Windows).

## Usage

```bash
python -m app.main
```

## Development

| Command | Description |
|---------|-------------|
| `make lint` | Lint with ruff |
| `make fmt` | Format with ruff |
| `make typecheck` | Type check with mypy |
| `make test` | Run tests with coverage |
| `make audit` | Security audit with pip-audit |
| `make pre-commit` | Run all pre-commit hooks |
| `make all` | Run everything |

## Pre-commit hooks

```bash
pre-commit install
```

Runs ruff (lint + format), mypy, and standard file checks on every commit. CI enforces the same checks.

## Dependency Management

Runtime dependencies are declared in `pyproject.toml` and pinned in `requirements.txt`.
Dev dependencies are pinned in `requirements-dev.txt`.

To add a new runtime dependency:

1. Add it to `requirements.in` (loose constraint)
2. Regenerate the lock file: `pip-compile requirements.in`
3. Update `pyproject.toml` `dependencies` to match

To add a new dev dependency, add it directly to `requirements-dev.txt` with a pinned version.
