# SchemeRadar

Source-backed government scholarship discovery and explainable student eligibility matching.
The repository was initially named SchemeScout. SchemeRadar is the application name.

## Current state — read before demonstrating

A runnable Next.js/FastAPI application is implemented with tested validation, matching, UI/API contracts,
and a compiled LangGraph workflow. **The live TinyFish → Qwen → PostgreSQL discovery flow has not been
verified in this environment.** No API key, PostgreSQL server, Ollama installation, or model was available.
No scholarship fixtures are presented as live data. The UI displays actionable service errors instead.
See [current development status](DEVELOPMENT_STATUS.md) for acceptance criteria and test results.

## Stack and architecture

- Next.js App Router, React, TypeScript, Tailwind CSS 4
- Python 3.11+, FastAPI, Pydantic 2, Uvicorn
- Ollama `qwen2.5:3b` for schema-constrained extraction and evidence-grounded answers
- LangGraph for an **explicit pipeline with conditional mode routing**, not autonomous reasoning
- TinyFish hosted MCP `search` and `fetch_content`, using the official Python MCP client
- PostgreSQL/psycopg pool, JSONB rules, parameterized SQL, transactional upserts
- Optional pgvector extension migration only; **embeddings and semantic retrieval are not implemented**
- Python logging, bounded request bodies/concurrency; no Redis or tracing service required

```text
Student profile → same-origin Next.js /api proxy → FastAPI/Pydantic
  → LangGraph: search → fetch → Qwen extraction → optional bounded detail-page hop → evidence/schema guards
  → PostgreSQL commit → deterministic match → structured UI results
CHAT → PostgreSQL lexical evidence retrieval → Qwen answer
RESEARCH → search/fetch/extract/store → source and completeness report
```

Eligibility never uses the LLM or vector similarity to make its decision. The matcher returns
`ELIGIBLE`, `NEEDS_INFORMATION`, or `NOT_ELIGIBLE`, with a result for every supported criterion.
An explicit failure dominates uncertainty. An eligible result needs all rules to pass, an approved
source and explicit extraction coverage. This is guidance, not an official award decision.

## Layout

```text
backend/
  app/
    main.py              FastAPI, validation/errors, body/concurrency limits, API routes
    config.py            environment settings (secret-valued credentials)
    models.py            profiles, extraction, rules, results and API contracts
    eligibility.py       deterministic normalized comparisons
    security.py          exact-host policy, URL/DNS guards
    providers.py         TinyFish MCP and Ollama adapters
    workflow.py          LangGraph mode routing and workflow nodes
    db.py                PostgreSQL pool, migrations and repositories
    migrations/          packaged reproducible SQL
  tests/                 unit, API, graph, provider-contract and opt-in live tests
  pyproject.toml          dependency declarations
  requirements.lock      exact resolved Python environment, including test tools
frontend/
  src/app/               overview, profile, discover, eligibility, research, assistant, about
  src/components/        workspace, shared forms, scholarship results
  src/lib/               typed contracts, same-origin API client and tests
tests/smoke.py            actual HTTP integration check through the frontend proxy
docs/                    operational status and source policy
compose.yaml             PostgreSQL (pgvector-capable image), Ollama, backend, frontend
```

## Local setup

Requirements: Python 3.11+, Node.js 22+, PostgreSQL 17 (or Docker Compose), Ollama, and a TinyFish API key.
Internet access must allow TinyFish's endpoint and model/container downloads. The Arena development
sandbox only permits selected GitHub/npm/PyPI hosts, so it cannot perform these external live checks.

From the repository root:

```bash
cp .env.example .env
python -m venv .venv
.venv/bin/pip install -r backend/requirements.lock
.venv/bin/pip install --no-deps -e backend
cd frontend
npm ci
cd ..
```

Edit `.env` privately. No real credentials belong in Git or chat. These are the supported names:

| Name | Purpose / nonsecret example |
| --- | --- |
| DATABASE_URL | PostgreSQL DSN, e.g. `postgresql://schemeradar:change-me@localhost:5432/schemeradar` |
| POSTGRES_PASSWORD | Local Compose database password; choose a new private value |
| COMPOSE_DATABASE_URL | Compose backend DSN using host `db` and the same password |
| TINYFISH_API_KEY | API key, intentionally blank in the template |
| OLLAMA_URL | `http://localhost:11434` for local setup |
| OLLAMA_MODEL | `qwen2.5:3b` |
| FRONTEND_ORIGIN | `http://localhost:3000`; exact direct frontend origin for CORS |
| REQUEST_TIMEOUT | Ollama/tool-call timeout seconds, default 90 |
| MAX_CONCURRENT_WORKFLOWS | Shared expensive-operation capacity per backend process, default 2 |
| BACKEND_URL | Server-side Next.js proxy destination, default `http://127.0.0.1:8000` |
| TEST_DATABASE_URL | Optional dedicated disposable PostgreSQL test database |
| RUN_LIVE_SERVICES | `1` opts into the real discovery test, which stores real records |

