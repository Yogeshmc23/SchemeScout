"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { createContext, useContext, useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import { api, ApiError } from "@/lib/api";
import type { AgentResult, Profile } from "@/lib/types";

interface Store {
  profile: Profile | null; setProfile: (p: Profile | null) => void;
  result: AgentResult | null; setResult: (r: AgentResult | null) => void;
  researchResult: AgentResult | null; setResearchResult: (r: AgentResult | null) => void;
  isCurrentProfile: (p: Profile | null) => boolean;
}
const Context = createContext<Store | null>(null);
export function useWorkspace() { const s = useContext(Context); if (!s) throw new Error("Missing workspace"); return s; }
export function Icon({name}: {name: string}) {
  const paths: Record<string, ReactNode> = {
    dashboard: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    discover: <><circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/></>,
    profile: <><circle cx="12" cy="8" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/></>,
    research: <><path d="M4 3h12l4 4v14H4zM15 3v5h5M8 12h8M8 16h6"/></>,
    assistant: <><path d="M21 4H3v14h5l4 4v-4h9zM7 9h10M7 13h6"/></>,
    arrow: <path d="M4 12h16m-6-6 6 6-6 6"/>,
  };
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] || paths.discover}</svg>;
}
const links = [["/", "dashboard", "Overview"], ["/profile", "profile", "Student profile"], ["/discover", "discover", "Discover scholarships"], ["/eligibility", "research", "Eligibility results"], ["/research", "research", "Research desk"], ["/assistant", "assistant", "AI assistant"], ["/about", "research", "About SchemeRadar"]];
export function Workspace({children}: {children: ReactNode}) {
  const [profile, setProfile] = useState<Profile | null>(null);
  const currentProfile = useRef<Profile | null>(null);
  const [result, setResult] = useState<AgentResult | null>(null);
  const [researchResult, setResearchResult] = useState<AgentResult | null>(null);
  const [sessionError, setSessionError] = useState("");
  const path = usePathname();
  const restore = useCallback(async () => {
    try {
      const raw = sessionStorage.getItem("schemeradar-profile");
      if (!raw) return;
      let parsed: unknown;
      try { parsed = JSON.parse(raw); }
      catch { sessionStorage.removeItem("schemeradar-profile"); setSessionError("The saved profile was unreadable. Please enter it again."); return; }
      const restored = await api<Profile>("profile", parsed);
      // Do not let a late restoration overwrite a newly saved profile.
      if (sessionStorage.getItem("schemeradar-profile") === raw && currentProfile.current === null) {
        currentProfile.current = restored;
        setProfile(restored);
      }
      setSessionError("");
    } catch (e) {
      if (e instanceof ApiError && e.status === 422) {
        sessionStorage.removeItem("schemeradar-profile");
        setSessionError("The saved profile is invalid. Please update your student details.");
      } else {
        // Keep the saved data when the service/network is temporarily unavailable.
        setSessionError("Your saved profile could not be validated. It has not been deleted. Retry when the backend is available.");
      }
    }
  }, []);
  useEffect(() => { void Promise.resolve().then(restore); }, [restore]);
  const save = (p: Profile | null) => {
    currentProfile.current = p;
    setProfile(p);
    setResult(null); // Decisions for an old profile must never survive an edit.
    try {
      if (p) sessionStorage.setItem("schemeradar-profile", JSON.stringify(p));
      else { sessionStorage.removeItem("schemeradar-profile"); setResearchResult(null); }
      setSessionError("");
    } catch { setSessionError("Browser storage is unavailable. Your profile is usable on this page but will not survive a reload."); }
  };
  const isCurrentProfile = (p: Profile | null) => JSON.stringify(p) === JSON.stringify(currentProfile.current);
  return <Context.Provider value={{profile, setProfile: save, result, setResult, researchResult, setResearchResult, isCurrentProfile}}>
    <div className="workspace">
      <aside className="sidebar">
        <Link href="/" className="brand"><span className="brand-mark">S<span>↗</span></span><span>SchemeRadar<small>OPPORTUNITY, CLARIFIED.</small></span></Link>
        <div className="nav-label">YOUR WORKSPACE</div>
        <nav aria-label="Main navigation">{links.map(([url, icon, label]) => <Link key={url} href={url} aria-current={path === url ? "page" : undefined} className={path === url ? "nav-link active" : "nav-link"}><Icon name={icon}/>{label}{path === url && <span className="active-dot"/>}</Link>)}</nav>
        <div className="sidebar-note"><div className="small-symbol">✓</div><strong>Evidence before answers.</strong><p>Official sources. Transparent rules. No guesswork about your future.</p><Link href="/research">Explore the research desk <span>↗</span></Link></div>
        <div className="sidebar-bottom"><span className="avatar">ST</span><div>Student workspace<small>No account required</small></div></div>
      </aside>
      <div className="main-wrap"><header className="topbar"><span>Workspace <span className="breadcrumb">/ {links.find(([url]) => url === path)?.[2] || "Overview"}</span></span><span className="privacy"><span/> Profile stored only in your browser session</span></header><main>{sessionError && <div className="alert" role="alert"><p>{sessionError}</p><button className="button secondary" onClick={() => void restore()}>Retry saved profile</button></div>}{children}</main><footer>SchemeRadar <span>Built for informed decisions, not assumptions.</span><a href="/api/docs" target="_blank" rel="noreferrer">API reference ↗</a></footer></div>
    </div>
  </Context.Provider>;
}
export function Alert({children}: {children: ReactNode}) {return <div role="alert" className="alert">{children}</div>;}
export function PageHeading({eyebrow, title, description}: {eyebrow: string; title: string; description: string}) {
  return <div className="page-heading"><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>;
}
