// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import ScholarshipDetail from "@/app/scholarships/[id]/page";
import { scholarships } from "@/lib/scholarships";
import { scholarshipFixture } from "../test/fixtures";

vi.mock("next/navigation", () => ({useParams: () => ({id: "1"})}));
afterEach(() => { cleanup(); vi.restoreAllMocks(); });
it("loads persisted details and reports absent legacy extraction history honestly", async () => {
  vi.spyOn(scholarships, "detail").mockResolvedValue({...scholarshipFixture, id: 1});
  vi.spyOn(scholarships, "history").mockResolvedValue([]);
  render(<ScholarshipDetail/>);
  expect(await screen.findByText(scholarshipFixture.name)).toBeTruthy();
  expect(await screen.findByText(/Older records are not retroactively assigned fabricated history/)).toBeTruthy();
});
it("does not discard a valid record when history fails", async () => {
  vi.spyOn(scholarships, "detail").mockResolvedValue({...scholarshipFixture, id: 1});
  vi.spyOn(scholarships, "history").mockRejectedValue(new Error("Snapshot storage unavailable"));
  render(<ScholarshipDetail/>);
  expect(await screen.findByText(scholarshipFixture.name)).toBeTruthy();
  expect(await screen.findByRole("alert")).toHaveProperty("textContent", "Snapshot storage unavailable");
});
