import request from "supertest";
import { createServer } from "../src/server";

const app = createServer();

describe("GET /health", () => {
  it("returns ok with uptime and env", async () => {
    const res = await request(app).get("/health").expect(200);

    expect(res.body.status).toBe("ok");
    expect(typeof res.body.uptimeSeconds).toBe("number");
    expect(res.body.env).toBeDefined();
  });
});
