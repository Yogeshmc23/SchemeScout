# SchemeRadar — Current Development Status

**Updated:** 31 October 2026 (Asia/Calcutta)  
**Branch:** `arena/ae4fd465-schemescout`  
**Repository:** `/home/user/SchemeScout`  
**Phase:** Approved targeted implementation and local QA completed; external live acceptance blocked on service configuration.

## Overall status

The existing application was preserved and improved, not scaffolded again. The backend and production frontend run locally on **8000** and **3000**. All seven page routes and the real frontend/backend proxy were checked over HTTP. No real scholarship data was invented, no secret was requested/printed, and no database migration or remote account call was performed without the required configuration.

**Not yet accepted as a live hackathon MVP:** PostgreSQL, TinyFish and local Ollama/Qwen success cannot be verified here. Docker, psql and Ollama executables/services are unavailable, and no real service configuration is present in this sandbox. The developer's historical Windows installations/key remain outside this environment. No need to send credentials in chat.

The [audit report](SCHEMERADAR_AUDIT_REPORT.md) is a frozen pre-change snapshot. The older `docs/development-status.md` describes the previous session. **This root file is the current checklist.** Its test results below are freshly executed, not inherited from either historical document.

Status meanings: COMPLETE means the explicitly bounded feature was tested; PARTIAL means an identified gap remains; NOT STARTED means no implementation exists; UNVERIFIED means an external/runtime acceptance check cannot be established. Unit tests with doubles do not verify live providers or PostgreSQL.

## Current feature checklist

