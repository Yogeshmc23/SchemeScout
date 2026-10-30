# SchemeRadar — Current Repository Audit

**Audit date:** 31 October 2026 (Asia/Calcutta)  
**Repository:** `/home/user/SchemeScout`  
**Branch:** `arena/ae4fd465-schemescout`  
**Scope:** Current checkout, supplied Windows handover, master development directive, and audit directive. Existing README and `docs/development-status.md` were also reconciled.

## Audit boundaries and status definitions

No application, test, dependency, database, deployment or existing documentation files were changed. No dependencies were installed, services started/stopped, migrations applied, credentials displayed or database writes attempted. The only authorized outputs are this report and the requested root `DEVELOPMENT_STATUS.md`. This interprets the instruction to save reports as a narrow exception to the inspection-only restriction.

- **COMPLETE:** The stated, bounded feature/check was verified; not a claim about untested dependencies.
- **PARTIAL:** Code exists, but an identified requirement or connection is incomplete.
- **NOT STARTED:** No implementation was found in this checkout.
- **UNVERIFIED:** An implementation or external capability cannot currently be exercised/confirmed.

Historical test passes are identified explicitly. They are not presented as fresh results. No completion percentage is assigned because effort-weighted MVP scope has not been established.

# A. Executive summary

SchemeRadar is **not an empty repository anymore**. It contains a modular FastAPI application, typed schemas, a deterministic matching engine, TinyFish MCP and Ollama adapters, a real LangGraph graph, PostgreSQL persistence code and migrations, a five-page Next.js frontend, tests, Docker configuration and CI. Do not rebuild or move this implementation based on the older Windows folder layout.

However, it is **not currently running or independently reverified as a live MVP**:

- No `.venv`, frontend `node_modules`, or `.next` directory is present.
- No listeners were found on local ports 3000, 8000, 5432 or 11434, and no matching application/provider processes were found.
- Python/Node exist, but required application/test packages are not installed in the inspected runtime.
- Docker, psql and Ollama executables were not found.
- No real `.env` / frontend `.env.local` exists in the inspected project locations. The relevant service-variable names are absent from the process environment. Only `.env.example` exists.
- The live TinyFish → fetch → Qwen → PostgreSQL → match path has not been verified here. The supplied history of successful Windows provider/database tests is not transferable to this runtime.
- The prior handoff records 84 backend passes/2 skips, nine frontend passes, builds and HTTP checks. Those are historical results; they were not rerun during this restricted audit.

**Fresh checks:** Python AST parsing passed for all 18 Python source/test files; ten direct assertions against the actual standard-library-only URL security module passed; manifests and route declarations were inspected; local service ports were probed; Git whitespace checking passed. These do not establish that FastAPI, Next.js or external integrations currently work.

## Reconciliation of the three supplied documents

| Subject | Historical handover / directive | Actual checkout / reconciliation |
| --- | --- | --- |
| Scope of this turn | Master requests implementation; final audit asks inspection first and approval | Audit takes precedence for this turn. No major development begins. Only two requested reports are created. |
| Git/project paths | Windows outer backend and nested frontend repository | One root `/home/user/SchemeScout` contains both `backend/` and `frontend/`. No consolidation/move is needed here. Windows machine contents cannot be inspected from this sandbox. |
| Git tracking | Historical setup implies existing backend commits may exist | `git ls-files` lists only README. README is modified; application/config/test folders are untracked in this branch working tree. They exist and must be preserved, but are not yet in HEAD. |
| Backend routes | `/chat`, `/search`, `/fetch`, `/research`, `/match`, `/extract`, `/discover-and-match`, `/agent` | Current contracts are `/api/...`, with `/api/discover` instead of `/discover-and-match`. Legacy aliases are absent. Current frontend matches the current API. Do not add incompatible aliases without a contract decision. |
| Agent/database duplicates | Root `agent.py`, `app/agents/agent.py`, two `database.py` versions | None of those historical modules exists. Current implementations are `backend/app/workflow.py` and `backend/app/db.py`. No duplicate application implementation was found. |
| Dependencies | Installed Windows Python packages, Node 24/npm 11 | Current executables are Python 3.11.2, Node 22.22.3, npm 10.9.8; project package installations are absent. Config uses httpx for Ollama, not the Python `ollama` SDK. |
| API environment variable | `NEXT_PUBLIC_API_URL=http://localhost:8000` | Current browser uses relative `/api/...`; Next.js server uses `BACKEND_URL`. This is appropriate for remote previews. Switching browser calls to localhost would break them outside the developer's machine. |
| Database | Existing Windows `schemeradar-db`, pgvector PostgreSQL 16, successful past connection | No local instance is available here. Compose specifies PostgreSQL 17, not migration of the Windows database. Never attach a PostgreSQL 16 data directory to a PostgreSQL 17 container. |
| Extraction | A prior portal test extracted three scholarship names | Current adapter deliberately extracts one scholarship and rejects multi-scheme directories by prompt. It does not preserve historical multi-scholarship extraction behavior. |
| Frontend | Starter/structure; pages planned; port 3001 | Five implemented page files exist; scripts default to port 3000. Neither 3000 nor 8000 is currently listening. `/eligibility` and `/about` pages are absent. |
| Hardware | Developer laptop has 16 GB RAM and installed Ollama | Historical local setup is useful for future live tests but is not the sandbox. Do not base a local embedding model decision on the sandbox's prior memory estimate alone. |

