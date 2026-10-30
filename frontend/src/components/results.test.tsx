// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Results, ScholarshipCard } from "./results";
import { resultFixture, scholarshipFixture } from "../test/fixtures";
afterEach(cleanup);
describe("Evidence and eligibility results", () => {
  it("renders the query, decision reasons and actual page outcomes", () => {
    render(<Results result={resultFixture}/>);
    expect(screen.getByText(resultFixture.query)).toBeTruthy();
    expect(screen.getByText("Synthetic coverage check")).toBeTruthy();
    expect(screen.getByText("Fetched test page")).toBeTruthy();
    expect(screen.getByText("Discovered sources")).toBeTruthy();
  });
  it("shows an explicit empty category when filtering", () => {
    render(<Results result={resultFixture}/>);
    const eligible = screen.getByRole("button", {name: /^Eligible/});
    fireEvent.click(eligible);
    expect(eligible.getAttribute("aria-pressed")).toBe("true");
    expect(screen.getByText("No scholarships in this category")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", {name: /^Needs information/}));
    expect(screen.getByText(scholarshipFixture.name)).toBeTruthy();
  });
  it("never calls an unconfirmed source official", () => {
    render(<ScholarshipCard s={{...scholarshipFixture, official_source: false}}/>);
    expect(screen.getByRole("link", {name: "Read unconfirmed source ↗"}).getAttribute("href")).toBe(scholarshipFixture.source_url);
    expect(screen.queryByText("Read official source ↗")).toBeNull();
  });
});
