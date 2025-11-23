import request from "supertest";
import { createApp } from "../src/server";

const app = createApp();

describe("GET /api/v1/health", () => {
  it("returns ok with overall status and services", async () => {
    const res = await request(app).get("/api/v1/health").expect(200);

    expect(res.body.ok).toBe(true);
    expect(res.body.data.overallStatus).toBeDefined();
    expect(Array.isArray(res.body.data.services)).toBe(true);
  });
});
