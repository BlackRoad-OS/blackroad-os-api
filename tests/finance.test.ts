import request from "supertest";
import { createApp } from "../src/server";

const app = createApp();

describe("GET /api/v1/finance/snapshot", () => {
  it("returns a finance snapshot in the standard envelope", async () => {
    const res = await request(app).get("/api/v1/finance/snapshot").expect(200);

    expect(res.body.ok).toBe(true);
    expect(res.body.data.timestamp).toBeDefined();
    expect(res.body.data.walletBalanceUsd).toBeDefined();
  });
});

describe("GET /api/v1/finance/summary", () => {
  it("returns a finance summary from the operator", async () => {
    const res = await request(app).get("/api/v1/finance/summary").expect(200);

    expect(res.body.ok).toBe(true);
    expect(res.body.data.cashBalance).toBeDefined();
    expect(res.body.data.currency).toBe("USD");
    expect(res.body.data.runwayMonths).toBeGreaterThan(0);
  });
});

describe("GET /api/v1/finance/cash-forecast", () => {
  it("returns a cash forecast with ordered buckets", async () => {
    const res = await request(app)
      .get("/api/v1/finance/cash-forecast")
      .expect(200);

    expect(res.body.ok).toBe(true);
    expect(Array.isArray(res.body.data.buckets)).toBe(true);
    expect(res.body.data.buckets.length).toBeGreaterThan(0);
    expect(res.body.data.buckets[0].startDate).toBeDefined();
    expect(res.body.data.currency).toBe("USD");
  });
});
