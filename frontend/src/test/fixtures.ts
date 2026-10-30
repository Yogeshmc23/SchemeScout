// Synthetic test fixtures ONLY. Never imported by application pages/services.
import type { AgentResult, Profile, Scholarship } from "../lib/types";
export const profileFixture: Profile = {
  state: "Karnataka", course: "B.Tech", education_level: "Undergraduate",
  study_year: 2, annual_income: 250000, category: "OBC",
};
const criterion = {status: "ANY" as const, values: [], minimum: null, maximum: null,
  minimum_exclusive: false, maximum_exclusive: false, evidence: "All students may apply."};
export const scholarshipFixture: Scholarship = {
  name: "Synthetic test scholarship", description: null, benefits: null, deadline: null,
  application_url: null, source_url: "https://scholarships.gov.in/test",
  required_documents: [], missing_information: [], fact_evidence: {},
  rules: {state: {...criterion}, course: {...criterion}, education_level: {...criterion},
    study_year: {...criterion}, annual_income: {...criterion}, category: {...criterion}},
  eligibility_complete: true, completeness_evidence: "All students may apply.",
  extraction_status: "EXTRACTED", official_source: true,
  last_verified_at: null, fetched_at: null, source_evidence: "All students may apply.",
};
export const resultFixture: AgentResult = {
  mode: "DISCOVER", query: "Synthetic test query", summary: "Synthetic test workflow result",
  sources: [{title: "Synthetic official page", url: scholarshipFixture.source_url, snippet: "", official: true}],
  scholarships: [scholarshipFixture], source_outcomes: [{url: scholarshipFixture.source_url,
    stage: "FETCH", status: "SUCCESS", message: "Fetched test page"}],
  matches: [{scholarship: scholarshipFixture, status: "NEEDS_INFORMATION", checks: [{
    field: "coverage", outcome: "UNKNOWN", reason: "Synthetic coverage check", evidence: null,
  }]}], errors: [], steps: ["Synthetic test execution"], stored_count: 1,
};
