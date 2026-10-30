"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Icon, useWorkspace } from "@/components/workspace";
import { ScholarshipCard } from "@/components/results";
import { api } from "@/lib/api";
import type { Scholarship } from "@/lib/types";
export default function Dashboard() {
  const {profile, result} = useWorkspace();
  const [records, setRecords] = useState<Scholarship[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const reload = useCallback(async () => {
    setLoading(true); setError("");
    try {setRecords(await api<Scholarship[]>("scholarships"));}
    catch(e) {setError(e instanceof Error ? e.message : "Scholarship retrieval failed.");}
    finally {setLoading(false);}
  }, []);
  useEffect(() => {void Promise.resolve().then(reload);}, [reload]);
  const matches = result?.matches || [];
  return <>
    <div className="overview-heading"><div><div className="eyebrow">A CLEARER PATH TO YOUR EDUCATION</div><h1>Your next opportunity<br/>starts with the right information.</h1><p>Find scholarships that fit your journey. Understand the requirements.<br className="desktop-break"/> Make your next move with confidence.</p></div><span className="workspace-tag"><span/> STUDENT WORKSPACE</span></div>
    <section className="hero"><div className="hero-copy"><span className="hero-kicker">SCHOLARSHIP DISCOVERY, WITH CLARITY</span><h2>More possibilities.<br/><em>Less guesswork.</em></h2><p>Explore government scholarships with official sources and eligibility checks you can actually understand.</p><Link className="button light" href={profile ? "/discover" : "/profile"}>{profile ? "Discover scholarships" : "Build my student profile"}<Icon name="arrow"/></Link><div className="hero-footnote">No account needed <span>·</span> No invented eligibility</div></div><div className="radar-art" aria-hidden="true"><div className="orbit orbit-1"/><div className="orbit orbit-2"/><div className="orbit orbit-3"/><div className="radar-line"/><div className="radar-center"><svg viewBox="0 0 64 64" fill="none"><path d="m7 25 25-13 25 13-25 13L7 25Z" stroke="currentColor" strokeWidth="2"/><path d="M17 31v16c9 7 21 7 30 0V31M57 26v19" stroke="currentColor" strokeWidth="2"/></svg></div><div className="radar-caption caption-1"><span>✓</span> Source-backed discovery</div><div className="radar-caption caption-2"><span>≡</span> Explainable eligibility</div><i className="radar-dot dot-1"/><i className="radar-dot dot-2"/></div></section>
    <div className="summary-grid"><div className="summary-card"><div className="summary-icon"><Icon name="profile"/></div><div><span>Your profile</span><strong>{profile ? `${profile.state || "State not set"}` : "Let’s get to know you"}</strong><small>{profile ? `${profile.course || "Course not set"} · ${profile.education_level || "Level not set"}` : "A few details make discovery more relevant"}</small></div><Link href="/profile" aria-label="Edit student profile">↗</Link></div><div className="summary-card"><div className="summary-icon"><Icon name="discover"/></div><div><span>Latest eligibility overview</span><strong>{result ? `${matches.filter(m => m.status === "ELIGIBLE").length} eligible · ${matches.filter(m => m.status === "NEEDS_INFORMATION").length} need information` : "Your possibilities await"}</strong><small>{result ? "From your latest workflow in this session" : "Run discovery to see real matching results"}</small></div></div></div>
    <div className="dashboard-columns"><section><div className="section-title"><h2>Recently discovered</h2><Link href="/discover">Explore scholarships <span>↗</span></Link></div>{loading ? <div className="empty" role="status">Checking stored scholarships…</div> : error ? <div className="alert" role="alert"><p>{error}</p><button className="button secondary" onClick={() => void reload()}>Retry scholarship retrieval</button></div> : records.length ? records.slice(0, 3).map((s, i) => <ScholarshipCard key={i} s={s}/>) : <div className="empty dashboard-empty"><div className="empty-icon"><Icon name="discover"/></div><h3>Your scholarship shortlist starts here</h3><p>{"No scholarships have been researched yet. Add your profile, then explore official sources."}</p><Link href="/discover" className="text-link">Start your first discovery <span>→</span></Link></div>}</section><section className="how-card"><div className="eyebrow">FROM QUESTIONS TO CLARITY</div><h2>A better way to find your fit.</h2>{[["01", "Tell us about you", "Your course, state and background help focus the search."], ["02", "Explore official sources", "Research is grounded in approved government and scheme domains."], ["03", "Understand your match", "See which rules pass, fail, or need more information."]].map(([n, title, text]) => <div className="how-step" key={n}><span>{n}</span><div><h3>{title}</h3><p>{text}</p></div></div>)}<Link href="/research">See the research behind results ↗</Link></section></div>
    <div className="bottom-note"><span>ⓘ</span><p><strong>Clarity, not a guarantee.</strong> Eligibility checks reflect extracted rules. Always confirm current requirements and deadlines on the official portal.</p></div>
  </>;
}
