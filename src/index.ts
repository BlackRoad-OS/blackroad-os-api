import express from "express";
import { env } from "./config/env";
import { createProxyRouter } from "./routes/proxy";
import { serviceClients } from "./lib/httpClient";

const app = express();

app.use(express.json({ limit: "5mb" }));

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

app.get("/version", (_req, res) => {
  res.json({ version: env.SERVICE_VERSION });
});

app.use("/core", createProxyRouter(serviceClients.core));
app.use("/agents", createProxyRouter(serviceClients.agents));
app.use("/operator", createProxyRouter(serviceClients.operator));

app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error(err);
  res.status(502).json({ error: "Upstream request failed" });
});

if (process.env.NODE_ENV !== "test") {
  app.listen(env.PORT, () => {
    console.log(`Gateway listening on port ${env.PORT}`);
  });
}

export default app;
