# Security and privacy boundaries

- Keep credentials in environment files excluded from Git. Never log the DSN,
  API key, complete profile, rejected private input, query or source content.
- Profiles are validated in memory, not persisted in PostgreSQL. Browser profile
  state is session-oriented; changing it invalidates stale discovery decisions.
- Saved research is deliberately opt-in and deployment-wide, not user-private.
  It retains queries and public evidence only. Do not put personal information in
  queries. Require access control and a retention policy before public enabling.
- Safe URL validation rejects userinfo, unsafe schemes/ports/private targets and
  unapproved official fetch domains. Local DNS checks do not pin DNS or redirects
  executed inside a remote provider; this residual SSRF boundary is documented.
- Third-party search leads cannot establish official provenance. Caller records
  cannot forge official status for matching; extraction refetches the source.
- Page text is untrusted model DATA, not instructions. Schema, verbatim evidence,
  fact/number checks and conservative coverage reduce, not eliminate, hallucinations.
- Qwen cannot downgrade extracted mandatory checks to optional. A source-domain
  flag and retrieval timestamp are not government endorsement or human validation.
- SQL uses bound parameters. Writes are transactional; immutable snapshot records
  retain extraction provenance. Never point test fixtures at a production database.
- Body (256 KiB), query/list limits, bounded page hops, shared concurrency semaphore
  and inference/workflow timeouts bound resource use. This is not distributed rate
  limiting or denial-of-service protection for an open internet deployment.
- Frontend uses same-origin proxy requests; CORS uses an explicit configured origin.
  Content is rendered as text, with HTTP(S)-only API URL guards and safe external
  link attributes. No raw model HTML is inserted.
- Error payloads omit rejected input values and exceptions. Server-generated request
  IDs and workflow IDs allow correlation without logging profile/query content.
- No authentication, user isolation, production TLS termination, operator audit
  access control, automated retention or security penetration test is claimed.
  Run behind a trusted/private boundary until these deployment controls are supplied.

See `source-policy.md` for exact approved-domain policy. Tests verify local guard
behavior, not a guarantee about a third-party service's network implementation.
