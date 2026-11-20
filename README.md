# Emami Insights Hub Mini

## Project Goal
A sales analytics web app with login, role-based dashboards and an AI "Ask your data" chat.
Built with a FastAPI + Postgres backend, a Next.js (TypeScript) frontend, and a Claude-powered query and RAG layer.
All data is synthetic: it mimics Emami's structure (regions, brands, SKUs, distributors) but contains no real company figures.

## Prerequisites
| Tool | Version |
|------|---------|
| Git | 2.x or later |
| VS Code | latest |
| Python | 3.11+ |
| Node.js | 20+ |
| GitHub account | with an SSH key added |

## Environment Check
Run from the repository root:

```bash
bash scripts/check_env.sh
```

The script prints the version of each required tool.
- **Exit code 0**: all tools are installed and the machine is ready.
- **Non-zero exit**: a tool is missing. Install it and run the script again.

To see the exit code: `echo $?`

## Project Structure
```
backend/        FastAPI app and Python warm-ups
frontend/       Next.js app and TypeScript warm-ups
data_pipeline/  ETL scripts
datasets/       Synthetic datasets
docs/           Documentation (git-drills.md, etc.)
scripts/        Helper scripts (check_env.sh)
```

## Code Quality (pre-commit)
Python uses **ruff** (lint) and **black** (format). TypeScript uses **prettier** (format) and **eslint** (lint).
They run automatically on every commit. One-time setup from the repository root:

```bash
python -m venv .venv
source .venv/Scripts/activate        # Windows Git Bash (macOS/Linux: .venv/bin/activate)
pip install -r backend/requirements-dev.txt
(cd frontend && npm install)
pre-commit install
```

Run every check by hand with `pre-commit run --all-files`. More details and a demo are in `docs/quality-tools.md`.

## Branch Rules
- `main`: stable, release-ready code only. No direct commits.
- `dev`: integration branch. All work is merged here through Pull Requests.
- Work branches are created from `dev`, using these prefixes:
  - `feature/<short-name>`: new features
  - `fix/<short-name>`: bug fixes
  - `docs/<short-name>`: documentation
  - `chore/<short-name>`: tooling and config
- Open a PR into `dev` using the PR template, answer every review comment, and delete the branch after merging.
- Never commit `.env`, `venv/`, `node_modules/` or any credentials.

## Commit Rules (Conventional Commits)
Format: `<type>(optional scope): <short description>`

| Type | Use for |
|------|---------|
| `feat` | a new feature |
| `fix` | a bug fix |
| `docs` | documentation only |
| `style` | formatting, no logic change |
| `refactor` | code change that is not a fix or a feature |
| `test` | adding or updating tests |
| `chore` | tooling, config, dependencies |

Examples:
- `feat(backend): add fiscal_year helper`
- `docs: add prerequisites to README`
- `chore: add pre-commit hook with ruff and black`

Keep the description in lower case, in the imperative mood ("add", not "added"), with no full stop at the end.
