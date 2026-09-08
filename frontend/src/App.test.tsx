import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

vi.mock("./MapPanel", () => ({ MapPanel: () => <div data-testid="map-panel" /> }));

describe("App", () => {
  afterEach(() => vi.restoreAllMocks());
  it("shows operational when the API responds", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      const body = url.endsWith("/database/status")
        ? {status:"ready",provider:"supabase-postgresql",database:"postgres",postgis_version:"3.3",schema_version:"20260909_0002",lookup_records:10}
        : url.endsWith("/map/areas")
          ? {type:"FeatureCollection",features:[]}
          : {service:"wildtrack-api",status:"operational",environment:"test",api_version:"v1",timestamp:"2026-09-09T00:00:00Z"};
      return new Response(JSON.stringify(body), {status:200});
    });
    render(<App />);
    await waitFor(() => expect(screen.getByText("API operational")).toBeInTheDocument());
    await waitFor(() => expect(screen.getByText("POSTGIS READY")).toBeInTheDocument());
  });
  it("shows a useful offline state", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("offline"));
    render(<App />);
    await waitFor(() => expect(screen.getByText("API offline")).toBeInTheDocument());
  });
});