# B. Repository structure

Actual application structure, excluding Git internals and individual lockfile entries:

```text
SchemeScout/
├── README.md                         # only path currently tracked in HEAD
├── .env.example                     # names/placeholders only
├── .gitignore
├── compose.yaml
├── .github/workflows/ci.yml
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── pyproject.toml
│   ├── requirements.lock
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── providers.py
│   │   ├── security.py
│   │   ├── eligibility.py
│   │   ├── workflow.py
│   │   ├── db.py
│   │   └── migrations/
│   │       ├── 001_initial.sql
│   │       └── 002_pgvector_optional.sql
│   └── tests/
│       ├── conftest.py
│       ├── test_api.py
│       ├── test_database_live.py
│       ├── test_eligibility.py
│       ├── test_providers.py
│       ├── test_security.py
│       ├── test_services_live.py
│       └── test_workflow.py
├── frontend/
│   ├── Dockerfile / .dockerignore
│   ├── package.json / package-lock.json
│   ├── next.config.ts / next-env.d.ts
│   ├── tsconfig.json
│   ├── postcss.config.mjs
│   ├── eslint.config.mjs
│   ├── vitest.config.ts
│   └── src/
│       ├── app/
│       │   ├── layout.tsx / globals.css / page.tsx
│       │   ├── profile/page.tsx
│       │   ├── discover/page.tsx
│       │   ├── research/page.tsx
│       │   └── assistant/page.tsx
│       ├── components/
│       │   ├── workspace.tsx
│       │   ├── research-form.tsx
│       │   ├── results.tsx
│       │   └── forms.test.tsx
│       └── lib/
│           ├── api.ts / api.test.ts
│           └── types.ts
├── tests/smoke.py
└── docs/
    ├── development-status.md          # prior historical handoff; not overwritten
    └── source-policy.md
```

The two new root audit/status reports are the outputs of this audit, not preexisting application artifacts. The working tree was already modified/untracked before the audit. No nested repository or duplicate Python agent/database implementations were found in the inspected project structure.

# C. Technology stack

| Layer | Evidence and actual finding |
| --- | --- |
| Backend | FastAPI, Uvicorn, Python >=3.11; Pydantic 2 and pydantic-settings; declared in `backend/pyproject.toml`. |
| Model access | Async httpx requests to Ollama `/api/chat`, configured `qwen2.5:3b`, temperature zero, JSON-schema format for extraction. |
| Web | Python MCP client connects to hosted TinyFish `search` / `fetch_content`, API key from secret settings. No paid browser automation calls found. |
| Orchestration | `StateGraph` with actual search/fetch/extract/store/match/chat/summarize nodes and mode-dependent edges. Explicit pipeline, not autonomous planning. |
| Persistence | psycopg async pool; SQL parameters; JSONB scholarships and evidence/source records. |
| Vector capability | Optional `CREATE EXTENSION vector` SQL only; no embedding provider, vector column, index or vector query. |
| Frontend | Locked Next.js 16.4.3, React 19.3.1, TypeScript 5.9.3, Tailwind 4.3.3. These are lockfile versions, not installed runtime versions. |
| Testing | pytest/pytest-asyncio, Ruff; locked Vitest 5.0.5, jsdom, Testing Library, ESLint; actual HTTP smoke script. |
| Operations | Dockerfiles, pgvector PostgreSQL 17 Compose image, Ollama container, GitHub Actions. Not executed during this audit. |
| Optional infrastructure | No Redis implementation or application OpenTelemetry configuration. Some tracing-related packages are transitive dependencies. |

### Configuration names only

`backend/app/config.py` reads `DATABASE_URL`, `TINYFISH_API_KEY`, `OLLAMA_URL`, `OLLAMA_MODEL`, `FRONTEND_ORIGIN`, `REQUEST_TIMEOUT`, `MAX_CONCURRENT_WORKFLOWS`; `.env` resolution is relative to process working directory.

Compose/template additionally use `POSTGRES_PASSWORD`, `COMPOSE_DATABASE_URL`, `BACKEND_URL`. Test gates use `TEST_DATABASE_URL` and `RUN_LIVE_SERVICES`. No corresponding real configured service variables were found. `NEXT_PUBLIC_API_URL` is not consumed by the current application.

# D. Feature status

Test references below describe existing coverage unless explicitly labelled **fresh**. **Historical** means prior documented execution, not a rerun.

