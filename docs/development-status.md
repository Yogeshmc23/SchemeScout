# SchemeRadar development handoff

Date: 2026-10-30. Branch: `arena/ae4fd465-schemescout`.

## Overall status

**Implemented and locally tested application foundation; NOT yet accepted as a live hackathon MVP.**
The baseline was README-only, with no application or existing Ollama setup in this checkout.
No existing application code was replaced. README was updated; all other deliverable files are new.
No credentials were printed or committed. No scholarship fixtures are served in the application.

## Phase outcomes

1. **Inspection:** confirmed clean branch and README-only checkout. No backend/frontend baseline tests existed.
   Python/Node available; Docker, PostgreSQL and Ollama executables absent. No configured service-variable
   names found. RAM approximately 4 GiB. External network allowlist excludes TinyFish/model/container hosts.
2. **Backend:** Pydantic contracts, FastAPI endpoints, safe errors, body/concurrency limits, structured
   logs, TinyFish MCP integration and Qwen extraction adapter implemented. Import/API/unit tests pass.
   Provider payload/response handling has synthetic contract tests, not live-account verification.
3. **Database:** packaged versioned/idempotent SQL, advisory-locked migration runner, pooled connections,
   transactional source/record upserts and retrieval implemented. PostgreSQL test is opt-in and skipped here.
   JSONB contains eligibility rules and extraction metadata; student profiles are not stored.
   Optional pgvector extension migration supplied; embedding generation/storage/query are not implemented.
4. **AI/orchestration:** actual compiled LangGraph pipeline runs in tests with explicit provider doubles.
   CHAT/RESEARCH/DISCOVER routing, partial fetch/extraction errors, storage and matching are covered.
   It is not marketed as an autonomous reasoning agent. Live Qwen/TinyFish remain blocked.
5. **Eligibility:** six supported criteria, inclusive numeric boundaries, exact normalized text matching,
   unknowns, unsupported coverage, source provenance and expired deadlines tested.
6. **Frontend:** five pages, navigation, profile summary, discovery/results, source evidence, research,
   chat, error/loading/empty states and responsive CSS implemented. No fake metrics or scholarship data.
7. **Integration:** actual production Next.js → FastAPI health/profile requests succeed. Missing services
   surface actionable 503 responses. Full live discovery cannot be verified in this sandbox.
8. **QA/docs:** backend/frontend tests, lint/typecheck/build pass. Compose, Dockerfiles and CI supplied,
   but Docker and remote GitHub Actions have not been run. Setup/source policy documentation provided.

## Actual verification results

| Check | Actual result |
| --- | --- |
| Backend application import | Passed |
| `ruff check backend` | Passed |
| `pytest -q backend/tests` | **84 passed, 2 skipped** |
| `pip check` | Passed; no broken requirements |
| Python wheel build | Passed with isolated build; both SQL migrations packaged |
| `npm run typecheck` | Passed |
| `npm run lint` | Passed, no warnings |
| `npm test` | **9 passed** (API service and jsdom form/chat behavior) |
| `npm run build` | Passed; all five application routes generated |
| `npm audit` | **0 vulnerabilities**, including dev dependencies |
| Backend Uvicorn startup | Passed on `0.0.0.0:8000` |
| Frontend development startup | Passed on `0.0.0.0:3000` |
| Frontend production startup | Passed on `0.0.0.0:3000`; left running as preview |
| HTTP page checks | All five routes returned 200, dev and production |
| Real frontend proxy health/profile | Passed, including invalid profile 422 |
| Production proxy docs/OpenAPI | Passed |
| Production Arena-style Host header | Returned 200 |
| Live missing-configuration behavior | Search, Discover, Chat returned actionable 503; no invented results |
| PostgreSQL persistence test | Skipped: no dedicated `TEST_DATABASE_URL` server |
| Live Karnataka provider/model/database test | Skipped: no services/key; requires `RUN_LIVE_SERVICES=1` |
| Visual/real-browser E2E | Not run; no browser installed. jsdom tests do not substitute for this |
| Docker Compose | Not run; Docker unavailable |
| Git diff whitespace check | Passed |

An expanded dependency audit found vulnerabilities in the initially selected Vitest 3 development
dependencies. Vitest was upgraded to 5.0.5, config adjusted, and tests/typechecks/build/audit rerun cleanly.
An initial non-isolated Python wheel attempt lacked the environment's wheel build tool; the standard
isolated build succeeded. No failing checks were hidden or disabled.

## Acceptance criteria

| Criterion | Status |
| --- | --- |
| Frontend starts | VERIFIED locally, development and production |
| Backend starts | VERIFIED locally |
| PostgreSQL connects | UNVERIFIED; requires server/configuration |
| TinyFish Search works live | UNVERIFIED; adapter/tests implemented |
| TinyFish Fetch works live | UNVERIFIED; adapter/tests implemented |
| Qwen extraction works live | UNVERIFIED; adapter/validation tests implemented |
| Records store/retrieve in PostgreSQL | UNVERIFIED live; SQL/repository/test implemented |
| Deterministic matching | VERIFIED in unit/API tests |
| LangGraph routing | VERIFIED with test doubles, not live providers |
| Frontend/backend communication | VERIFIED with actual HTTP proxy requests |
| Profiles can be submitted | VERIFIED through actual proxy and component tests |
| Discovery end-to-end | NOT VERIFIED with live external services |
| Eligibility explanations | VERIFIED in matching/API tests; implemented in UI |
| Official links displayed | Implemented; real source click-through not browser-verified |
| Graceful errors | VERIFIED for tested invalid/configuration/provider-fixture failures |
| Production frontend build | VERIFIED |
| Automated backend/frontend tests | 84 + 9 passing; 2 live tests explicitly skipped |
| Setup documentation | Implemented; local dependency/start commands checked, external setup not verified |

