import { Router, Request, Response } from "express";
import { SERVICE_ID } from "../config/serviceConfig";

const router = Router();

router.get("/health", (req: Request, res: Response) => {
  res.status(200).json({
    status: "ok",
    service: SERVICE_ID,
  });
});

export default router;
