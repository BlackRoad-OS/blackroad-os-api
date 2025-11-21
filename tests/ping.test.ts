import request from "supertest";
import app from "../src/index";

describe("GET /v1/ping", () => {
  it("returns ok response", async () => {
    const response = await request(app).get("/v1/ping");

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty("ok", true);
    expect(response.body).toHaveProperty("service", "api");
  });
});
