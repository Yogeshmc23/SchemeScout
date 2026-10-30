"use client";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ScholarshipCard } from "@/components/results";
import { Alert, PageHeading } from "@/components/workspace";
import { scholarships } from "@/lib/scholarships";
import type { ExtractionSnapshot, Scholarship } from "@/lib/types";

export default function ScholarshipDetail() {
  const params = useParams<{id: string}>();
  return <Detail key={params.id} rawId={params.id}/>;
}

function Detail({rawId}: {rawId: string}) {
  const validId = Number.isSafeInteger(Number(rawId)) && Number(rawId) > 0;
  const [record, setRecord] = useState<Scholarship | null>(null);
  const [history, setHistory] = useState<ExtractionSnapshot[]>([]);
  const [error, setError] = useState("");
  const [historyError, setHistoryError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    const id = Number(rawId);
    if (!validId) return;
    void scholarships.detail(id, controller.signal).then(setRecord).catch(e => {
      if (!controller.signal.aborted) setError(e instanceof Error ? e.message : "Could not load scholarship.");
    });
    void scholarships.history(id, controller.signal).then(setHistory).catch(e => {
      if (!controller.signal.aborted) setHistoryError(e instanceof Error ? e.message : "Could not load history.");
    });
    return () => controller.abort();
  }, [rawId, validId]);
  return <><PageHeading eyebrow="PERSISTED EVIDENCE" title="Scholarship details" description="The latest saved source extraction, with previous snapshots. Automated extraction is not human verification."/>
    {!validId ? <Alert>Invalid scholarship ID.</Alert> : error ? <Alert>{error}</Alert> : record ? <ScholarshipCard s={record}/> : <p role="status">Loading scholarship…</p>}
    <section className="panel"><h2>Extraction history</h2>{historyError && <Alert>{historyError}</Alert>}
      {!historyError && record && history.length === 0 && <p>No extraction snapshots have been recorded. Older records are not retroactively assigned fabricated history.</p>}
      {history.map(item => <details key={item.id}><summary>{new Date(item.recorded_at).toLocaleString()} · {item.scholarship.extraction_status}</summary><ScholarshipCard s={item.scholarship}/></details>)}
    </section></>;
}
