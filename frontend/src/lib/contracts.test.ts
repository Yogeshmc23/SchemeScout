import { describe, expect, it } from "vitest";
import { isAgentResult, isMatch, isProfile, isScholarship, validResponse } from "./contracts";
import { profileFixture, resultFixture, scholarshipFixture } from "../test/fixtures";
describe("Backend response contracts", () => {
  it("accepts complete profile/scholarship/match/agent shapes", () => {
    expect(isProfile(profileFixture)).toBe(true);
    expect(isScholarship(scholarshipFixture)).toBe(true);
    expect(isMatch(resultFixture.matches[0])).toBe(true);
    expect(isAgentResult(resultFixture)).toBe(true);
  });
  it("rejects unsafe source URLs", () => {
    expect(isScholarship({...scholarshipFixture, source_url: "javascript:alert(1)"})).toBe(false);
    expect(isAgentResult({...resultFixture, sources: [{...resultFixture.sources[0], url: "file:///etc/passwd"}]})).toBe(false);
  });
  it("rejects missing nested contracts", () => {
    expect(isScholarship({...scholarshipFixture, rules: {}})).toBe(false);
    expect(isAgentResult({...resultFixture, source_outcomes: [{url: "bad"}]})).toBe(false);
  });
});

it("rejects malformed detail/history payloads", () => {
  expect(validResponse("scholarships/1", {})).toBe(false);
  expect(validResponse("scholarships/1/history", [{id: 1, recorded_at: "now", scholarship: {}}])).toBe(false);
  expect(validResponse("research/history", [{id: "test", query: "test"}])).toBe(false);
  expect(validResponse("research/history/test", {})).toBe(false);
});