| Feature | Status | Evidence/files | Test result | Remaining work |
| --- | --- | --- | --- | --- |
| Backend/frontend co-location | COMPLETE | Both directories under verified Git root | Fresh filesystem/Git inspection | No relocation needed |
| Dependency manifests/lockfiles | COMPLETE | Python pyproject/lock, frontend package/lock | Fresh readable/parsed manifests | Restore installs only after approval; do not equate declarations with runtime |
| FastAPI startup and routing | UNVERIFIED | `backend/app/main.py` | Fresh AST valid; dependencies absent; startup historically passed | Reinstall then exercise startup/endpoints |
| Pydantic schemas/profile validation | UNVERIFIED | `models.py`, `test_eligibility.py`, `test_api.py` | Historical suite pass; cannot import Pydantic now | Rerun constraints and route contracts |
| TinyFish Search live | UNVERIFIED | `providers.py:TinyFish.search` | Synthetic provider fixtures; no current key/network test | Verify account, MCP protocol and real payloads |
| TinyFish Fetch live | UNVERIFIED | `providers.py:TinyFish.fetch` | Partial-failure/redirect fixtures exist | Live fetch, response-shape and unreachable-site tests |
| Ollama/Qwen live inference | UNVERIFIED | `providers.py:Ollama.generate` | Mock HTTP failure/extraction tests; no current service | Confirm model availability, latency, context and response handling |
| Structured extraction/grounding | PARTIAL | `models.py`, `providers.py:extract` | Fixture tests; live extraction unverified | Multi-scheme/detail-page workflow, rule semantics/conflicts, malformed-provider coverage |
| Research workflow | PARTIAL | `workflow.py`, `/api/research` | Historical graph tests with doubles | Live validation; meaningful evidence summary and fetched-source details |
| Deterministic six-field matching | UNVERIFIED | `eligibility.py`, `test_eligibility.py` | Historical unit/API tests; cannot rerun full stack now | Rerun; add unsupported/exclusive threshold tests |
| Decision explanations and unknowns | UNVERIFIED | `Check`, `Match`, matcher, results UI | Historical matching checks | Current suite/browser verification; explain coverage failures |
| Discover/extract/store/match pipeline | PARTIAL | `Workflow.run`, `/api/discover` | Graph-double tests, opt-in live test | Live dependency test; stored-record rematching and reliable source discovery |
| LangGraph execution | UNVERIFIED | `workflow.py`, `test_workflow.py` | Historical double-backed graph tests | Rerun API/graph modes and live services |
| Backend logging | PARTIAL | `main.py` request IDs/type-only errors | Historical correlation test | Cover 413/429/error request correlation; deployment log review |
| Backend errors/input limits | PARTIAL | `main.py`, `security.py`, model validators | Historical tests; fresh URL subset passed | Normalize malformed provider data; initialization/end-to-end timeout tests |
| Exact-host URL classification subset | COMPLETE | `security.py` | Fresh ten actual URL-policy assertions passed | Domain ownership/availability and broader negative tests remain separate |
| Remote-fetch SSRF safeguards | PARTIAL | URL/DNS guards, exact-host policy | No remote DNS/redirect execution during audit | Verify provider egress/redirect guarantees; maintain host policy |
| PostgreSQL connectivity/schema deployment | UNVERIFIED | `config.py`, `db.py`, initial SQL | No local service/DSN/client; live test not run | Connect to authorized database and inspect applied schema |
| Scholarship storage/retrieval | UNVERIFIED | `db.py:save/list` | Dedicated live test exists; not run | Test commits, rollback, reload retrieval and data integrity |
| Deduplication | PARTIAL | Unique `(source_url, normalized_name)`, upserts | Live uniqueness test not run | Confirm identity behavior; cross-URL duplicates not resolved |
| Extraction/source metadata | UNVERIFIED | JSONB, source table, extraction timestamps | Static schema only in this audit | Inspect actual stored values; correct timestamp/conflict semantics |
| pgvector extension installed | UNVERIFIED | `002_pgvector_optional.sql` | No database inspected | Verify actual extension; runner applies only migration 001 |
| Embedding generation/storage | NOT STARTED | No implementation/vector column | Not applicable | Assess actual laptop/model resources; implement only if needed |
| Semantic/vector retrieval | NOT STARTED | Chat explicitly uses lexical overlap | Not applicable | Model/dimensions/storage/query tests if selected |
| Next.js/TS/Tailwind runtime | UNVERIFIED | App Router, strict TS config, Tailwind import/PostCSS | Lockfiles inspected; dependencies missing; historical build passed | Restore dependencies; rerun types/lint/build/start |
| Dashboard | PARTIAL | `src/app/page.tsx` | Historical page smoke | Current browser test; distinguish backend failure from empty results |
| Student profile form | UNVERIFIED | `profile/page.tsx`, workspace, five component tests | Historical component/HTTP success | Rerun; fix stale-result/session-recovery behavior |
| Discovery UI | PARTIAL | `research-form.tsx`, discover page | Historical disabled/loading/error tests | Real successful result browser test; request/profile association |
| Eligibility result component | PARTIAL | `components/results.tsx` | No dedicated result-render/filter suite | Stale-state fixes, filter/empty tests, actual link checks |
| Dedicated `/eligibility` page | NOT STARTED | No route file | Not applicable | Decide route vs accepted embedded results requirement |
| Assistant UI and grounding | PARTIAL | Assistant page, `workflow.py:chat`, Ollama answer | Historical mocked UI/chat tests | Live answer, structured citations, retrieval quality |
| Research UI | PARTIAL | Research page/shared form/results | Historical fixture state tests | Persist/display query, per-page outcomes, evidence summary |
| About page | NOT STARTED | No route file | Not applicable | Add if required by final agreed scope |
| Navigation/reusable layout | UNVERIFIED | Workspace/layout/components | Fresh source inspection; historical smoke | Browser keyboard/navigation checks |
| Responsive/accessibility behavior | UNVERIFIED | CSS breakpoints/reduced-motion; labels/status roles | Fresh static CSS/markup inspection only | Real browser/mobile/screen-reader audit |
| API service/contracts | PARTIAL | `lib/api.ts`, `types.ts`, Next rewrite | Historical four mocked API tests | Reject malformed successful responses; runtime contract validation |
| Legacy endpoint compatibility | NOT STARTED | Unprefixed historical routes absent | Fresh route AST inventory | Agree whether aliases/translation are needed; don't change current clients blindly |
| Actual frontend/backend HTTP integration | UNVERIFIED | Proxy + `tests/smoke.py` | Historical passes; both services stopped now | Start after approval and rerun smoke |
| Automated tests/CI execution | UNVERIFIED | Backend/frontend suites, CI workflow | Historical 84 passes/2 skips and nine passes | Rerun locally and in CI; current dependencies absent |
| Docker deployment | UNVERIFIED | Compose and Dockerfiles | No Docker executable | Validate config/build/start, readiness and model setup |
| Setup/source-policy documentation | PARTIAL | README, previous handoff, policy | Fresh source/document reconciliation | PowerShell guidance, current-runtime caveats and approved contract decisions |
| Full live hackathon acceptance | UNVERIFIED | Opt-in test and demo sequence | Never established for this checkout | Complete checklist in section L |

