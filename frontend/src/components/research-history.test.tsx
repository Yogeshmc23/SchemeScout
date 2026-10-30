// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { ResearchHistory } from "./research-history";
import { researchHistory } from "@/lib/scholarships";

afterEach(() => { cleanup(); vi.restoreAllMocks(); });
it("loads real service history on request and displays empty state", async () => {
  const list = vi.spyOn(researchHistory, "list").mockResolvedValue([]);
  render(<ResearchHistory/>);
  expect(list).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", {name: "Load saved research"}));
  expect(await screen.findByText("No research runs have been saved.")).toBeTruthy();
});
it("shows disabled history without substituting fixtures", async () => {
  vi.spyOn(researchHistory, "list").mockRejectedValue(new Error("Research history is disabled for privacy."));
  render(<ResearchHistory/>);
  fireEvent.click(screen.getByRole("button", {name: "Load saved research"}));
  expect(await screen.findByRole("alert")).toHaveProperty("textContent", "Research history is disabled for privacy.");
});
