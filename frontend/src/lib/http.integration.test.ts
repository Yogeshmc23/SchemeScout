// Opt-in real HTTP integration: start both servers and set SCHEMERADAR_SMOKE_URL.
// These tests use explicit synthetic input, not fabricated live discovery results.
import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";
import { profileFixture, scholarshipFixture } from "../test/fixtures";
import type { Match, Profile } from "./types";
const base = process.env.SCHEMERADAR_SMOKE_URL;
const actualFetch = globalThis.fetch;
afterEach(() => vi.unstubAllGlobals());
function connect() {
  vi.stubGlobal("fetch", (input: string, init: RequestInit) => actualFetch(new URL(input, base), init));
}
describe.skipIf(!base)("Actual Next.js → FastAPI proxy", () => {
  it("validates a student profile using the frontend runtime contract", async () => {
    connect();
    expect(await api<Profile>("profile", profileFixture)).toEqual(profileFixture);
  });
  it("surfaces real backend validation without echoing a rejected private field", async () => {
    connect();
    await expect(api("profile", {annual_income: -1, secret: "test-private-value"})).rejects.toMatchObject({status: 422});
    try {await api("profile", {annual_income: -1, secret: "test-private-value"});}
    catch(e) {expect((e as Error).message).not.toContain("test-private-value");}
  });
  it("evaluates explicit test records without allowing forged official provenance", async () => {
    connect();
    const matches = await api<Match[]>("match", {profile: profileFixture, scholarships: [scholarshipFixture]});
    expect(matches[0].status).toBe("NEEDS_INFORMATION");
    expect(matches[0].scholarship.official_source).toBe(false);
    expect(matches[0].checks.some(c => c.field === "source" && c.outcome === "UNKNOWN")).toBe(true);
  });
});