# E. Completed functionality and actual verification evidence

## Fresh audit results

1. Verified Git root and active branch, tracked/untracked state, co-located app structure and absence of historical duplicates.
2. Parsed all **18** Python application/test/smoke files with `ast.parse`; no Python syntax errors were found. This is not dependency import or type/runtime validation.
3. Executed the actual `security.py` module in memory with the standard library and passed **ten URL-policy assertions**: seven unsafe/unapproved inputs rejected, a known approved host accepted, a third-party host not official, and URL fragment normalization correct. DNS and remote fetch were not tested.
4. Inspected declared route schemas and parsed package lock versions.
5. Confirmed required project dependencies are absent using Python module discovery and Node module resolution. No packages were installed.
6. Confirmed no local listener on the four required application/service ports. No services were started.
7. `git diff --check` passed for existing tracked changes.

## Historical evidence retained, not recertified

`docs/development-status.md` records 84 backend passes with two external tests skipped, nine frontend passes, successful lint/type/build, wheel packaging, npm audit and actual HTTP proxy/profile checks. Prior conversation also reports a later API-only 13-test pass after adding the backend root redirect. The redirect exists in current source. There is no new result asserting those suites pass today.

Current runtime prerequisites prevent pytest, backend imports, Next.js type/lint/test/build, DB integration and full E2E execution. Building would also generate artifacts, so it was not attempted under inspection-only instructions.

# F. Incomplete functionality

- Live verification of both TinyFish tools, Qwen inference/extraction, database connectivity and complete discovery.
- Real current runtime installations and startup checks.
- Multi-scholarship portal/detail-page discovery: extraction currently rejects directories instead of following scheme detail links.
- Re-evaluation of stored scholarships for an edited/new profile without performing another web research request.
- Extraction conflict resolution, richer numeric operators, unsupported criteria coverage checks and auditable semantic-rule validation.
- Research query retention, structured per-source fetch outcomes and substantive evidence-grounded research summary.
- Dedicated Eligibility/About pages required by supplied scope but absent from current routes. Embedded eligibility results already exist and should be reused.
- Structured assistant citations, relevance thresholds and conversation memory if desired. Current history is presentation-only.
- Embeddings, vector columns and semantic retrieval. These are optional, not a reason to block correct deterministic matching.
- Browser/mobile/accessibility testing, broader contract tests, deployment and public-service access controls.
- Windows-specific instructions aligned to the actual single-root structure and current `/api` contracts.

# G. Bugs and technical risks

Findings marked **source finding** were established by code inspection, not reproduced through a running full app. Do not confuse them with observed live production failures.

