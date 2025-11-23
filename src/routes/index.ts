import { Express } from "express";
import { createFinanceRouter } from "./finance";
import { createHealthRouter } from "./health";
import { createVersionRouter } from "./version";

export function registerRoutes(app: Express) {
  app.use("/health", createHealthRouter());
  app.use("/version", createVersionRouter());
  app.use("/finance", createFinanceRouter());
}