Percent-encode reserved characters in database credentials used in DSNs. Backend settings read the root
`.env` when commands run from the root. For Next.js, set `BACKEND_URL` in the process environment or
`frontend/.env.local` if its default is unsuitable. Production rewrites capture this URL at build time;
set it **before** `npm run build`. Never put credentials into `NEXT_PUBLIC_*` variables.

### PostgreSQL

With Docker available, start only the database for local development:

```bash
docker compose up -d db
.venv/bin/python -m app.db
```

Alternatively provision PostgreSQL yourself and set `DATABASE_URL`. The user needs permission to create
tables/indexes in the selected database. The migration runner refuses an existing incompatible flat scholarships table before DDL. It uses a transaction and advisory lock;
rerunning the initial migration is safe. It is intentionally not run on ordinary API startup.

Rules and scholarship metadata are JSONB; source URL/evidence/fetch time have a related source table.
Identity is canonical source URL plus case/space-normalized name. Discovery re-reads each committed record before matching. Upserts prevent repeat records for
that identity. The same scheme appearing at different URLs is not automatically merged.
Student profiles are **not** persisted on the server.

The optional extension can be enabled on a pgvector-capable server after the initial migration:

```bash
# Supply your connection securely through normal PostgreSQL environment/configuration.
psql -f backend/app/migrations/002_pgvector_optional.sql
```

This does not add vectors or enable semantic search. Chat currently uses bounded lexical retrieval with source links; irrelevant records are not automatically used for unrelated questions.
The sandbox has ~4 GiB RAM and no Ollama runtime, so a second embedding model was deliberately deferred
until Qwen's actual memory/latency can be measured. Do not claim complete pgvector integration.

### Ollama / Qwen

Install Ollama on your machine, then:

```bash
ollama serve
# In a separate terminal:
ollama pull qwen2.5:3b
ollama list
```

The application uses Ollama's `/api/chat` JSON-schema output and temperature zero. Verify inference on
your hardware; extraction uses up to a 16K context budget and may exceed small machines' memory/latency.
Fetched text is capped at 40,000 characters, and failed/truncated output is rejected rather than guessed.

### TinyFish

Set `TINYFISH_API_KEY` privately. The adapter connects to `https://agent.tinyfish.ai/mcp`, sends
`X-API-Key`, initializes MCP, and calls `search` / `fetch_content`. It does not use paid browser-automation
tools. Provider account policies/quotas still apply; no payment was initiated during development.

