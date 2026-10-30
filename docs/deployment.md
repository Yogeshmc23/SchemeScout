# Startup and deployment

## Existing local setup (preferred when PostgreSQL/Ollama already work)

Preserve existing services and data. From the repository root, create/configure
`.env` using `.env.example`; never commit it. Point DATABASE_URL to the existing
compatible database. Keep `OLLAMA_MODEL=qwen2.5:3b`. Do not containerize or upgrade
an existing Windows database simply to match the optional Compose file.

POSIX, from the repository root:

```sh
python3.11 -m venv .venv
.venv/bin/pip install -r backend/requirements.lock
.venv/bin/pip install --no-deps -e backend
# Run with cwd=root so .env resolves at the root:
PYTHONPATH=backend .venv/bin/python -m app.db
PYTHONPATH=backend .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log
```

In another terminal, start/verify local Ollama (`ollama serve` only if not already
running) and run `ollama pull qwen2.5:3b`. In a third terminal:

```sh
cd frontend
npm ci
npm run build
npm start
```

PowerShell, from the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e backend
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m app.db
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log
# Separate terminal: cd frontend; npm ci; npm run build; npm start
```

Do not move `backend` into a nested checkout. `.env` resolves from the working
directory; the commands above keep it at the root. Readiness: `/api/v1/ready`;
OpenAPI: `/api/openapi.json`. Readiness does not verify TinyFish or Qwen live calls.
Next proxies browser-relative `/api/v1` requests to BACKEND_URL (server-side only).
For a remote preview, bind to `0.0.0.0`; never put localhost URLs in browser code.

## Optional isolated Compose setup

Inspect port ownership, existing containers, PostgreSQL version and volumes first.
Do not stop unrelated IDS containers or attach existing PG16 data to PG17. The
supplied stack uses its own named volumes, PG17 and an Ollama container; it is an
alternative, not required for a working local setup. Set POSTGRES_PASSWORD,
COMPOSE_DATABASE_URL and TINYFISH_API_KEY in root `.env`:

```sh
docker compose up -d db ollama
docker compose exec ollama ollama pull qwen2.5:3b
docker compose up --build -d backend frontend
```

Container startup runs migrations before serving. Backend and database published
ports use loopback; frontend is port 3000. Keep private unless access control/TLS
are provided. No Docker operation was performed in this sandbox (Docker absent).

## Validation and acceptance

```sh
.venv/bin/pytest -q backend/tests
.venv/bin/ruff check backend
.venv/bin/pip check
cd frontend
npm run typecheck
npm run lint
SCHEMERADAR_SMOKE_URL=http://127.0.0.1:3000 npm test
npm run build
```

Dedicated PostgreSQL integration requires TEST_DATABASE_URL; never production.
Live provider tests require explicit opt-in/configuration (see README). Confirm
migration idempotence, duplicate upsert, snapshots, rollback and restart persistence
on the actual target database. Then use a real student profile to discover official
sources, inspect source text, confirm Qwen output, save/reload/match, open details
and history, and ask an evidence-grounded assistant question. Verify in a real
browser, including errors and mobile layout. These gates remain UNVERIFIED here;
fixture tests and healthy HTTP endpoints do not replace them.

Optional research history defaults off; enable only with informed query-retention
policy and trusted access. No embeddings/vector retrieval or Redis service needs
to be provisioned for this implementation.
