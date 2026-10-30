"use client";
import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { Alert, PageHeading, useWorkspace } from "@/components/workspace";
import { Results } from "@/components/results";
import { api } from "@/lib/api";
import type { AgentResult, Match } from "@/lib/types";

export default function EligibilityPage() {
  const {profile, result, isCurrentProfile} = useWorkspace();
  const [evaluation, setEvaluation] = useState<{profileKey: string; data: AgentResult} | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const activeRequest = useRef<AbortController | null>(null);
  useEffect(() => () => activeRequest.current?.abort(), []);
  const key = JSON.stringify(profile);
  const visible = evaluation?.profileKey === key ? evaluation.data : result;
  async function recheck(e: FormEvent) {
    e.preventDefault(); if (!profile) return;
    const submittedProfile = profile;
    const controller = new AbortController(); activeRequest.current = controller;
    setBusy(true); setError(""); setEvaluation(null);
    try {
      const matches = await api<Match[]>("eligibility", profile, controller.signal);
      if (!isCurrentProfile(submittedProfile)) {
        setError("Your profile changed during matching. Recheck with your current details."); return;
      }
      setEvaluation({profileKey: JSON.stringify(submittedProfile), data: {
        mode: "ELIGIBILITY", query: "Stored scholarships compared with the current student profile",
        summary: "These decisions use records retrieved from PostgreSQL. No web search or AI eligibility decision was made. Always confirm current source requirements.",
        scholarships: matches.map(m => m.scholarship), matches, sources: [], source_outcomes: [],
        errors: [], steps: ["Retrieved stored records", "Compared explicit rules deterministically"], stored_count: 0,
      }});
    } catch(e) {if (!controller.signal.aborted) setError(e instanceof Error ? e.message : "Could not load stored scholarship eligibility.");}
    finally {setBusy(false);}
  }
  return <><PageHeading eyebrow="UNDERSTAND YOUR FIT" title="Every decision, explained." description="Review your latest discovery or recheck scholarships already stored in the database. Unknown requirements never count as passed."/>
    <form className="panel" onSubmit={recheck}><h2>Use your current profile</h2><p className="muted">{profile ? `${profile.state || "State unknown"} · ${profile.course || "Course unknown"}` : <>First <Link href="/profile">save a student profile</Link>.</>}</p><div className="form-actions"><button className="button" disabled={busy || !profile}>{busy ? "Checking stored rules…" : "Recheck stored scholarships"}</button><Link className="button secondary" href="/discover">Discover new scholarships</Link></div></form>
    {busy && <p className="loading-panel" role="status">Retrieving stored scholarships and evaluating their rules…</p>}{error && <Alert>{error}</Alert>}
    {!busy && visible ? <Results result={visible}/> : !busy && !error && <div className="empty"><h3>No eligibility results yet</h3><p>Run discovery or recheck stored scholarships with your current profile.</p></div>}
  </>;
}
