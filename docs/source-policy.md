# Official-source and URL policy

Policy version: 2026-10-31 (bounded detail-hop documentation update; no new host approvals). Maintained in `backend/app/security.py:OFFICIAL_HOSTS`.

The policy approves exact hosts, NOT any URL containing `gov`, `nic`, or a provider name.
Subdomains are not implicitly approved. This initial shortlist is based on known agency/portal
identities; live availability/ownership checks were not possible in the development sandbox.
Recheck each host against the responsible agency before a public demonstration.

| Exact hosts | Intended operator |
| --- | --- |
| scholarships.gov.in, scholarship.gov.in | National Scholarship Portal candidates; verify current canonical hostname |
| ssp.karnataka.gov.in, ssp.postmatric.karnataka.gov.in | Karnataka State Scholarship Portal |
| aicte-india.org, www.aicte-india.org | All India Council for Technical Education |
| socialjustice.gov.in | Ministry of Social Justice and Empowerment |
| tribal.nic.in | Ministry of Tribal Affairs |
| minorityaffairs.gov.in | Ministry of Minority Affairs |

Approval means a domain is permitted as a source. It does NOT mean every page is a valid scholarship,
that its content is current, or that automated extraction is human verified.

## Fetch safeguards

- HTTP/HTTPS only; reject credentials, unusual ports, IP literals, local names and malformed URLs.
- Fetch only exact approved domains; DNS must resolve exclusively to globally routable addresses.
- Maximum three URLs per fetch request; a workflow checks at most three initial pages and three additional linked detail pages. The extra hop uses actual provider-returned links, never LLM-invented URLs, and does not recurse.
- Require nonempty provider-returned page text and an exact matching requested URL.
- Reject reported redirect targets that differ from the requested canonical URL.
- Search may show third parties, but they cannot establish confirmed scholarship facts.
- Extraction endpoints refetch from TinyFish; client-supplied content cannot acquire official provenance.
- Source text is untrusted data, never a tool instruction. React renders text, not raw HTML.

**Residual limitation:** fetching occurs in TinyFish's remote infrastructure, not our local HTTP client.
Local DNS checks cannot pin TinyFish's DNS resolution or prevent a redirect the provider does not
report. Enforce remote redirect/egress restrictions with the provider before broadening this policy.
We intentionally do not offer unrestricted public URL fetching.

## Maintaining the shortlist

Verify the agency's ownership through an independent official directory, inspect canonical URLs and
redirect behavior, record the review in this document, then add exact hosts and policy tests. Do not
approve a host because an LLM proposed it. Broader India-wide source coverage requires ongoing review.
