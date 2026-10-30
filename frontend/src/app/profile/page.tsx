"use client";
import { useState, type FormEvent } from "react";
import Link from "next/link";
import { Alert, PageHeading, useWorkspace } from "@/components/workspace";
import { api } from "@/lib/api";
import type { Profile } from "@/lib/types";
const textFields = [["state", "State / Union territory", "e.g. Karnataka"], ["course", "Course", "Use the exact course name, e.g. B.Tech"], ["education_level", "Education level", "e.g. Undergraduate"], ["category", "Category", "e.g. General, SC, ST, OBC"]] as const;
export default function ProfilePage() {
  const {profile, setProfile} = useWorkspace();
  const [busy, setBusy] = useState(false); const [error, setError] = useState(""); const [saved, setSaved] = useState(false);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault(); setError(""); setSaved(false); setBusy(true);
    const form = new FormData(e.currentTarget);
    const value = (key: string) => String(form.get(key) || "").trim() || null;
    const numeric = (key: string) => value(key) === null ? null : Number(value(key));
    try { const p = await api<Profile>("profile", {state: value("state"), course: value("course"), education_level: value("education_level"), category: value("category"), study_year: numeric("study_year"), annual_income: numeric("annual_income")}); setProfile(p); setSaved(true); }
    catch (e) {setError(e instanceof Error ? e.message : "Could not validate profile.");} finally {setBusy(false);}
  }
  return <><PageHeading eyebrow="YOUR STARTING POINT" title="A profile that opens possibilities." description="Share only what you know. Missing details lead to uncertain matches, never assumed eligibility."/><div className="form-layout"><form key={JSON.stringify(profile)} className="panel profile-form" onSubmit={submit}><h2>Student details</h2><p className="muted">Validated by SchemeRadar. Stored only in this browser tab’s session.</p><div className="form-grid">{textFields.map(([key, label, placeholder]) => <label key={key}>{label}<input name={key} placeholder={placeholder} minLength={2} maxLength={key === "course" ? 120 : 80} defaultValue={profile?.[key] || ""}/></label>)}<label>Year of study<input name="study_year" type="number" min={1} max={12} step={1} placeholder="e.g. 2" defaultValue={profile?.study_year ?? ""}/></label><label>Annual family income (₹)<input name="annual_income" type="number" min={0} max={1000000000} step={1} placeholder="e.g. 250000" defaultValue={profile?.annual_income ?? ""}/></label></div>{error && <Alert>{error}</Alert>}{saved && <div className="success" role="status">Profile validated and saved for this session. <Link href="/discover">Discover scholarships →</Link></div>}<div className="form-actions"><button className="button" disabled={busy}>{busy ? "Validating…" : "Save student profile"}</button>{profile && <button type="button" className="button secondary" onClick={() => {setProfile(null); setSaved(false);}}>Clear my session profile</button>}</div></form><aside className="info-panel"><div className="eyebrow">YOU STAY IN CONTROL</div><h2>No assumptions.<br/>No unnecessary data.</h2><p>We don’t need your name, email, Aadhaar number or documents to check scholarship requirements.</p><p>Course and category names are compared exactly after spacing and case normalization. We never silently assume equivalent qualifications.</p></aside></div></>;
}
