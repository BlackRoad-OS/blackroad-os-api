import express from "express";
import cors from "cors";
import { loggingMiddleware } from "./middleware/logging";
import { errorHandler } from "./middleware/errorHandler";
import { registerRoutes } from "./routes";

export function createServer() {
  const app = express();
  app.use(cors());
  app.use(express.json());
  app.use(loggingMiddleware);
  // TODO: add rate limiting/abuse protection middleware when requirements are defined.

  registerRoutes(app);

  // TODO: add auth middleware when authN/authZ requirements are defined.
  // TODO: emit metrics/traces once observability stack is available.
  app.use(errorHandler);

  return app;
}