Contract reference: [TinyFish official tool reference](https://github.com/tinyfish-io/tinyfish-mcp-server/blob/main/docs/tools.md).
Response parsing is tested with synthetic contract fixtures, **not captured live responses**. A live
account smoke test must confirm response shapes; unsupported shapes are not silently considered success.

## Start locally

Terminal 1, at repository root:

```bash
.venv/bin/python -m app.db
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log
```

Terminal 2:

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000`. All browser requests use relative `/api/...` URLs. Next.js proxies to the
backend, so remote preview browsers never call their own localhost. The dev server permits Arena
`*.e2b.app` previews. Set `FRONTEND_ORIGIN` for direct cross-origin deployments; do not use wildcard CORS.

Production frontend:

```bash
cd frontend
npm run build
npm start
```

### Full Docker Compose setup (configuration supplied, not tested in this sandbox)

After setting the database passwords/DSN and TinyFish key in root `.env`:

```bash
docker compose up -d db ollama
docker compose exec ollama ollama pull qwen2.5:3b
docker compose up --build -d backend frontend
```

The backend image applies its packaged initial migration before serving. Database/Ollama ports bind to
host loopback; frontend listens on port 3000. Ollama models and PostgreSQL use persistent volumes.
Container builds and startup remain unverified because Docker is unavailable here.

## API

Interactive docs: `/api/docs` through Next.js, or backend `/docs`. JSON schema: `/api/openapi.json`.
Swagger UI loads its assets from a CDN; raw OpenAPI remains available if the CDN is blocked.

| Method / path | Request | Result |
| --- | --- | --- |
| GET `/api/health` | none | process liveness only |
| GET `/api/ready` | none | database/schema readiness and configuration indicators; does not claim provider health |
| POST `/api/profile` | six nullable student fields | validated profile, no server storage |
| GET `/api/scholarships` | none | up to 30 most recently updated records |
| POST `/api/search` | `{ "query": "Karnataka engineering scholarships" }` | source list, official-domain flags |
| POST `/api/fetch` | `{ "urls": ["https://scholarships.gov.in/"] }` | successful pages and per-source errors |
| POST `/api/extract` | `{ "url": "https://scholarships.gov.in/" }` | refetched/validated extraction; does not itself store |
| POST `/api/eligibility` | Profile | matches against records actually retrieved from PostgreSQL; no web/model call |
| POST `/api/match` | `{ "profile": {...}, "scholarships": [...] }` | untrusted-record rule evaluation; client records cannot claim confirmed provenance |
| POST `/api/chat` | `{ "query": "Which documents are required?" }` | evidence-grounded answer in AgentResult |
| POST `/api/research` | `{ "query": "..." }` | search/fetch/extract/store report |
| POST `/api/discover` | `{ "mode": "DISCOVER", "query": "...", "profile": {...} }` | stored extractions and deterministic matches |
| POST `/api/agent` | `{ "mode": "CHAT|RESEARCH|DISCOVER", "query": "...", "profile": null }` | same pipeline; profile mandatory for DISCOVER |

Profile fields: `state`, `course`, `education_level`, `study_year`, `annual_income` (integer INR), `category`.
Match criteria use `UNKNOWN`, explicit unrestricted `ANY`, or `RESTRICTED` (exact values or explicitly inclusive/exclusive
numeric bounds), with source quotations. No alias inference: “B.Tech” is not silently mapped to
“Engineering.” Unsupported disjoint numeric ranges/additional eligibility dimensions remain uncertain.

HTTP errors: 422 validation/policy, 413 body limit, 429 shared capacity, 502 provider/output failure,
503 missing/unavailable database/configuration, 504 time budget. A successful research response can
contain partial source/extraction failures in `errors`; inspect it rather than assuming all pages worked.
Search/fetch are limited to three URLs per tool request. Research can follow three additional actual approved detail links when initial extraction fails. The whole research budget, including database preflight, is 360 seconds; committed records can remain if a later step fails.

## Testing

```bash
.venv/bin/ruff check backend
.venv/bin/pytest -q backend/tests
.venv/bin/pip check
cd frontend
npm run typecheck
npm run lint
npm test
npm run build
npm audit --omit=dev
cd ..
# With both actual servers running:
.venv/bin/python tests/smoke.py
```

Database test: set `TEST_DATABASE_URL` to a **dedicated test database** before pytest. The test applies
migrations, inserts/upserts a synthetic fixture and removes that fixture; do not point it at production.
CI is configured with PostgreSQL 17 for this test, but the remote workflow has not been run here.

Full live test (real calls, may consume provider quotas and stores real scholarship records): configure
all services, then `RUN_LIVE_SERVICES=1 .venv/bin/pytest -q backend/tests/test_services_live.py`.
The test deliberately fails if no validated scholarships are produced; it never passes with fabricated data.

## Demonstration sequence

1. Confirm database readiness and real TinyFish/Ollama connectivity with the opt-in tests.
2. Open Overview and Student profile; enter Karnataka, exact course/education/category names,
   year of study and family income. Save to validate against FastAPI.
3. Open Discover and search “Karnataka engineering scholarships”.
4. Inspect workflow steps, approved sources, extraction errors and saved records.
5. Inspect eligibility checks and unknown requirements; never promise an eligible result for every query.
6. Open the source/application link and confirm the current official text/deadline.
7. Open Research to inspect source evidence and automated retrieval timestamps.
8. Open Eligibility and recheck stored scholarships after editing your profile. No fresh web search is needed.
9. Ask the assistant about documents or benefits from the records actually stored and inspect the supplied source links.
10. Reload Overview to confirm persisted scholarship retrieval.

If services are unavailable, demonstrate validation/error behavior and explain the blocker instead of
claiming live discovery worked.

## Known limitations and security posture

- **Not yet hackathon-accepted:** live providers, PostgreSQL and full browser E2E remain unverified.
- No registration/authentication: entering a profile is the supported MVP path. Profile data is sent
  to the backend for matching, held in tab sessionStorage, and not stored server-side or logged.
- Conversation history is UI-only; each question retrieves evidence independently. No cross-turn memory.
- Exact-domain coverage is intentionally narrow. See [source policy and remote-fetch residual risks](docs/source-policy.md).
- One scholarship per fetched page. If extraction fails, the graph may follow up to three approved scholarship/detail links actually returned by fetched pages, for one extra hop only (six page fetches maximum). It does not recursively crawl the web.
- Quotation/schema checks reject fabricated literal facts, but do not prove semantic accuracy of
  AI-extracted rules or the model's completeness assessment. Human source review remains necessary.
- No embeddings/semantic retrieval; no Redis; no optional telemetry integration. LangGraph's transitive
  dependencies may include telemetry libraries, but application tracing is not configured.
- No per-user quotas, authentication, distributed rate limiting or job queue. Shared in-process capacity
  and body limits are only MVP safeguards. Put behind access control/reverse-proxy limits before public use.
- Logs avoid bodies, credentials and exception messages. Automatic fetch timestamps are not human verification.
- No stale-record refresh scheduling, history/versioning, cross-URL deduplication or application submission.
- Responsive styles and component states are tested/static-reviewed; visual browser, mobile and assistive
  technology testing still need a real browser. Docker deployment also needs a real smoke test.


## Approved reliability update — 31 October 2026

The current implementation adds the dedicated `/eligibility` and `/about` pages. Eligibility can
recheck existing PostgreSQL records using the current profile without another model/web request.
Profile edits clear old decisions, and late responses for a different profile are discarded.
Research and discovery keep separate session state; response queries, actual per-page fetch/extraction
outcomes, exact source evidence and assistant grounding links are displayed. Backend/provider output
is checked at runtime by the frontend, not simply cast to TypeScript types. Temporary backend outages
do not erase a saved profile; the interface offers retry.

Rule extraction supports explicit inclusive/exclusive numeric bounds. Guardrails verify numbers
(including lakh/crore notation) and text values appear in quoted evidence, but cannot prove semantic
completeness. Conflicting or unsupported/disjoint requirements must remain unknown; source review
is still necessary. Source acquisition time is preserved separately from extraction completion.
Provider envelope/type failures and initialization timeouts return safe errors rather than accidental 500s.

`AgentResult` now also includes `query` and `source_outcomes` (URL, stage, success/failure, message).
Fetched Page payloads include approved links, acquisition timestamps and a truncation flag. Truncated pages cannot claim complete eligibility coverage. Rule fields add
`minimum_exclusive` and `maximum_exclusive`, defaulting false for existing stored JSON. No new database
migration is required for these additive JSON fields. No legacy Windows database was moved or upgraded.

### Windows PowerShell — use the actual cloned root

Do not blindly move the historical outer backend or nested Windows repository. These commands apply
to this checkout structure, where the root contains both `backend` and `frontend`. Existing Windows
service credentials should stay private. The backend reads root `.env` when launched from that root.

```powershell
Set-Location "<actual-clone-root>"
# Only if no private .env exists; edit it locally afterward:
if (!(Test-Path .env)) { Copy-Item .env.example .env }
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e backend
# Only after inspecting/backing up any existing database and confirming DATABASE_URL:
.\.venv\Scripts\python.exe -m app.db
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log
```

In a second terminal:

```powershell
Set-Location "<actual-clone-root>\frontend"
npm ci
npm run build
npm start
```

If port 3000 belongs to another project, do not stop unrelated containers. Use `npm run dev -- --port 3001`
and set `FRONTEND_ORIGIN` for direct cross-origin calls as needed. The browser still uses the same-origin
API proxy. `NEXT_PUBLIC_API_URL` is not consumed by this version; do not configure a preview browser to
call its own localhost. Change server-side `BACKEND_URL` before building when the backend destination changes.

Compose currently selects PostgreSQL 17. Do not attach an existing PostgreSQL 16 data directory/volume
to it: use a separately reviewed logical migration, or keep using your existing correctly configured server.
Do not remove unrelated IDS containers or database volumes. Compose itself remains unverified here.

### Real HTTP tests (no provider/account calls)

With frontend/backend running, these exercise the frontend runtime guards and actual FastAPI through
Next.js, using explicitly synthetic request inputs, not substitute discovery results:

```powershell
Set-Location "<actual-clone-root>\frontend"
$env:SCHEMERADAR_SMOKE_URL = "http://127.0.0.1:3000"
npm test
Remove-Item Env:SCHEMERADAR_SMOKE_URL
```

In POSIX shells: `SCHEMERADAR_SMOKE_URL=http://127.0.0.1:3000 npm test` from frontend.
Without this variable, the three real-HTTP tests are explicitly skipped, not silently mocked.
The database and full live-provider tests remain separately opt-in as described above.

Fresh approved-update results: **125 backend tests passed, two external tests skipped; 31 frontend
tests passed with real HTTP enabled** (28 unit/component/contract tests plus three actual proxy tests).
Ruff, ESLint, TypeScript, production build, pip consistency and full npm audit passed. All seven page
routes returned HTTP 200. PostgreSQL/TinyFish/Ollama live success and real-browser E2E remain unverified;
missing configuration returns explicit 503 responses. See `DEVELOPMENT_STATUS.md` for the current ledger.
