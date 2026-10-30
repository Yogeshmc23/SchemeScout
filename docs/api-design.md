# API contracts

Preferred prefix: `/api/v1`. Legacy `/api` uses the very same router and models,
not a duplicate implementation. The Next.js transport uses `/api/v1`; browser code
never uses backend localhost. OpenAPI: `/api/openapi.json`; UI: `/api/docs`.

| Method | Relative path | Contract / behavior |
| --- | --- | --- |
| GET | `/health` | Process liveness only |
| GET | `/ready` | Database probe, key-presence indication; not a model/provider live test |
| POST | `/profile` | Validate/return six nullable fields; no server retention |
| POST | `/search` | Query → TinyFish source leads; third-party is unconfirmed |
| POST | `/fetch` | 1–3 approved URLs → pages and independent errors |
| POST | `/extract` | URL → refetch then evidence-validated Scholarship; no caller content trusted |
| POST | `/match` | Profile + up to 30 records → deterministic checks; caller cannot assert official provenance |
| POST | `/eligibility` | Profile → match persisted records |
| POST | `/agent` | Explicit CHAT / RESEARCH / DISCOVER request |
| POST | `/chat` | Query → stored-evidence assistant; never decides eligibility |
| POST | `/research` | Query → bounded discovery/extraction/save/readback |
| POST | `/discover` or `/discover-and-match` | DISCOVER request with required profile |
| GET | `/scholarships` | Latest 30 persisted records with stable SQL-owned IDs |
| GET | `/scholarships/{positive_id}` | Latest record or 404 |
| GET | `/scholarships/{positive_id}/history?limit=20` | Extraction snapshots, max 50; unknown parent is 404 |
| GET | `/research/history?limit=10` | Opt-in research summaries, max 20; disabled → 503 |
| GET | `/research/history/{uuid}` | Saved RESEARCH AgentResult or 404; disabled → 503 |

Schema authority is `backend/app/models.py`; generated OpenAPI is the full field
reference. Frontend interfaces and runtime guards accept additive server fields
while validating the fields each UI consumes. Unknown data is not filled with
sample scholarships. Requests reject unknown fields and enforce string/list/body
limits. Match checks include outcome, reason, evidence, mandatory flag, student
value and full structured requirement. Optional checks never disqualify.

## Errors and compatibility

All application errors retain `detail` (string or safe validation issues), adding:

```json
{"detail":"Scholarship not found.","error":{"code":"NOT_FOUND","message":"Scholarship not found.","request_id":"opaque-server-generated-id"}}
```

The same opaque ID is in `X-Request-ID`. Rejected input values are omitted.
413 bounds body size to 256 KiB; 422 is validation; 429 is shared workflow capacity;
502 provider/grounding failure; 503 unavailable persistence/configuration; 504 timeout.
Unhandled 500s are generic and never expose exception values. HTTP-level framework
errors also use the envelope. No authentication or per-user history isolation is
claimed; deployment-wide history must not be publicly exposed without access control.
