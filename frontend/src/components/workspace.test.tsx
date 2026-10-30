// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Workspace, useWorkspace } from "./workspace";
import { profileFixture, resultFixture } from "../test/fixtures";
const mocks = vi.hoisted(() => ({ api: vi.fn() }));
vi.mock("../lib/api", async importOriginal => ({...await importOriginal<typeof import("../lib/api")>(), api: mocks.api}));
vi.mock("next/navigation", () => ({usePathname: () => "/profile"}));
vi.mock("next/link", () => ({default: ({children, ...props}: React.ComponentProps<"a">) => <a {...props}>{children}</a>}));
function Consumer() {
  const store = useWorkspace();
  return <><p data-testid="state">{store.profile?.state || "none"}</p>
    <p data-testid="discovery">{store.result?.query || "none"}</p>
    <p data-testid="research">{store.researchResult?.query || "none"}</p>
    <button onClick={() => store.setProfile(profileFixture)}>Save first profile</button>
    <button onClick={() => store.setResult(resultFixture)}>Save discovery</button>
    <button onClick={() => store.setResearchResult({...resultFixture, mode: "RESEARCH"})}>Save research</button>
    <button onClick={() => store.setProfile({...profileFixture, state: "Kerala"})}>Change profile</button>
    <button onClick={() => store.setProfile(null)}>Clear profile</button></>;
}
beforeEach(() => { sessionStorage.clear(); mocks.api.mockReset(); });
afterEach(cleanup);
describe("Workspace profile/result safety", () => {
  it("invalidates decisions when a profile changes without erasing unrelated research", () => {
    render(<Workspace><Consumer/></Workspace>);
    fireEvent.click(screen.getByText("Save first profile"));
    fireEvent.click(screen.getByText("Save discovery"));
    fireEvent.click(screen.getByText("Save research"));
    expect(screen.getByTestId("discovery").textContent).toBe(resultFixture.query);
    fireEvent.click(screen.getByText("Change profile"));
    expect(screen.getByTestId("state").textContent).toBe("Kerala");
    expect(screen.getByTestId("discovery").textContent).toBe("none");
    expect(screen.getByTestId("research").textContent).toBe(resultFixture.query);
    fireEvent.click(screen.getByText("Clear profile"));
    expect(screen.getByTestId("research").textContent).toBe("none");
    expect(sessionStorage.getItem("schemeradar-profile")).toBeNull();
  });
  it("preserves saved profile on a transient outage and supports retry", async () => {
    sessionStorage.setItem("schemeradar-profile", JSON.stringify(profileFixture));
    mocks.api.mockRejectedValueOnce(new Error("Offline")).mockResolvedValueOnce(profileFixture);
    render(<Workspace><Consumer/></Workspace>);
    await waitFor(() => expect(screen.getByRole("alert").textContent).toContain("not been deleted"));
    expect(sessionStorage.getItem("schemeradar-profile")).not.toBeNull();
    fireEvent.click(screen.getByText("Retry saved profile"));
    await waitFor(() => expect(screen.getByTestId("state").textContent).toBe("Karnataka"));
    expect(screen.queryByRole("alert")).toBeNull();
  });
  it("does not let late restoration overwrite a newly edited profile", async () => {
    sessionStorage.setItem("schemeradar-profile", JSON.stringify(profileFixture));
    let resolve!: (value: typeof profileFixture) => void;
    mocks.api.mockImplementation(() => new Promise(done => {resolve = done;}));
    render(<Workspace><Consumer/></Workspace>);
    await waitFor(() => expect(mocks.api).toHaveBeenCalled());
    fireEvent.click(screen.getByText("Change profile"));
    resolve(profileFixture);
    await waitFor(() => expect(screen.getByTestId("state").textContent).toBe("Kerala"));
  });
});
