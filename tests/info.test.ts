import request from "supertest";
import app from "../src/index";
import packageInfo from "../package.json";

describe("GET /info", () => {
  it("returns service metadata", async () => {
    const response = await request(app).get("/info");

    expect(response.status).toBe(200);
    expect(response.body).toMatchObject({
      id: "api",
      name: "BlackRoad OS – Public API",
      version: packageInfo.version,
    });
  });
});
