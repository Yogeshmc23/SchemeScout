"use client";
import { useState, type FormEvent } from "react";
import { Alert, PageHeading } from "@/components/workspace";
import { api } from "@/lib/api";
import type { AgentResult, Source } from "@/lib/types";
export default function AssistantPage() {
  const [messages, setMessages] = useState<{role: string; text: string; sources?: Source[]}[]>([]);
  const [input, setInput] = useState(""); const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  async function submit(e: FormEvent) {
    e.preventDefault(); const query = input.trim(); if (!query) return;
    setMessages(m => [...m, {role: "You", text: query}]); setInput(""); setError(""); setBusy(true);
    try {const r = await api<AgentResult>("chat", {query}); setMessages(m => [...m, {role: "SchemeRadar", text: r.summary, sources: r.sources}]);}
    catch(e) {setError(e instanceof Error ? e.message : "Assistant unavailable."); setInput(query);} finally {setBusy(false);}
  }
  return <><PageHeading eyebrow="ASK WITH CONFIDENCE" title="A little clarity goes a long way." description="Ask about researched scholarships. Answers use stored source evidence; eligibility decisions belong to the rule engine."/><section className="panel chat"><div className="chat-heading"><span className="chat-dot"/><strong>Scholarship assistant</strong><span>Qwen2.5 · Local reasoning</span></div><div className="messages" aria-live="polite">{messages.length === 0 && <div className="empty"><h3>What would you like to understand?</h3><p>Research a scholarship first, then ask about benefits, documents or application steps.</p><p className="muted">Example: “Which documents are required for the scholarships you found?”</p></div>}{messages.map((m, i) => <article key={i} className={`message ${m.role === "You" ? "user" : "ai"}`}><strong>{m.role}</strong><p>{m.text}</p>{m.sources && m.sources.length > 0 && <div className="citation-links" aria-label="Answer evidence">{m.sources.map((s, j) => <a key={j} href={s.url} target="_blank" rel="noopener noreferrer">{s.title} ↗</a>)}</div>}</article>)}{busy && <p role="status">Reading stored evidence…</p>}</div>{error && <Alert>{error}</Alert>}<form onSubmit={submit} className="chat-input"><label className="sr-only" htmlFor="message">Your scholarship question</label><input id="message" value={input} onChange={e => setInput(e.target.value)} placeholder="Ask a scholarship question…" minLength={3} maxLength={500} required/><button className="button" disabled={busy}>Send ↑</button></form><p className="chat-disclaimer">Each question retrieves evidence independently. History stays on this page and is not sent to the server. AI answers may be wrong; confirm facts at the official source.</p></section></>;
}