| Feature | Status | Evidence / actual verification | Remaining work |
| --- | --- | --- | --- |
| Repository/backend/frontend co-location | COMPLETE | Git root/branch inspected; no historical agent/database duplicate modules | No moves/rewrite needed |
| Dependency restoration | COMPLETE | Existing Python lockfile + editable package, npm ci; pip check and npm audit pass | No new dependency introduced |
| Git-only delivery | PARTIAL | Work preserved on fixed session branch; existing source remains working-tree/untracked | Review/version intended files before Git-based delivery; no commit/push performed |
| FastAPI startup/liveness/docs | COMPLETE | Uvicorn startup, root/docs/OpenAPI/health HTTP checks | Provider readiness is separate |
| Pydantic request/response contracts | COMPLETE | Backend validation tests, actual profile/invalid-profile HTTP tests | Additional fields must keep frontend contracts aligned |
| Six-field deterministic engine | COMPLETE | Inclusive/exclusive bounds, exact normalized values, unknowns, missing data, expired deadline and provenance tests | Disjoint/unsupported requirements must remain UNKNOWN; no alias guessing |
| Explanation rendering | COMPLETE | Decision/check/source/filter/empty-category component tests; actual API match contract | Real source/decision review still required |
| TinyFish MCP adapter | PARTIAL | Envelope, fetch-link, initialization timeout and failure tests | Actual account/protocol/response shapes remain unverified |
| TinyFish Search live | UNVERIFIED | No key configured in sandbox; explicit 503 observed through proxy | Verify in authorized configured environment |
| TinyFish Fetch live | UNVERIFIED | Fixture coverage, actual policy guards | Verify successful/inaccessible sites and provider redirect behavior |
| Qwen inference/extraction live | UNVERIFIED | No Ollama service/model here | Run real local model on developer laptop and measure latency/memory |
| Structured extraction | PARTIAL | Exact fact quotes, numeric/text rule evidence, strict bounds, malformed JSON and truncation coverage tests | Semantic completeness/conflicting source meaning cannot be proved by quote/schema checks |
| Bounded official detail-page hop | PARTIAL | Actual LangGraph tests follow max three real returned links, one hop, no recursion | Live portal/detail-page coverage unverified |
| Exact-host policy and URL safeguards | PARTIAL | Actual URL tests, private DNS fixture, provider-reported redirect rejection, bounded source URLs | Domain ownership and TinyFish remote DNS/redirect pinning remain unresolved externally |
| LangGraph routing/state | COMPLETE | CHAT/RESEARCH/DISCOVER graph execution tests with explicit doubles | Full external pipeline remains unverified |
| Query/source outcomes/citations contracts | COMPLETE | Backend result/query/outcome tests; frontend runtime contract and rendering tests | Live factual content/source relevance needs review |
| Logging/input/capacity/error behavior | COMPLETE | Body/capacity/validation tests; request IDs retained on 413/429; safe timeout/provider error handling | No authentication, per-user or distributed quotas; harden public deployment |
| PostgreSQL connection/applied schema | UNVERIFIED | SQL/pool code present, no server/DSN/client | Inspect authorized server before migration; don't reuse PG16 volume in PG17 |
| Incompatible-schema guard | COMPLETE | Unit test proves incompatible legacy column set is refused before CREATE/ALTER/DROP | Actual legacy schema migration still requires inspection/backup |
| Scholarship insertion/retrieval/upsert | UNVERIFIED | SQL parameter/transaction/read reconstruction unit tests pass | Real PostgreSQL commit/rollback/uniqueness/restart tests remain blocked |
| Discover save/reload/match wiring | COMPLETE | Graph saves then retrieves by source/name before deterministic evaluation; missing read fails safely | Real persistence integration remains unverified |
| Stored-record eligibility endpoint | UNVERIFIED | `/api/eligibility` API test uses explicit database double; real missing-DB response verified | Success needs actual PostgreSQL records |
| Deduplication | PARTIAL | Unique source URL/normalized name and upsert SQL | Live constraint test; cross-URL entity deduplication absent |
| Extraction/source metadata storage | UNVERIFIED | Actual acquisition timestamp preserved; JSONB metadata/schema exists | Inspect real stored records; failures are response metadata, not durable attempt history |
| pgvector extension deployment | UNVERIFIED | Optional migration only; never automatically claimed active | Inspect actual database extension if needed |
| Embedding generation/storage | NOT STARTED | No second model, vector column or embedding implementation | Optional; assess actual 16-GB laptop first |
| Semantic retrieval | NOT STARTED | Assistant uses bounded lexical retrieval | Explicitly defer or implement/test full vector path |
| Next.js/TypeScript/Tailwind build/start | COMPLETE | Production build, strict TS, ESLint and HTTP startup pass | Real browser visual audit separate |
| Dashboard | COMPLETE | Actual page retrieval; error vs empty state separated; real records only | Broader dashboard interaction tests optional |
| Student profile form/session | COMPLETE | Actual HTTP validation plus component/session tests; no profile stored server-side | Browser storage remains subject to user browser policy |
| Stale-profile result invalidation | COMPLETE | Real Workspace tests clear old decisions; pending discovery guard discards old-profile response | Continue regression coverage on contract changes |
| Discovery/research state separation | COMPLETE | Dedicated context state and request query in result; research no longer overwrites eligibility overview | Full successful live workflow still unverified |
| Eligibility page | COMPLETE | `/eligibility` production route/HTTP; component tests for stored recheck and decision rendering | Successful PostgreSQL-backed recheck remains external UNVERIFIED |
| About page | COMPLETE | `/about` production route/HTTP; source/privacy/limitations documentation | No fabricated marketing metrics |
| Assistant UI | PARTIAL | Actual request contract/component tests and structured source links; relevance filters | Live Qwen grounded answer unverified; history is page-only, not backend memory |
| Research interface | PARTIAL | Query, separate discovered sources/page outcomes, extraction evidence and factual source excerpts | Live results and substantive user review remain unverified |
| API runtime validation/cancellation | COMPLETE | Invalid 2xx JSON/shapes/URLs rejected; network/timeout/cancel tests; actual HTTP frontend guards | Maintain manual contracts as schema evolves |
| Navigation/loading/error/empty states | COMPLETE | Seven routes return 200; component tests for states, filters, retry and links | Real browser/assistive technology testing remains separate |
| Responsive/accessibility quality | UNVERIFIED | Breakpoints, reduced-motion, labels and live regions exist | No real browser/mobile/screen-reader run |
| Local frontend/backend HTTP integration | COMPLETE | Three actual proxy tests, profile validation/matching and seven-route smoke pass | These do not substitute for live scholarship discovery |
| Legacy unprefixed route aliases | NOT STARTED | Current clients correctly use `/api/...` | No unknown historical schema aliases added; agree compatibility only if needed |
| Docker deployment/remote CI | UNVERIFIED | Existing Dockerfiles/Compose/CI retained | Docker unavailable; remote workflow not run |
| README/PowerShell setup | PARTIAL | Updated paths, additive contracts, test/start commands and PG16/17 safety note | Windows execution and external deployment not verified here |
| Complete hackathon live scenario | UNVERIFIED | No synthetic live results substituted | Complete external acceptance checklist below |

## Fresh test ledger

