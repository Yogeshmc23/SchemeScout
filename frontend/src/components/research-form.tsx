"use client";
import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { api } from "@/lib/api";
import type { AgentResult } from "@/lib/types";
import { Alert, PageHeading, useWorkspace } from "./workspace";
import { Results } from "./results";
export function ResearchForm({mode}: {mode: "DISCOVER" | "RESEARCH"}) {
  const {profile, result: discoveryResult, setResult: setDiscoveryResult, researchResult, setResearchResult, isCurrentProfile} = useWorkspace();
  const result = mode === "DISCOVER" ? discoveryResult : researchResult;
  const setResult = mode === "DISCOVER" ? setDiscoveryResult : setResearchResult;
  const activeRequest = useRef<AbortController | null>(null);
  useEffect(() => () => activeRequest.current?.abort(), []);
  const [query, setQuery] = useState(""); const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  async function submit(e: FormEvent) {
    e.preventDefault(); setError(""); setBusy(true); setResult(null);
    const controller = new AbortController(); activeRequest.current = controller;
    const submittedProfile = profile;
    try {
      const response = await api<AgentResult>(mode === "DISCOVER" ? "discover" : "research", mode === "DISCOVER" ? {mode, query, profile} : {query}, controller.signal);
      if (mode === "DISCOVER" && !isCurrentProfile(submittedProfile)) {
        setError("Your profile changed during discovery. Old eligibility results were discarded; run discovery again or recheck stored scholarships.");
      } else { setResult(response); }
    }
    catch(e) {if (!controller.signal.aborted) setError(e instanceof Error ? e.message : "Research failed.");} finally {setBusy(false);}
  }
  return <><PageHeading eyebrow={mode === "DISCOVER" ? "FIND YOUR NEXT OPPORTUNITY" : "FOLLOW THE EVIDENCE"} title={mode === "DISCOVER" ? "Discover a better fit." : "The research desk."} description={mode === "DISCOVER" ? "Search official sources and see how explicit scholarship rules compare with your profile." : "Trace scholarship information back to its source. Inspect evidence, missing details and extraction status."}/><form onSubmit={submit} className="panel search-panel"><label htmlFor="query">What would you like to explore?</label><div className="search-row"><input id="query" disabled={busy} value={query} onChange={e => setQuery(e.target.value)} minLength={3} maxLength={500} required placeholder="e.g. Karnataka engineering scholarships"/><button className="button" disabled={busy || (mode === "DISCOVER" && !profile)}>{busy ? "Researching…" : mode === "DISCOVER" ? "Discover scholarships →" : "Research sources →"}</button></div>{mode === "DISCOVER" && <p className="muted">{profile ? `Using your profile: ${profile.state || "State unknown"} · ${profile.course || "Course unknown"}` : <>First <Link href="/profile">save your student profile</Link> to enable matching.</>}</p>}<p className="muted">Up to 3 search pages and 3 linked detail pages per workflow. Live research can take several minutes.</p></form>{busy && <div className="loading-panel" role="status"><span className="spinner"/><div><strong>Following the evidence…</strong><p>Searching, fetching and validating sources. Results appear when the workflow finishes; no simulated progress is shown.</p></div></div>}{error && <Alert>{error}</Alert>}{result && !busy ? <Results result={result}/> : !busy && !error && <div className="empty"><h3>Real sources. Transparent results.</h3><p>Your results will appear here after research. Unknown requirements stay unknown.</p></div>}</>;
}
