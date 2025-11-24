import request from "supertest";
import { createApp } from "../src/server";

const app = createApp();

describe("request validation", () => {
  it("rejects unknown agent status filters", async () => {
    const res = await request(app).get("/api/v1/agents?status=bogus").expect(400);

    expect(res.body.ok).toBe(false);
    expect(res.body.error.code).toBe("INVALID_REQUEST");
  });

  it("clamps and defaults events limit", async () => {
    const res = await request(app).get("/api/v1/events?limit=1").expect(200);

    expect(res.body.ok).toBe(true);
    expect(res.body.data.length).toBe(1);
  });

  it("rejects invalid event severity", async () => {
    const res = await request(app)
      .get("/api/v1/events?severity=critical")
      .expect(400);

    expect(res.body.ok).toBe(false);
    expect(res.body.error.code).toBe("INVALID_REQUEST");
    expect(res.body.error.details?.length).toBeGreaterThan(0);
  });
});
