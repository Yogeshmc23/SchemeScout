"use client";
import { useEffect, useRef, useState } from "react";
import { researchHistory } from "@/lib/scholarships";
import type { AgentResult, ResearchRun } from "@/lib/types";
import { Alert } from "./workspace";
import { Results } from "./results";

export function ResearchHistory() {
  const [runs, setRuns] = useState<ResearchRun[] | null>(null);
  const [result, setResult] = useState<AgentResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const active = useRef<AbortController | null>(null);
  useEffect(() => () => active.current?.abort(), []);
  async function load(id?: string) {
    active.current?.abort(); const controller = new AbortController(); active.current = controller;
    setBusy(true); setError(""); setResult(null);
    try { if (id) setResult(await researchHistory.detail(id, controller.signal)); else setRuns(await researchHistory.list(controller.signal)); }
    catch (e) { if (!controller.signal.aborted) setError(e instanceof Error ? e.message : "History request failed."); }
    finally { if (!controller.signal.aborted) setBusy(false); }
  }
  return <section className="panel"><h2>Saved research</h2><p>Optional deployment-wide history, not a private account. Disabled by default. Do not include personal information in research queries.</p>
    <button className="button" disabled={busy} onClick={() => void load()}>Load saved research</button>
    {busy && <p role="status">Loading saved research…</p>}{error && <Alert>{error}</Alert>}
    {runs?.length === 0 && <p>No research runs have been saved.</p>}
    {runs && <ul>{runs.map(run => <li key={run.id}><button disabled={busy} onClick={() => void load(run.id)}>{run.query}</button> · {new Date(run.created_at).toLocaleString()} · {run.scholarship_count} records</li>)}</ul>}
    {result && <Results result={result}/>}</section>;
}
