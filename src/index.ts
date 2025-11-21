import express from "express";
import cors from "cors";
import healthRouter from "./routes/health";
import infoRouter from "./routes/info";
import versionRouter from "./routes/version";
import debugEnvRouter from "./routes/debugEnv";
import v1PingRouter from "./routes/v1/ping";
import { loggingMiddleware } from "./middleware/logging";
import { errorHandler } from "./middleware/errorHandler";
import { SERVICE_ID } from "./config/serviceConfig";

const app = express();

app.use(cors());
app.use(express.json());
app.use(loggingMiddleware);

app.use(healthRouter);
app.use(infoRouter);
app.use(versionRouter);
app.use(debugEnvRouter);
app.use("/v1", v1PingRouter);

app.use(errorHandler);

const PORT = process.env.PORT ? Number(process.env.PORT) : 8080;

if (process.env.NODE_ENV !== "test") {
  app.listen(PORT, () => {
    console.log(
      JSON.stringify({
        ts: new Date().toISOString(),
        message: `Service ${SERVICE_ID} listening on port ${PORT}`,
      })
    );
  });
}

export default app;
