import express from "express";
import { env } from "./config/env";
import { createProxyRouter } from "./routes/proxy";
import { serviceClients } from "./lib/httpClient";
import healthRouter from "./routes/health";
import infoRouter from "./routes/info";
import versionRouter from "./routes/version";
import pingRouter from "./routes/v1/ping";
import v1HealthRouter from "./routes/v1/health";
import verificationRouter from "./routes/v1/verify";

const app = express();

app.use(express.json({ limit: "5mb" }));

// API routes
app.use(healthRouter);
app.use(infoRouter);
app.use(versionRouter);
app.use("/v1", pingRouter);
app.use("/v1", v1HealthRouter);
app.use("/v1", verificationRouter);

// Proxy routes
app.use("/core", createProxyRouter(serviceClients.core));
app.use("/agents", createProxyRouter(serviceClients.agents));
app.use("/operator", createProxyRouter(serviceClients.operator));

app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error(err);
  res.status(502).json({ error: "Upstream request failed" });
});

if (process.env.NODE_ENV !== "test") {
  app.listen(env.PORT, env.HOST, () => {
    console.log(`Gateway listening on ${env.HOST}:${env.PORT}`);
  });
}

export default app;