| Command/check | Actual result |
| --- | --- |
| Baseline backend suite after restoration | 84 passed, 2 external tests skipped |
| Baseline frontend suite | 9 passed |
| Final `pytest -q backend/tests` | **125 passed, 2 skipped** |
| `ruff check backend` | Passed |
| `pip check` | Passed; no broken requirements |
| Frontend with `SCHEMERADAR_SMOKE_URL=http://127.0.0.1:3000 npm test` | **31 passed**, including three real HTTP tests |
| Ordinary frontend `npm test` without running-server opt-in | 28 local tests; three HTTP tests intentionally gated (run with variable above) |
| `npm run typecheck` | Passed |
| `npm run lint` | Passed |
| `npm run build` | Passed; seven application routes plus standard not-found output |
| `npm audit` | Zero vulnerabilities, including development dependencies |
| Production frontend and backend startup | Passed, bound to 0.0.0.0 on 3000 / 8000 |
| `tests/smoke.py` | All seven pages, health/profile/invalid-profile and actual OpenAPI checks passed |
| Preview-style Host on 3000 and 8000 | HTTP 200 (backend root redirects to docs) |
| Missing-service actual HTTP | Search, stored eligibility and discovery return explicit 503s |
| Database live test | Skipped: no dedicated TEST_DATABASE_URL/server; test would write fixtures |
| Live Karnataka discovery test | Skipped: no live key/Ollama/PostgreSQL configuration; would store actual discovered records |
| Real-browser / Docker / live provider success | Not executed; cannot be claimed verified |

Frontend tests that failed during contract/context integration were fixed by updating test inputs to the actual complete schemas and context API, not by removing assertions or disabling type checking. All new synthetic fixtures are in test-only modules and are never imported by application pages/services. No dependency additions were needed.

## Phase journal and exact changed paths

### Phase 1 — Restore and stabilize

Restored `.venv` from `backend/requirements.lock`, installed current package editable without dependency changes, and restored `frontend/node_modules` with `npm ci`. All generated dependencies/build outputs remain ignored. Confirmed existing baseline and preserved all preexisting implementation.

### Phases 2–6 — Backend, contracts, persistence wiring and eligibility

Changed:

- `backend/app/models.py`: exclusive bound flags/defaults, strict numeric/empty rule validation, Page links/acquisition/truncation metadata, query/per-source outcomes.
- `backend/app/eligibility.py`: inclusive/exclusive deterministic boundaries and explicit operator explanations.
- `backend/app/providers.py`: whole MCP lifecycle budget, safe envelope types/statuses, public approved actual links, fact/rule value/number evidence checks, invalid Ollama output/timeouts, real fetch timestamp and truncated-source uncertainty.
- `backend/app/workflow.py`: bounded detail_fetch/detail_extract nodes, per-page outcomes/query, read-after-write matching, source-bearing/relevance-filtered chat, shared whole-workflow preflight budget.
- `backend/app/db.py`: refuse incompatible existing flat table before DDL; identity-based parameterized read for committed-record reload.
- `backend/app/main.py`: stored `/api/eligibility` endpoint; request correlation on early limits/errors.
- `backend/tests/test_api.py`, `test_eligibility.py`, `test_providers.py`, `test_workflow.py`: new regressions; existing graph doubles updated to implement actual repository readback.
- New `backend/tests/test_database_unit.py`: explicitly double-backed transaction/SQL/legacy-schema/read tests.
- `backend/tests/test_database_live.py`: expanded real read-after-write assertion, still unexecuted externally.

Database changes are code-only: no new table migration, existing database mutation, PG version change, model install or provider account call was performed. Existing JSON records receive false defaults for new exclusive flags when read. Unit SQL tests are not PostgreSQL acceptance evidence.

### Phases 7–8 — Frontend integration

Changed:

- `frontend/src/lib/types.ts`, `api.ts`: current backend types, runtime response validation, safe typed errors and cancellation.
- New `frontend/src/lib/contracts.ts`: runtime guards for profile/scholarship/match/agent/source contracts.
- `frontend/src/components/workspace.tsx`: invalidation, separate research state, preservation/retry of transient session failures, late-restoration guard, navigation.
- `frontend/src/components/research-form.tsx`: request cancellation, old-profile response discard, mode-specific results.
- `frontend/src/components/results.tsx`: query, page outcomes, correct source labels, accessible filters and explicit empty category.
- `frontend/src/app/page.tsx`: distinguish retrieval failure from empty records and offer functional retry.
- `frontend/src/app/assistant/page.tsx`: structured evidence links beside model text.
- New `frontend/src/app/eligibility/page.tsx` and `about/page.tsx`: stored-rule recheck and transparent product/privacy/limitations page.
- `frontend/src/app/globals.css`: outcome/citation/about styling and bounded sidebar scrolling.
- Existing `forms.test.tsx`, `api.test.ts` updated/expanded; new `workspace.test.tsx`, `results.test.tsx`, `contracts.test.ts`, `http.integration.test.ts` and test-only `src/test/fixtures.ts`.