## External/manual actions before a truthful hackathon demo

1. Configure `DATABASE_URL` and provision PostgreSQL. Run the initial migration.
2. Install/start Ollama and pull `qwen2.5:3b`. Measure extraction memory/latency before adding another model.
3. Configure `TINYFISH_API_KEY` privately in the backend environment, not chat or source control.
4. Use an environment with outbound access to TinyFish and model/container registries.
5. Recheck approved domain ownership/canonical redirects; expand the reviewed policy as needed.
6. Run the real database test using a dedicated test database.
7. Run `RUN_LIVE_SERVICES=1` live discovery test. Confirm actual provider response shapes against the
   adapter. If they differ, adjust the single adapter and its contract tests rather than adding fallback data.
8. Complete the README's browser demonstration, including source links, mobile layout, keyboard access
   and an assistant answer grounded in records actually extracted and stored.
9. Smoke-test Docker Compose if that is the intended demo deployment.

## Remaining limitations / engineering priorities

- No embeddings or semantic pgvector search. Extension availability is not vector integration.
- Qwen schema and exact-quote guards cannot establish semantic correctness/completeness of extracted
  eligibility rules. Human official-source review is still necessary.
- Only six eligibility dimensions supported; unsupported criteria must stay uncertain. Numeric rules
  support inclusive ranges, not arbitrary/disjoint operators. No course/category alias inference.
- One scholarship per source page; portal/listing pages can yield no valid extraction. No recursive crawl.
- TinyFish result parsing is based on documentation plus synthetic tests, not captured live payloads.
- Remote-fetch DNS/redirect control cannot be fully enforced locally; see source policy.
- No per-user/distributed quotas or authentication. Entry by profile is implemented, not registration.
- Long-running workflows are synchronous, bounded to 360 seconds, not resumable jobs. Partial commits
  can survive a later failure. Database commits are not falsely reported as complete after a failed run.
- No automated refresh, historical versioning or cross-URL entity deduplication.
- Chat retrieves recent records lexically, not semantically. It has visible page-local history but does
  not send prior turns to the LLM. AI-generated citations/summaries still require user source confirmation.
- TypeScript contracts mirror Pydantic manually; add schema-generated types/contract CI as APIs grow.
- Broader accessibility, real-browser/mobile and deployment checks remain necessary.

## Resume without rewriting

Keep `models.py` as the contract authority, `providers.py` as the only external-service adapter layer,
`workflow.py` as orchestration, `db.py` as persistence, and `eligibility.py` as the only decision engine.
Start with live service provisioning and contract verification, not another app scaffold. Existing mock
fixtures are only tests. Do not introduce mock live results to make a demo appear successful.

## Dependency changes

Runtime Python: FastAPI, Uvicorn, pydantic-settings/Pydantic, httpx, psycopg (binary/pool), LangGraph, MCP.
Python QA: pytest, pytest-asyncio, Ruff. Exact resolved transitive versions: `backend/requirements.lock`.
Frontend runtime: Next.js, React, React DOM. Frontend QA/build: TypeScript, Tailwind/PostCSS, type packages,
ESLint/Next config, Vitest 5, jsdom, React Testing Library. Exact versions: `frontend/package-lock.json`.
No existing dependencies were removed. No Redis, alternative LLM provider, paid automation or separate
microservice was introduced. PostgreSQL/Ollama are required service dependencies, not verified installs.

## Exact deliverable file inventory

Modified: `README.md`. Created files:

```text
.env.example
.github/workflows/ci.yml
.gitignore
backend/.dockerignore
backend/Dockerfile
backend/app/__init__.py
backend/app/config.py
backend/app/db.py
backend/app/eligibility.py
backend/app/main.py
backend/app/migrations/001_initial.sql
backend/app/migrations/002_pgvector_optional.sql
backend/app/models.py
backend/app/providers.py
backend/app/security.py
backend/app/workflow.py
backend/pyproject.toml
backend/requirements.lock
backend/tests/conftest.py
backend/tests/test_api.py
backend/tests/test_database_live.py
backend/tests/test_eligibility.py
backend/tests/test_providers.py
backend/tests/test_security.py
backend/tests/test_services_live.py
backend/tests/test_workflow.py
compose.yaml
docs/development-status.md
docs/source-policy.md
frontend/.dockerignore
frontend/Dockerfile
frontend/eslint.config.mjs
frontend/next-env.d.ts
frontend/next.config.ts
frontend/package-lock.json
frontend/package.json
frontend/postcss.config.mjs
frontend/src/app/assistant/page.tsx
frontend/src/app/discover/page.tsx
frontend/src/app/globals.css
frontend/src/app/layout.tsx
frontend/src/app/page.tsx
frontend/src/app/profile/page.tsx
frontend/src/app/research/page.tsx
frontend/src/components/forms.test.tsx
frontend/src/components/research-form.tsx
frontend/src/components/results.tsx
frontend/src/components/workspace.tsx
frontend/src/lib/api.test.ts
frontend/src/lib/api.ts
frontend/src/lib/types.ts
frontend/tsconfig.json
frontend/vitest.config.ts
tests/smoke.py
```

Generated virtual environments, node_modules, Next.js outputs, wheel/build artifacts, caches and
package metadata are ignored and are not deliverable source files.
