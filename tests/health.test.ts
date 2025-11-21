import request from "supertest";
import app from "../src/index";

describe("GET /health", () => {
  it("returns ok status and service id", async () => {
    const response = await request(app).get("/health");

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty("ok", true);
    expect(response.body).toHaveProperty("service", "api");
  });
});