### Phases 9–10 — QA, documentation and runnable preview

- `tests/smoke.py` now checks seven routes and current OpenAPI, supports an opt-in base URL.
- `README.md` documents new contracts/features, truthful live-service limitations, Windows PowerShell commands, real HTTP test opt-in, and safe handling of existing Windows PG16 versus Compose PG17.
- `docs/source-policy.md` records the bounded detail-hop behavior without silently approving new domains.
- `.env.example` documents the test-only smoke variable by name, without secrets.
- This status document supersedes its earlier audit-only state; frozen audit and historical handoff were not rewritten.
- Both application servers are left running as live previews. No commit, push or unrelated container operation was performed.

## Remaining blockers and limitations

1. Configure existing authorized services privately in an environment that can reach TinyFish/model registries. This sandbox cannot inspect Windows environment files/services or use their credentials automatically.
2. Inspect/backup the actual Windows PostgreSQL schema before running migrations. Do not mount PG16 data directly into PG17. The new guard refuses incompatible columns rather than attempting a destructive automatic conversion.
3. Verify real MCP response envelopes, fetch success/failure, Qwen inference and extraction accuracy, DB persistence/retrieval/duplicates/rollback, then full discover flow.
4. Quote/number membership checks cannot prove rule meaning or completeness. Unsupported conditions, conflicts/disjoint ranges and broader eligibility dimensions need source review; never infer aliases or claim official award confirmation.
5. One extra detail hop uses actual links only, with a six-page total cap. No general recursive crawler or multiple-scheme extraction from one directory page is claimed.
6. Remote TinyFish DNS/redirect behavior cannot be pinned by local URL checks. Source host shortlist ownership/canonical redirects need external review.
7. No authentication, per-user/distributed quotas, background job recovery, durable extraction-failure history, refresh scheduling, cross-URL deduplication or multi-turn backend chat memory.
8. Optional vector functionality remains absent beyond extension SQL; do not add another model without actual laptop measurements.
9. Real-browser/mobile/accessibility, Docker deployment and remote CI checks remain outstanding.
10. Work remains saved in the branch workspace; Git-based delivery still needs deliberate review/versioning. No unrelated files were discarded and no credential was added to source.

## Hackathon acceptance gates

- [x] Existing backend/frontend install, start and communicate through current proxy.
- [x] Student profile validation and deterministic matching verified locally with explicit test inputs.
- [x] Stale-profile decisions, transient storage recovery and malformed API/provider responses regression-tested.
- [x] Seven page routes compile/serve; result explanations, filters/outcomes and grounding links component-tested.
- [x] Current Python/TypeScript/lint/build/local HTTP tests pass without disabling checks.
- [ ] Actual PostgreSQL connection/schema, inserts/reads/uniqueness/rollback/restart persistence verified.
- [ ] Actual TinyFish Search and Fetch, including one inaccessible source alongside successful sources.
- [ ] Actual Qwen extraction and source-reviewed eligibility requirements.
- [ ] Complete real Karnataka engineering discovery → validated store → retrieved match → UI results.
- [ ] Official links opened and assistant answer grounded in those actual stored records.
- [ ] Real browser/mobile/accessibility and intended deployment smoke test.
- [ ] Optional vector search explicitly deferred for MVP or fully generated/stored/queried/tested.
- [ ] Intended Git delivery reviewed; Windows/service setup and remaining limitations confirmed.

**Resume point:** Provision/verify the real configured services and run the existing dedicated database/live tests, then the README demonstration. Do not start a replacement scaffold or substitute demo scholarships for live results.

## Architecture expansion — phase 1 assessment and phase 2 module boundaries (2026-10-31)

**Assessment COMPLETE; backend modularization PARTIAL.** Baseline before changes: `pytest -q backend/tests` 125 passed, 2 skipped; Ruff and `pip check` passed. Existing contracts, bounded LangGraph and transactional JSONB repository are retained rather than replaced with empty scaffolding.

