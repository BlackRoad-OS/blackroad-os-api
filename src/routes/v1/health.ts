import { Router, Request, Response } from "express";
import { SERVICE_ID } from "../../config/serviceConfig";

const router = Router();

router.get("/health", (req: Request, res: Response) => {
  res.json({
    ok: true,
    service: SERVICE_ID,
    ts: new Date().toISOString(),
  });
});

export default router;