| Priority | Finding and evidence | Consequence / recommended verification |
| --- | --- | --- |
| CRITICAL | **Current runtime unavailable:** packages/services/config missing; fresh probes above. | Cannot demonstrate actual app now. Restore only after audit approval; then repeat full checks. |
| HIGH | **Most implementation remains untracked:** fresh `git ls-files` lists only README. | Current work exists in the workspace, but a Git-only clone of HEAD will not contain it. Review and deliberately version the intended source; do not discard it. |
| HIGH | **Stale eligibility after profile edits — source finding:** `Workspace.save(p)` clears `result` only when `p` is null, not when a non-null profile changes. | Prior eligibility can be shown beside a newly saved profile. Invalidate/associate results with profile/request identity and add a regression test. |
| HIGH | **Malformed provider responses can escape intended errors — source finding:** TinyFish uses `raw.get(...)` unless raw is a list; null/string responses cause AttributeError. Ollama JSON indexing can raise TypeError, but catches only HTTPError/ValueError/KeyError. | Invalid upstream payloads may surface generic 500s instead of controlled 502s. Validate outer types and add negative-response tests. |
| HIGH | **Quoted evidence does not prove extracted rule values:** extraction verifies that `rule.evidence` occurs in the page, but not that `values`/numeric bounds faithfully represent that quote; completeness is model-assessed. | A valid quote can accompany an incorrect threshold or missing mandatory criterion. Add adversarial extraction fixtures and explicit semantic/manual review safeguards. |
| HIGH | **Numeric restrictions support inclusive ranges only:** Criterion has minimum/maximum but no exclusive operators or disjoint sets. | Requirements like income strictly below a threshold cannot be represented exactly without a defined conversion policy; ambiguous rules must remain unknown, not rounded by the LLM. |
| HIGH | **Live provider contract not captured:** tests mock `TinyFish.call` with expected dictionaries, bypassing MCP result/session transport. | Adapter shape assumptions could block all results on a real account. Test actual Search/Fetch separately before full graph testing. |
| HIGH | **Directory rejection conflicts with practical discovery:** prompt returns `{}` for multi-scheme portals; no recursive detail link step exists. | Search may land on valid official homepages yet yield zero scholarship records. Add bounded official detail-page discovery, preserving current safeguards. |
| HIGH | **Remote SSRF boundary:** local DNS check cannot pin TinyFish's remote DNS or enforce redirects the provider doesn't report. | Do not advertise complete SSRF protection. Confirm remote guarantees and retain narrow hosts; `docs/source-policy.md` already acknowledges this. |
| HIGH | **No auth/per-user or distributed quotas:** current semaphore is process-local; expensive operations are available without identities. | Put behind access control/reverse-proxy limits before a public deployment. No need to introduce Redis for a private single-process demo. |
| MEDIUM | **CHAT/RESEARCH require DB readiness before doing anything:** `Workflow.run` calls `db.health()` outside the graph timeout. | A DB outage blocks chat and research, even evidence acquisition. Decide if this fail-closed behavior is intended; don't add a fake fallback. |
| MEDIUM | **No persisted-record reload before matching:** store node saves extracted objects, match node evaluates the same in-memory list. | DB commit is a prerequisite, but discovery doesn't prove retrieval works or match existing records. Add save/reload/rematch integration tests. |
| MEDIUM | **Successful non-JSON API response becomes null:** frontend catches response JSON parse errors then casts `data as T` for HTTP success. | Callers can throw on null rather than show a helpful invalid-response error. Validate JSON/content/schema explicitly. |
| MEDIUM | **Session restoration deletes profile on transient validation/network failure:** workspace catch removes sessionStorage with no visible recovery state. | A brief backend outage can discard the student's tab profile. Preserve it and surface retry/error state. |
| MEDIUM | **Research/Discover share one result without request identity:** query is not in AgentResult, state not separated by mode; headings always say Discovery results. | Results from another page/request can appear with a blank/different query; research can overwrite dashboard eligibility overview. Track mode/query/profile. |
| MEDIUM | **Assistant citations/relevance are not validated:** graph clears `sources`, selects up to four recent lexically ranked records even with zero overlap; frontend renders plain text. | Answers may be weakly grounded and source URLs not clickable structured citations. Add relevance filtering and verified source metadata. |
| MEDIUM | **Fetch status shape unchecked:** `item.get('status_code', 200) >= 400` assumes a number; other types are silently skipped by TypeError handling. | Real provider format differences can drop successful pages. Explicit schema mapping and safe error details needed. |
| MEDIUM | **Timeout gaps:** MCP initialization isn't inside `session.call_tool` wait_for; health precheck isn't inside graph's 360-second wait. | Claimed whole-request budget is not strictly enforced. Wrap lifecycle/preflight and test cancellation/partial commits. |
| MEDIUM | **Failure metadata isn't persisted:** errors are response strings; no durable extraction attempt/status table exists for failed pages. | Troubleshooting/history is lost after response. Add bounded attempt metadata if needed; don't store sensitive profile data. |
| MEDIUM | **Migration runner applies only 001; second script is optional/manual.** Version table records versions but does not dispatch ordered upgrade migrations. | Existing arbitrary legacy tables won't be upgraded by CREATE TABLE IF NOT EXISTS. Inspect Windows schema and plan migration before touching data. |
| MEDIUM | **Misleading source UI label:** ScholarshipCard always says “Read official source” even when `official_source` is false. | Conditional text must reflect source policy; don't imply government confirmation. |
| MEDIUM | **Source list is labelled “Sources checked” but contains search results, not necessarily fetched pages.** No structured fetched-source list is returned. | User cannot reliably distinguish discovered vs successfully read pages. Return/render per-source outcomes. |
| LOW | **Timestamp semantics:** `fetched_at` is assigned after model extraction, not at actual fetch; no human verification state. | Track actual acquisition time separately and keep automated-vs-human verification clear. |
| LOW | **Packaging/container weight:** backend lock includes test tools; frontend runtime image copies all build dependencies; Ollama image is latest. | Improve production footprint/pinning after functional validation, not by rewriting architecture. |

