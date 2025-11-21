import { Router, Request, Response } from "express";
import {
  SERVICE_ID,
  OS_ROOT,
  CORE_BASE_URL,
  OPERATOR_BASE_URL,
} from "../config/serviceConfig";

const router = Router();

router.get("/debug/env", (req: Request, res: Response) => {
  res.json({
    ok: true,
    service: SERVICE_ID,
    env: {
      NODE_ENV: process.env.NODE_ENV,
      OS_ROOT,
      LOG_LEVEL: process.env.LOG_LEVEL,
      CORE_BASE_URL,
      OPERATOR_BASE_URL,
    },
  });
});

export default router;
