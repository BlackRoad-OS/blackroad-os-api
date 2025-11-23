import { Router } from "express";
import { fetchOperatorHealth } from "../clients/operatorClient";
import { ApiResponse, ServiceHealth, SystemOverview } from "../types/api";

function summarizeStatus(services: ServiceHealth[]): SystemOverview["overallStatus"] {
  if (services.some((service) => service.status === "down")) return "down";
  if (services.some((service) => service.status === "degraded")) return "degraded";
  return "healthy";
}

export function createSystemRouter() {
  const router = Router();

  router.get("/overview", async (_req, res, next) => {
    try {
      const services: ServiceHealth[] = [
        {
          id: "api",
          name: "API Gateway",
          status: "healthy",
          latencyMs: 1,
          lastChecked: new Date().toISOString(),
        },
        ...((await fetchOperatorHealth()) || []),
      ];

      const overview: SystemOverview = {
        overallStatus: summarizeStatus(services),
        services,
        jobsProcessedLast24h: 128,
        errorsLast24h: 2,
        notes: "Mocked system overview. Replace with metrics from Operator and observability stack.",
      };

      const response: ApiResponse<SystemOverview> = { ok: true, data: overview };
      res.json(response);
    } catch (err) {
      next(err);
    }
  });

  return router;
}
