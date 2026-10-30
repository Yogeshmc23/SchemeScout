// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import ProfilePage from "../app/profile/page";
import { ResearchForm } from "./research-form";
import AssistantPage from "../app/assistant/page";
import EligibilityPage from "../app/eligibility/page";
import { profileFixture, resultFixture } from "../test/fixtures";
import type { Profile } from "../lib/types";

const mocks = vi.hoisted(() => ({ api: vi.fn(), save: vi.fn(), result: vi.fn(), profile: null as Profile | null, current: vi.fn() }));
vi.mock("../lib/api", () => ({ api: mocks.api }));
vi.mock("next/link", () => ({default: ({children, href}: {children: React.ReactNode; href: string}) => <a href={href}>{children}</a>}));
vi.mock("./workspace", () => ({
  useWorkspace: () => ({profile: mocks.profile, setProfile: mocks.save, result: null, setResult: mocks.result, researchResult: null, setResearchResult: mocks.result, isCurrentProfile: mocks.current}),
  Alert: ({children}: {children: React.ReactNode}) => <div role="alert">{children}</div>,
  PageHeading: ({title}: {title: string}) => <h1>{title}</h1>,
}));
beforeEach(() => {mocks.profile = null; mocks.current.mockReturnValue(true);});
afterEach(() => {cleanup(); vi.clearAllMocks();});
describe("Student-facing forms", () => {
  it("submits typed profile data to FastAPI", async () => {
    mocks.api.mockResolvedValue({state: "Karnataka", course: "B.Tech", education_level: null, category: null, study_year: 2, annual_income: 250000});
    render(<ProfilePage/>);
    fireEvent.change(screen.getByLabelText("State / Union territory"), {target: {value: "Karnataka"}});
    fireEvent.change(screen.getByLabelText("Course"), {target: {value: "B.Tech"}});
    fireEvent.change(screen.getByLabelText("Year of study"), {target: {value: "2"}});
    fireEvent.change(screen.getByLabelText("Annual family income (₹)"), {target: {value: "250000"}});
    fireEvent.click(screen.getByText("Save student profile"));
    await waitFor(() => expect(mocks.save).toHaveBeenCalled());
    expect(mocks.api.mock.calls[0]).toEqual(["profile", {state: "Karnataka", course: "B.Tech", education_level: null, category: null, study_year: 2, annual_income: 250000}]);
    expect(screen.getByRole("status").textContent).toContain("validated");
  });
  it("shows backend errors without claiming a saved profile", async () => {
    mocks.api.mockRejectedValue(new Error("Backend unavailable"));
    render(<ProfilePage/>);
    fireEvent.click(screen.getByText("Save student profile"));
    await waitFor(() => expect(screen.getByRole("alert").textContent).toContain("Backend unavailable"));
    expect(mocks.save).not.toHaveBeenCalled();
  });
  it("disables discovery until a profile exists", () => {
    render(<ResearchForm mode="DISCOVER"/>);
    const button = screen.getByRole("button", {name: "Discover scholarships →"}) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
  });
  it("shows real pending and failure states for research", async () => {
    let reject: (e: Error) => void = () => {};
    mocks.api.mockImplementation(() => new Promise((_resolve, rejectPromise) => { reject = rejectPromise; }));
    render(<ResearchForm mode="RESEARCH"/>);
    fireEvent.change(screen.getByLabelText("What would you like to explore?"), {target: {value: "Karnataka engineering scholarships"}});
    fireEvent.click(screen.getByText("Research sources →"));
    expect(screen.getByRole("status").textContent).toContain("Following the evidence");
    reject(new Error("TinyFish is not configured"));
    await waitFor(() => expect(screen.getByRole("alert").textContent).toContain("TinyFish"));
  });
  it("connects chat to the backend and displays the answer", async () => {
    mocks.api.mockResolvedValue({summary: "No scholarship evidence is stored yet."});
    render(<AssistantPage/>);
    fireEvent.change(screen.getByLabelText("Your scholarship question"), {target: {value: "What documents are required?"}});
    fireEvent.click(screen.getByText("Send ↑"));
    await waitFor(() => expect(screen.getByText("No scholarship evidence is stored yet.")).toBeTruthy());
    expect(mocks.api).toHaveBeenCalledWith("chat", {query: "What documents are required?"});
  });
});

it("discards an in-flight discovery result when the profile changes", async () => {
  mocks.profile = profileFixture;
  let resolve!: (value: typeof resultFixture) => void;
  mocks.api.mockImplementation(() => new Promise(done => {resolve = done;}));
  render(<ResearchForm mode="DISCOVER"/>);
  fireEvent.change(screen.getByLabelText("What would you like to explore?"), {target: {value: "Karnataka scholarships"}});
  fireEvent.click(screen.getByText("Discover scholarships →"));
  mocks.current.mockReturnValue(false);
  resolve(resultFixture);
  await waitFor(() => expect(screen.getByRole("alert").textContent).toContain("profile changed"));
  expect(mocks.result).not.toHaveBeenCalledWith(resultFixture);
});
it("rechecks stored scholarships through the actual eligibility contract", async () => {
  mocks.profile = profileFixture;
  mocks.api.mockResolvedValue(resultFixture.matches);
  render(<EligibilityPage/>);
  fireEvent.click(screen.getByText("Recheck stored scholarships"));
  await waitFor(() => expect(screen.getByText("Stored scholarship eligibility")).toBeTruthy());
  expect(mocks.api.mock.calls[0][0]).toBe("eligibility");
  expect(mocks.api.mock.calls[0][1]).toEqual(profileFixture);
  expect(screen.getByText("Synthetic coverage check")).toBeTruthy();
});
it("renders assistant grounding links independently of model-generated text", async () => {
  mocks.api.mockResolvedValue({...resultFixture, mode: "CHAT"});
  render(<AssistantPage/>);
  fireEvent.change(screen.getByLabelText("Your scholarship question"), {target: {value: "What documents are required?"}});
  fireEvent.click(screen.getByText("Send ↑"));
  await waitFor(() => expect(screen.getByRole("link", {name: "Synthetic official page ↗"})).toBeTruthy());
  expect(screen.getByRole("link", {name: "Synthetic official page ↗"}).getAttribute("href")).toBe(resultFixture.sources[0].url);
});