Implemented files: `backend/app/api/{dependencies.py,routes/operations.py}`, `backend/app/services/{runtime.py,ollama.py}`, `backend/app/tools/tinyfish.py`; modified bootstrap/workflow/provider/API tests. Removed the former combined `providers.py` after migrating all imports and monkeypatch targets. Services are application-scoped and obtained through FastAPI dependency injection. Legacy `/api` and new `/api/v1` share handlers, including `discover-and-match`; both use the same concurrency limit. Endpoint logic is no longer in bootstrap.

Actual verification after these changes: backend **125 passed, 2 skipped**; Ruff passed. Live services remain UNVERIFIED. Remaining: expanded criterion contracts/tests, durable extraction history/detail access, frontend consumers, explicit graph stages/diagnostics, architecture docs and integration validation. No semantic retrieval or real student acceptance is claimed.

## Architecture phase 3 — contracts and eligibility

**COMPLETE (implemented scope), live acceptance UNVERIFIED.** Modified `models.py`, `eligibility.py`, `api/errors.py`, bootstrap/router and frontend types/guards. Additive criterion `mandatory` defaults true for old data; explanations include student value and structured requirement. Failed mandatory checks outrank unknown mandatory checks; optional failures/unknowns cannot disqualify. Model extraction rejects optional downgrades rather than silently trusting an LLM's classification. Errors retain legacy `detail` and add code/message/request ID. New API/versioning/optional-rule tests executed: **130 passed, 2 skipped** at this phase; Ruff passed. Normalization remains explicit exact case/whitespace normalization, not inferred equivalences.

## Architecture phase 4 — database persistence

**IMPLEMENTED; actual PostgreSQL execution UNVERIFIED.** Added `migrations/003_extraction_history.sql`; modified `db.py`, models, routes and database/API tests. Stable existing bigint IDs and updated timestamps are projected from SQL rather than accepted from extraction. Each save atomically updates the latest scholarship/source and appends an extraction snapshot. Positive-ID detail/history endpoints provide bounded reads and honest 404s. Optional research history has separate constrained storage; only RESEARCH without matches may be retained. Default disabled; no profiles are added to storage. Existing rows are preserved, not assigned invented past extractions. Packaged migration runner applies 001+003 under the existing advisory lock/transaction; optional extension 002 is still not automatic.

SQL/lifecycle doubles and API tests passed, but are NOT migration/transaction proof. No PostgreSQL or Docker executable is available in this workspace; the opt-in real database test is updated to assert stable IDs and two snapshots and remains skipped. Existing Windows data, resources and volumes were not touched.

## Architecture phases 5–7 — providers, orchestration and deterministic matching

**IMPLEMENTED; live provider integration UNVERIFIED.** TinyFish and Qwen retain the existing source/evidence guards and bounded transport. Added `services/research.py` to own opt-in retention policy; a history save outage produces an explicit warning without falsely claiming a history ID or discarding already valid results. `workflow.py` remains the single LangGraph: explicit validate/classify, acquisition/extraction, pre-store validation, store, retrieve, deterministic match and summary, with separate chat path. Store/retrieve are now distinct stages. Added bounded per-stage timings/status and opaque workflow IDs; logs contain no queries/profiles/source URLs/content. Latest backend run after these additions: **137 passed, 2 skipped**, Ruff passed. Embeddings/semantic retrieval NOT STARTED and deliberately not represented as complete; existing lexical evidence selection is retained. No Redis added without a concrete need.

## Architecture phase 8 — frontend

**IMPLEMENTED; final checks in progress.** Added typed `lib/scholarships.ts`, scholarship detail route, extraction snapshot display and explicit opt-in saved-research loading. Modified result cards/rule labels, Research page, transport (now `/api/v1`), types and runtime contracts. Existing dashboard/profile/discovery/eligibility/assistant/about remain in place. Real loading/error/empty states replace any assumption of available storage/history. New detail/history contract and history component tests added. First frontend run before these last tests: typecheck/lint passed; **28 passed, 3 optional HTTP tests skipped**. A lint violation in the initial detail effect was fixed with keyed route state (no rule disabled). A missing test import caught by typecheck is corrected; final re-run pending below.

Remaining: final frontend/backend/proxy validation, six architecture docs, review of diffs and operational limitations. Full service-backed student journey remains UNVERIFIED, not complete.

