import { Router, Request, Response } from "express";
import packageInfo from "../../package.json";
import { SERVICE_ID, SERVICE_NAME } from "../config/serviceConfig";

const router = Router();

router.get("/info", (req: Request, res: Response) => {
  res.json({
    name: SERVICE_NAME,
    id: SERVICE_ID,
    version: packageInfo.version,
    time: new Date().toISOString(),
    env: process.env.NODE_ENV || "development",
  });
});

export default router;
