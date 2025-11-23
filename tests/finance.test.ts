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