## Architecture phases 9–10 — integration, documentation and final validation

**Local implementation/validation COMPLETE; live acceptance PARTIAL / UNVERIFIED.** Added all six required references: `docs/{architecture,database-design,api-design,agent-workflow,security,deployment}.md`. They describe the actual module map, API contracts, SQL schema, graph/dataflow diagrams, privacy boundaries, exact POSIX/PowerShell startup and remaining acceptance gates. Updated README/module tree, `.env.example`, and Compose's opt-in history environment forwarding. Existing database images/volumes and unrelated services were not altered.

Final executed results (2026-10-31):

| Check | Actual result |
| --- | --- |
| `.venv/bin/pytest -q backend/tests` | **141 passed, 2 skipped** |
| `.venv/bin/ruff check backend` | **passed** |
| `.venv/bin/pip check` | **No broken requirements found** |
| `npm --prefix frontend run typecheck` | **passed** |
| `npm --prefix frontend run lint` | **passed** |
| `SCHEMERADAR_SMOKE_URL=http://127.0.0.1:3000 npm --prefix frontend test` | **36 passed**, including 3 actual Next → FastAPI HTTP tests |
| `npm run build` in frontend | **passed**, seven existing pages plus dynamic scholarship detail route |
| `.venv/bin/python tests/smoke.py` | **passed** seven pages, health proxy, real profile validation, invalid rejection and OpenAPI; DB listing honestly **503** |
| Additional actual HTTP | detail page shell **200**; v1 health **200**; disabled research history **503**; nonpositive scholarship ID **422**; versioned detail/history OpenAPI confirmed |
| `git diff --check` | **passed** |

New regressions cover backward-compatible versioning/shared capacity, safe error envelopes, optional/mandatory precedence, structured check values, positive-ID details and missing records, history bounds/privacy defaults, parameterized query retention and discovery rejection, retained results on history outage, explicit graph-stage metadata, frontend history loading/errors, detail/history independent failure, and runtime detail/history guards. SQL/provider/graph test doubles are isolated fixtures, not live integration proof.

The actual current source was loaded into Uvicorn on **0.0.0.0:8000**; the latest production Next build serves on **0.0.0.0:3000**. Only this app's previously inspected API/Next processes were restarted. Preview page success is not proof of populated scholarship data.

### Remaining gates / limitations

- **UNVERIFIED:** actual PostgreSQL 001+003 execution, upsert/snapshot/rollback/restart behavior and compatibility with the user's existing database. Dedicated live DB test was updated, not run.
- **UNVERIFIED:** real TinyFish Search/Fetch, Qwen extraction, official-source manual review and a complete real-profile discovery → persisted readback → eligibility → details/assistant browser journey. Missing service configuration was not replaced with fake data.
- **UNVERIFIED:** Docker build/start, intended Windows deployment, real browser/mobile/accessibility E2E and remote CI.
- **NOT STARTED / intentionally deferred:** embeddings/semantic retrieval. Optional pgvector extension alone is not counted as functionality; eligibility never uses similarity.
- Optional-rule semantics require reviewed structured data; automatic model downgrades are intentionally rejected. JSONB structured rules are retained instead of an unnecessary relational rewrite.
- Research history is opt-in, deployment-wide, not user-private; authentication/isolation/automatic retention are not implemented. Do not publicly expose it without controls. No personal profiles or DISCOVER match results are persisted.
- Existing conservative extraction/evidence and remote-provider DNS/redirect limitations still apply. History lists are bounded, but operators must establish retention limits for stored snapshots/queries.

**Overall:** substantial connected architecture expansion implemented and locally tested, not a claim of complete service-backed student acceptance. No additional Git commit/push was made in this expansion; changes are saved on the fixed session branch and are not yet included in the already-open PR's remote diff.

Final packaging follow-up: an optional `pip wheel --no-build-isolation` attempt failed because this venv lacks `bdist_wheel` and has an older build backend; no application check was disabled. Retried with the project's declared isolated build requirements using `.venv/bin/pip wheel --no-deps --wheel-dir backend/dist ./backend`: **passed**. Inspected the resulting wheel to confirm the new API/service/tool packages and migration 003 are packaged and removed `providers.py` is absent. Wheel/build outputs remain ignored. API detail IDs are additionally bounded to PostgreSQL bigint range; backend tests still **141 passed, 2 skipped**, Ruff/diff checks passed afterward. Latest source API was restarted on port 8000; latest production frontend remains on 3000.