Additional limitations: no cross-URL deduplication, staleness refresh/history, conflict detection or robust successful-result rendering tests; course/category aliases are intentionally not guessed. Existing unit tests use explicit synthetic fixtures and no application fallback dataset was found.

# H. Database status

## What is implemented in source

`Database` creates an async pool only when a secret DATABASE_URL is configured, opens/closes it with app lifecycle, and refuses DB-backed operations when absent. SQL values are parameterized.

Migration 001 declares:

- `schema_migrations(version, applied_at)`.
- `scholarship_sources(url PRIMARY KEY, evidence, fetched_at, official)`.
- `scholarships(id identity PRIMARY KEY, source_url FK, normalized_name, name, data JSONB, updated_at)`.
- Unique `(source_url, normalized_name)`, updated-time index and JSONB rules GIN index.

`save()` upserts source and scholarship inside a transaction. `list()` reads recent JSONB and validates it as Scholarship. Metadata/rules reside within the JSONB record rather than the historical flat column schema. Profiles are intentionally not stored. No production in-memory database substitute exists.

## What was actually verified

No database server, connection, applied schema, extension installation, record count, inserts, reads, rollbacks or uniqueness enforcement was verified during this audit. There is no DSN configured here. Source SQL is a proposed/deployed-intent schema, not evidence of an actual deployed database.

`test_database_live.py` is a dedicated-DB test that would apply migrations, save the synthetic fixture twice, inspect retrieval/uniqueness, and delete its fixture. It was not run, both because prerequisites are absent and because the audit forbids database changes. `test_services_live.py` would store real discovered records and likewise was not run.

The optional second migration enables vector only. No vector data type column, embedding generation, vector index or similarity query exists. Semantic retrieval is **NOT STARTED**, not an untested completed feature.

The developer's Windows PostgreSQL 16 instance and its previously enabled extension remain **UNVERIFIED from this environment**. Current Compose PostgreSQL 17 is not evidence of migrating that existing data.

# I. Frontend status

| Route | Actual behavior in source | Verification boundary |
| --- | --- | --- |
| `/` | Loads recent scholarship records via GET `/api/scholarships`, shows profile and latest in-session match counts, links to working routes | Source inspected; historical HTTP pass, no current server/browser |
| `/profile` | Six optional fields, HTML constraints, numeric conversion, POST `/api/profile`; saves validated profile in tab sessionStorage; clear action | Five shared component tests include profile submission/failure; not rerun |
| `/discover` | Requires a saved profile; POST `/api/discover` with mode/query/profile; renders shared results | Loading/error logic exists; successful live workflow unverified |
| `/research` | POST `/api/research`; renders scholarships/sources/step strings and extraction evidence | No retained research query or per-page structured status; summary is count-based |
| `/assistant` | POST `/api/chat`; page-local messages, pending/error states, plain-text response | No cross-turn model context; no structured citation rendering |
| `/eligibility` | No page | Reuse existing Results component if a separate page is approved |
| `/about` | No page | Missing from requested page scope |

Shared layout/navigation, reusable fields/results, evidence expanders, status filters, links and accessible labels/status roles exist. CSS has breakpoints at 1500, 1150 and 760 pixels plus reduced-motion support. No `dangerouslySetInnerHTML` use was found in TSX files. These static checks do not establish responsive/accessibility quality in a browser.

The frontend uses relative API URLs and a server-side Next rewrite; this avoids remote-preview localhost mistakes. `BACKEND_URL` must be supplied before production build when changing the destination. TypeScript shapes currently mirror inspected backend schemas, but `api<T>` is a compile-time assertion, not runtime validation. No generated schema/TS contract check exists.

# J. Integration status

## Actual route contracts

All routes below are declared in `backend/app/main.py`; runtime responses cannot currently be exercised.

