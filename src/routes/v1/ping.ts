import { Router, Request, Response } from "express";
import { SERVICE_ID, SERVICE_NAME } from "../../config/serviceConfig";

const router = Router();

router.get("/ping", (req: Request, res: Response) => {
  res.json({
    ok: true,
    api: SERVICE_NAME,
    service: SERVICE_ID,
    ts: new Date().toISOString(),
  });
});

export default router;
