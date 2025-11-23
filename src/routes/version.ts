import { Router } from "express";
import packageInfo from "../../package.json";
import { getApiConfig } from "../config/env";

export function createVersionRouter(): Router {
  const router = Router();

  router.get("/", (_req, res) => {
    const cfg = getApiConfig();
    const payload: Record<string, unknown> = {
      version: packageInfo.version,
      env: cfg.env,
    };

    if (process.env.GIT_SHA) {
      payload.gitSha = process.env.GIT_SHA;
    }

    if (process.env.BUILD_TIME) {
      payload.buildTime = process.env.BUILD_TIME;
    }

    res.json(payload);
  });

  return router;
}