| Method/path | Body | Result/meaning |
| --- | --- | --- |
| GET `/` | None | 307 redirect to `/api/docs` |
| GET `/api/docs`, `/api/openapi.json` | None | Swagger HTML / OpenAPI; FastAPI also has its default docs/schema routes |
| GET `/api/health` | None | Process liveness, not provider/DB readiness |
| GET `/api/ready` | None | Queries scholarships table; reports DB ready and TinyFish configuration only; Ollama explicitly not probed |
| POST `/api/profile` | Profile | Validated profile; no server persistence |
| GET `/api/scholarships` | None | Recent Scholarship array |
| POST `/api/search` | Query `{query}` | Source array |
| POST `/api/fetch` | FetchRequest `{urls}` | `{pages, errors}` |
| POST `/api/extract` | ExtractRequest `{url}` | One refetched/validated Scholarship, not automatically saved |
| POST `/api/match` | `{profile, scholarships}` | Match array; caller's official flag forcibly cleared |
| POST `/api/agent` | AgentRequest `{mode, query, profile?}` | AgentResult; DISCOVER requires profile |
| POST `/api/chat` | Query | CHAT AgentResult |
| POST `/api/research` | Query | RESEARCH AgentResult |
| POST `/api/discover` | AgentRequest, mode must be DISCOVER | DISCOVER AgentResult |

Profile keys are `state`, `course`, `education_level`, `study_year`, `annual_income`, `category`; statuses are uppercase. Historical StudentProfile/ChatRequest shapes cannot simply be substituted.

The frontend calls profile, scholarships, discover, research and chat using matching current bodies. Search/fetch/extract/match/agent are exposed backend operations, not independently surfaced as frontend tool controls. That is not necessarily a missing UI connection: the discovery/research service calls these functions internally rather than making loopback HTTP requests.

No unprefixed legacy endpoints or `/discover-and-match` alias exist. Supporting historical clients requires an explicit adapter/contract decision after approval. Do not silently rename current endpoints.

## End-to-end trace

| Stage | Implemented connection | Test evidence / current status |
| --- | --- | --- |
| Student → profile form | Fields/constraints/session context | Historical component tests; current UNVERIFIED |
| Frontend → FastAPI | Relative API client + server rewrite | Historical real profile HTTP; current UNVERIFIED |
| FastAPI → validation | Pydantic models in route signatures | Syntax/source verified; dependencies absent |
| FastAPI → LangGraph | run_agent → Workflow.run → compiled graph | Historical API/graph doubles; current UNVERIFIED |
| LangGraph → TinyFish Search | Search node calls adapter | Mocked provider fixture only; live UNVERIFIED |
| Search → Fetch | Prioritizes approved results, max three URLs, isolates per-source ServiceError | Mock failure tests; live UNVERIFIED; no detail-link crawl |
| Fetch → Qwen extraction | Per-page schema/evidence validation | Synthetic model output only; live UNVERIFIED |
| Extraction → PostgreSQL | Store node calls transactional db.save | Code wired, not a disconnected persistence stub; live UNVERIFIED |
| PostgreSQL → matching | Matching follows successful save but uses extracted in-memory objects, not DB re-read | PARTIAL for stated stored-record workflow |
| Matching → frontend | Match array/check reasons/status filters | Code contracts align; real-result UI UNVERIFIED |
| Stored records → assistant | Reads up to 20 recent records; lexical ranking; up to four to Qwen | No semantic retrieval; live UNVERIFIED |

# K. Recommended development order

**No implementation is authorized by this audit outcome until approval.** Reuse existing layers; do not scaffold again.

