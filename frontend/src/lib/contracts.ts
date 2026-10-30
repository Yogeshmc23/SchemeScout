// Runtime guards for API data: TypeScript casts alone cannot validate network responses.
type ObjectValue = Record<string, unknown>;
const object = (v: unknown): v is ObjectValue => typeof v === "object" && v !== null && !Array.isArray(v);
const strings = (v: unknown): v is string[] => Array.isArray(v) && v.every(x => typeof x === "string");
const nullableString = (v: unknown) => v === null || typeof v === "string";
const nullableNumber = (v: unknown) => v === null || (typeof v === "number" && Number.isInteger(v));
const arrayOf = (v: unknown, check: (x: unknown) => boolean) => Array.isArray(v) && v.every(check);
const oneOf = (v: unknown, values: string[]) => typeof v === "string" && values.includes(v);
const url = (v: unknown) => {
  if (typeof v !== "string") return false;
  try { const parsed = new URL(v); return ["http:", "https:"].includes(parsed.protocol) && !parsed.username && !parsed.password; }
  catch { return false; }
};
const nullableUrl = (v: unknown) => v === null || url(v);
export function isProfile(v: unknown): boolean {
  return object(v) && ["state", "course", "education_level", "category"].every(k => nullableString(v[k])) &&
    ["study_year", "annual_income"].every(k => nullableNumber(v[k]));
}
function isCriterion(v: unknown): boolean {
  return object(v) && (v.mandatory === undefined || typeof v.mandatory === "boolean") && oneOf(v.status, ["UNKNOWN", "ANY", "RESTRICTED"]) && strings(v.values) &&
    nullableNumber(v.minimum) && nullableNumber(v.maximum) && nullableString(v.evidence) &&
    typeof v.minimum_exclusive === "boolean" && typeof v.maximum_exclusive === "boolean";
}
export function isScholarship(v: unknown): boolean {
  return object(v) && (v.id === undefined || v.id === null || (typeof v.id === "number" && Number.isSafeInteger(v.id) && v.id > 0)) &&
    (v.updated_at === undefined || nullableString(v.updated_at)) && typeof v.name === "string" && nullableString(v.description) && nullableString(v.benefits) &&
    nullableString(v.deadline) && nullableUrl(v.application_url) && url(v.source_url) &&
    strings(v.required_documents) && strings(v.missing_information) && object(v.fact_evidence) &&
    Object.values(v.fact_evidence).every(x => typeof x === "string") && object(v.rules) &&
    ["state", "course", "education_level", "study_year", "annual_income", "category"].every(k => isCriterion((v.rules as ObjectValue)[k])) &&
    typeof v.eligibility_complete === "boolean" && nullableString(v.completeness_evidence) &&
    oneOf(v.extraction_status, ["PARTIAL", "EXTRACTED"]) && typeof v.official_source === "boolean" &&
    nullableString(v.last_verified_at) && nullableString(v.fetched_at) && typeof v.source_evidence === "string";
}
function isSource(v: unknown): boolean {
  return object(v) && typeof v.title === "string" && url(v.url) && typeof v.snippet === "string" && typeof v.official === "boolean";
}
export function isMatch(v: unknown): boolean {
  return object(v) && isScholarship(v.scholarship) && oneOf(v.status, ["ELIGIBLE", "NEEDS_INFORMATION", "NOT_ELIGIBLE"]) &&
    arrayOf(v.checks, c => object(c) && typeof c.field === "string" && oneOf(c.outcome, ["PASS", "FAIL", "UNKNOWN"]) &&
      typeof c.reason === "string" && nullableString(c.evidence));
}
function isOutcome(v: unknown): boolean {
  return object(v) && url(v.url) && oneOf(v.stage, ["FETCH", "EXTRACT", "DETAIL_FETCH", "DETAIL_EXTRACT"]) &&
    oneOf(v.status, ["SUCCESS", "FAILED"]) && typeof v.message === "string";
}
export function isAgentResult(v: unknown): boolean {
  return object(v) && (v.execution === undefined || arrayOf(v.execution, e => object(e) && typeof e.stage === "string" && oneOf(e.status, ["SUCCESS", "FAILED"]) && typeof e.duration_ms === "number" && Number.isInteger(e.duration_ms) && e.duration_ms >= 0)) && typeof v.mode === "string" && typeof v.query === "string" && typeof v.summary === "string" &&
    arrayOf(v.sources, isSource) && arrayOf(v.source_outcomes, isOutcome) && arrayOf(v.scholarships, isScholarship) &&
    arrayOf(v.matches, isMatch) && strings(v.errors) && strings(v.steps) &&
    typeof v.stored_count === "number" && Number.isInteger(v.stored_count) && v.stored_count >= 0;
}
export function validResponse(path: string, data: unknown): boolean {
  const route = path.split("?")[0];
  if (/^scholarships\/\d+\/history$/.test(route)) return arrayOf(data, s => object(s) && typeof s.id === "number" && typeof s.recorded_at === "string" && isScholarship(s.scholarship));
  if (/^scholarships\/\d+$/.test(route)) return isScholarship(data);
  if (route === "research/history") return arrayOf(data, r => object(r) && typeof r.id === "string" && typeof r.query === "string" && typeof r.created_at === "string" && typeof r.scholarship_count === "number");
  if (route.startsWith("research/history/")) return isAgentResult(data);
  if (path === "profile") return isProfile(data);
  if (path === "scholarships") return arrayOf(data, isScholarship);
  if (path === "eligibility" || path === "match") return arrayOf(data, isMatch);
  if (["discover", "research", "chat", "agent"].includes(path)) return isAgentResult(data);
  if (path === "search") return arrayOf(data, isSource);
  if (path === "extract") return isScholarship(data);
  // Reject null even for routes without a dedicated UI contract.
  return data !== null && data !== undefined;
}
