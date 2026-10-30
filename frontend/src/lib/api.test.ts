import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";
afterEach(() => vi.unstubAllGlobals());
describe("API service", () => {
  it("uses relative same-origin URLs and correct body", async () => {
    const mock = vi.fn().mockResolvedValue(new Response(JSON.stringify({state: "Karnataka", course: null, education_level: null, study_year: null, annual_income: null, category: null}), {status: 200}));
    vi.stubGlobal("fetch", mock);
    const result = await api<{state: string}>("profile", {state: "Karnataka"});
    expect(result.state).toBe("Karnataka");
    expect(mock.mock.calls[0][0]).toBe("/api/profile");
    expect(mock.mock.calls[0][1].method).toBe("POST");
    expect(JSON.parse(mock.mock.calls[0][1].body)).toEqual({state: "Karnataka"});
  });
  it("surfaces provider errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({detail: "TinyFish is not configured"}), {status: 503})));
    await expect(api("research", {query: "test"})).rejects.toThrow("TinyFish is not configured");
  });
  it("surfaces validation errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({detail: [{msg: "Invalid income"}]}), {status: 422})));
    await expect(api("profile", {})).rejects.toThrow("Invalid income");
  });
  it("does not swallow proxy failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("upstream failed", {status: 502})));
    await expect(api("health")).rejects.toThrow("502");
  });
});

it.each([null, {}, {state: "Karnataka"}])("rejects invalid successful profile responses: %j", async data => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(data), {status: 200})));
  await expect(api("profile", {})).rejects.toThrow("invalid response");
});
it("rejects non-JSON successful responses", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("HTML instead of data", {status: 200})));
  await expect(api("research", {query: "test"})).rejects.toThrow("invalid response");
});
it("shows an actionable network error", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Internal network details")));
  await expect(api("health")).rejects.toThrow("Could not reach SchemeRadar");
});
it("supports caller cancellation", async () => {
  const controller = new AbortController(); controller.abort();
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new DOMException("Aborted", "AbortError")));
  await expect(api("health", undefined, controller.signal)).rejects.toThrow("Request cancelled");
});
it("reports timeouts without inventing successful results", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new DOMException("Timed out", "TimeoutError")));
  await expect(api("research", {query: "test"})).rejects.toThrow("timed out");
});
