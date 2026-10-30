// Mirrors backend/app/models.py; nullable fields are never replaced with guessed defaults.
export interface Profile {
  state: string | null; course: string | null; education_level: string | null;
  study_year: number | null; annual_income: number | null; category: string | null;
}
export interface Criterion {
  mandatory?: boolean;
  status: "UNKNOWN" | "ANY" | "RESTRICTED"; values: string[];
  minimum: number | null; maximum: number | null; minimum_exclusive: boolean; maximum_exclusive: boolean; evidence: string | null;
}
export interface Scholarship {
  id?: number | null; updated_at?: string | null;
  name: string; description: string | null; benefits: string | null; deadline: string | null;
  application_url: string | null; source_url: string; required_documents: string[];
  missing_information: string[]; fact_evidence: Record<string, string>; rules: Record<keyof Profile, Criterion>;
  eligibility_complete: boolean; completeness_evidence: string | null;
  extraction_status: "PARTIAL" | "EXTRACTED"; official_source: boolean;
  last_verified_at: string | null; fetched_at: string | null; source_evidence: string;
}
export interface Source { title: string; url: string; snippet: string; official: boolean }
export type EligibilityStatus = "ELIGIBLE" | "NEEDS_INFORMATION" | "NOT_ELIGIBLE";
export interface Match {
  scholarship: Scholarship; status: EligibilityStatus;
  checks: {field: string; outcome: "PASS" | "FAIL" | "UNKNOWN"; reason: string; evidence: string | null; mandatory?: boolean; student_value?: string | number | null; requirement?: Criterion | null}[];
}
export interface SourceOutcome {
  url: string; stage: "FETCH" | "EXTRACT" | "DETAIL_FETCH" | "DETAIL_EXTRACT";
  status: "SUCCESS" | "FAILED"; message: string;
}
export interface AgentResult {
  workflow_id?: string | null; research_id?: string | null;
  execution?: {stage: string; status: "SUCCESS" | "FAILED"; duration_ms: number}[];
  mode: string; query: string; source_outcomes: SourceOutcome[]; summary: string; sources: Source[]; scholarships: Scholarship[];
  matches: Match[]; errors: string[]; steps: string[]; stored_count: number;
}

export interface ExtractionSnapshot { id: number; recorded_at: string; scholarship: Scholarship }
export interface ResearchRun { id: string; query: string; created_at: string; scholarship_count: number }
