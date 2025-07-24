# Contributing to semantic-memory

First, thank you for considering contributing! We welcome improvements, bug fixes, and new features.

## How to Contribute

1. **Fork** the repo and create a branch:
   ```bash
   git checkout -b feature/my-feature
   ```
2. **Install dependencies**:
   ```bash
   poetry install
   ```
3. **Follow code standards**:
   - Format with **Black** (`make format`).
   - Lint with **Ruff** and **flake8** (`make lint`).
   - Type-check with **mypy** (`make type-check`).
4. **Write tests** for new functionality and ensure existing tests pass:
   ```bash
   pytest --cov=.
   ```
5. **Commit messages** should follow Conventional Commits:
   - `feat: add new RAG endpoint`
   - `fix: handle empty cache read`
   - `docs: update README`
6. **Push** and open a **Pull Request** (PR) against `main`:
   - PRs must pass CI: lint, type-check, tests, coverage.
   - Add a clear description of changes and link any related issues.

## Branch Protection & Review

- `main` is protected: all PRs require two approvals and passing CI.
- Use draft PRs for early feedback.

## Issue Tracking

- Use GitHub Issues for bug reports and feature requests.
- Label issues with `bug`, `enhancement`, `question`, etc.

## Code of Conduct

Please read [CODE\_OF\_CONDUCT.md](CODE_OF_CONDUCT.md) to understand expected behavior.

