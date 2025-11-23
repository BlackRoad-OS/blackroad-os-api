import cors from "cors";
import express from "express";
import { errorHandler } from "./middleware/errorHandler";
import { requestLogger } from "./middleware/requestLogger";
import { createV1Router } from "./routes";

export function createApp() {
  const app = express();
  app.use(cors());
  app.use(express.json());
  app.use(requestLogger);

  app.use("/api/v1", createV1Router());

  app.use((req, res) => {
    res.status(404).json({
      ok: false,
      error: {
        code: "NOT_FOUND",
        message: `Route not found: ${req.method} ${req.originalUrl}`,
      },
    });
  });

  app.use(errorHandler);

  return app;
}
