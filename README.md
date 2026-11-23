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

## Sales API (Week 3)
A read-only FastAPI service over the cleaned Week 2 dataset (`data_pipeline/output/clean_sales.csv`).
`SalesRepository` loads the CSV into pandas once at startup; routers never touch pandas.

### Run the API
From `backend/`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1          # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive documentation of every endpoint.
If PowerShell blocks the activate script, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first.

### Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Returns `{"status": "ok"}` |
| GET | `/sales` | Filtered, paginated rows: `items`, `page`, `page_size`, `total` |
| GET | `/sales/summary` | `net_value`, `quantity`, `row_count`, plus `groups` when `group_by` is set |
| GET | `/regions` | Distinct regions |
| GET | `/brands` | Distinct brands |
| GET | `/skus` | Distinct SKUs with name and brand |
| GET | `/distributors` | Distinct distributors with name, region and state |

**Filters** (on `/sales` and `/sales/summary`): `region`, `state`, `brand`, `sku_code`, `channel`,
`date_from`, `date_to` (both `YYYY-MM-DD`, inclusive) and `is_return`.
`/sales` also takes `page` (default 1) and `page_size` (default 50, max 200).
`/sales/summary` also takes `group_by`: `region`, `state`, `brand`, `sku`, `channel` or `month`.

**Errors** always use one shape:

```json
{"error": {"code": "VALIDATION_ERROR", "message": "page_size: Input should be less than or equal to 200"}}
```

| Status | Code | When |
|--------|------|------|
| 422 | `VALIDATION_ERROR` | Invalid input (bad date, unknown region/channel/group_by, page_size over 200) |
| 404 | `SKU_NOT_FOUND` | `sku_code` filter value does not exist |
| 404 | `NOT_FOUND` | Unknown URL |
| 500 | `INTERNAL_ERROR` | Unexpected error (details are logged, never returned) |

CORS allows only `http://localhost:3000`.

### Test the API
From `backend/` with the virtual environment active:

```powershell
pip install -r requirements-dev.txt
python -m pytest             # all tests (API tests are in backend/tests/)
python -m pytest tests -v    # API tests only, one line per test
python -m ruff check .
python -m black --check .
```

To try requests by hand, open `docs/api-examples.http` in VS Code with the
**REST Client** extension and click **Send Request** above any call.

### OpenAPI file
`docs/openapi.json` is generated from the app. After changing any endpoint or model,
regenerate it from `backend/` and commit it (a test fails if it is out of date):

```powershell
python -m scripts.export_openapi
```

### Configuration
Optional environment variables (defaults work out of the box):

| Variable | Default | Purpose |
|----------|---------|---------|
| `INSIGHTS_SALES_CSV_PATH` | `data_pipeline/output/clean_sales.csv` | CSV the API loads |
| `INSIGHTS_CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed browser origins (JSON list) |

### Backend layout
```
backend/app/
  main.py           app, startup (loads CSV), CORS, routers
  config.py         settings
  dependencies.py   wires repository -> service -> routes
  errors.py         common error shape and handlers
  routers/          HTTP endpoints only (no pandas)
  services/         business logic (e.g. unknown sku_code -> 404)
  repositories/     SalesRepository: all pandas / CSV access
  schemas/          Pydantic request/response models and enums
backend/tests/      pytest + TestClient API tests
backend/scripts/    export_openapi.py
```

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