| Order | Priority | Exact location | Action after approval | Completion check |
| --- | --- | --- | --- | --- |
| 1 | CRITICAL | Git root, `.gitignore`, manifests | Review/version intended existing source; restore reproducible Python/Node installs without overwriting developer files/secrets | Clean install from source, recorded test baseline; intended files present in Git diff |
| 2 | CRITICAL | Local environment, `backend/app/config.py`, README | Privately supply service configuration on the authorized laptop/runtime; resolve Windows single-root launch convention | Settings presence-only check, backend import/start, Next build/start and health/proxy smoke |
| 3 | CRITICAL | `backend/app/db.py`, migrations, `test_database_live.py` | Inspect actual existing database/schema before applying anything; verify compatibility, connectivity, rollback/upsert/retrieval | Authorized disposable DB tests; restart/retrieve evidence; no production fixture insertion |
| 4 | CRITICAL | `backend/app/providers.py`, `test_providers.py` | Verify real TinyFish Search/Fetch independently and normalize actual MCP output; harden malformed outer types/timeouts | Live sources + one successful fetch + unreachable failure; captured redacted contract fixtures |
| 5 | CRITICAL | Ollama setup, `providers.py`, extraction tests | Verify Qwen on developer laptop; test exact facts, thresholds, missing rules and unsupported criteria | Real extraction with source review, no invented facts; bounded failure/retry behavior |
| 6 | HIGH | `providers.py`, `workflow.py`, models | Add bounded official detail-page selection and reliable multi-source discovery; preserve per-page outcomes and extraction conflicts | Portal fixture → approved detail pages → valid records; inaccessible source doesn't suppress other successes |
| 7 | HIGH | `models.py`, `eligibility.py`, tests | Model unsupported/exclusive operators safely; validate rule semantics and coverage; rematch retrieved records | Boundary/adversarial rules tests; missing criteria never eligible; explicit violation fails |
| 8 | HIGH | `frontend/src/components/workspace.tsx`, shared forms/results/API | Fix profile-result invalidation, per-mode query identity, session recovery, malformed 2xx errors and source labels | Component regression tests and real HTTP/error handling checks |
| 9 | HIGH | AgentResult, workflow + Research/Assistant UI | Return structured fetched-source statuses/citations, grounded summaries; decide legacy alias needs | Schema-compatible tests; sources align with actual fetched evidence; no unsupported citation |
| 10 | MEDIUM | `frontend/src/app/eligibility/`, `about/`, existing Results | Add missing agreed routes by reuse, not duplicate rendering logic | Navigation, deep links, empty/filter/success state tests |
| 11 | HIGH | Both test suites, `tests/smoke.py`, live tests | Rerun complete unit/contract suite and full live Karnataka scenario; add real browser coverage | Current recorded lint/types/build/tests + DB/live/browser acceptance |
| 12 | HIGH | Compose, Dockerfiles, CI, README, source policy | Smoke-test chosen deployment, source host review and Windows instructions; gate public access | Fresh machine setup, migration/model readiness, restart/persistence and safe failure demo |
| 13 | LOW | Optional pgvector migration/new embedding service only if justified | Assess actual 16-GB laptop and retrieval quality; implement embeddings only if required | Generated/stored/queried vectors with dimension/relevance tests, otherwise explicitly deferred |

### Future PowerShell checks (instructions only; not executed)

Run from the **actual cloned root containing both backend and frontend**, not an assumed nested Windows path. Approval and private configuration are prerequisites:

```powershell
Set-Location "<actual-clone-root>"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e backend
.\.venv\Scripts\python.exe -m pytest -q backend\tests
Set-Location frontend
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

Do not run migration or the live tests against an existing Windows database until its schema/data and consent are established. README supplies backend/frontend startup commands; convert executable paths to `.venv\Scripts` on Windows, keeping the process working directory at the root for `.env` resolution. Do not stop unrelated containers or expose DSNs/keys.

# L. Final acceptance checklist

## Runtime and security

- [ ] Restore installed dependencies from existing manifests after approval; rerun current tests/builds.
- [ ] Confirm FastAPI and Next.js start on chosen ports and accept preview hosts; profile POST works through proxy.
- [ ] Configure credentials privately; verify exact CORS origin and working-directory/env behavior.
- [ ] Verify body/concurrency limits, provider shape failures, lifecycle timeouts and safe error/log behavior.
- [ ] Resolve source policy reviews/remote-fetch boundary; don't label third-party facts official.
- [ ] Review/version the intended untracked source before Git-based delivery.

## Persistence and real providers

- [ ] Inspect authorized PostgreSQL schema/connectivity; validate migrations, insert/read/upsert/rollback and restart persistence.
- [ ] Verify pgvector extension only if claimed; keep semantic retrieval marked absent until real vectors are generated/stored/queried.
- [ ] Verify live TinyFish Search response, successful Fetch and unreachable-site handling.
- [ ] Verify local Qwen actual inference/extraction on the developer laptop.
- [ ] Validate scholarship facts/rules against real quoted sources; unknown/conflicting/unrepresentable criteria remain unknown.
- [ ] Demonstrate complete discovery, committed records and deterministic matching without synthetic live responses.

## UI and demonstration

- [ ] Fix stale results after profile changes and separate research/discovery request identity.
- [ ] Reject invalid successful API payloads and recover from transient session validation failures.
- [ ] Implement or explicitly agree scope of About and separate Eligibility pages.
- [ ] Show discovered vs fetched sources, query, evidence, completeness, deadlines and correct source/application labels.
- [ ] Browser-test eligible/uncertain/ineligible display, filters, navigation and official link click-through.
- [ ] Ask Qwen a scholarship question grounded in records actually stored; inspect source citations.
- [ ] Verify responsive/keyboard/accessibility behavior and failure/empty/loading states.
- [ ] Run full real Karnataka engineering scenario with year/income/category supplied by the user; don't fabricate eligibility outcomes.
- [ ] Validate chosen Docker/local deployment, update PowerShell setup docs and explicitly state unresolved limitations.

**Audit decision:** Preserve the current implementation. The principal next step is restoring and verifying the runtime/live service contracts, followed by targeted reliability fixes—not another rewrite. Stop here and request approval before implementation.
