import { Router } from "express";
import { getApiConfig } from "../config/env";

export function createHealthRouter(): Router {
  const router = Router();

  router.get("/", (_req, res) => {
    const cfg = getApiConfig();
    res.json({
      status: "ok",
      uptimeSeconds: Math.round(process.uptime()),
      env: cfg.env,
    });
  });

  return router;
}
