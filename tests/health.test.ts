import request from "supertest";
import app from "../src/index";

describe("GET /api/health", () => {
  it("returns ok status and service id", async () => {
    const response = await request(app).get("/api/health");

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty("status", "ok");
    expect(response.body).toHaveProperty("service", "blackroad-os-api");
  });
});
