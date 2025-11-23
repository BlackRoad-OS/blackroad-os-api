import { Router } from "express";
import { createAgentsRouter } from "./agents";
import { createEventsRouter } from "./events";
import { createFinanceRouter } from "./finance";
import { createHealthRouter } from "./health";
import { createRoadchainRouter } from "./roadchain";
import { createSystemRouter } from "./system";

export function createV1Router() {
  const router = Router();

  router.use("/health", createHealthRouter());
  router.use("/system", createSystemRouter());
  router.use("/agents", createAgentsRouter());
  router.use("/finance", createFinanceRouter());
  router.use("/events", createEventsRouter());
  router.use("/roadchain", createRoadchainRouter());

  return router;
}
