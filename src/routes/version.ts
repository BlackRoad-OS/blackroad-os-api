import { Router, Request, Response } from "express";
import packageInfo from "../../package.json";
import { SERVICE_ID } from "../config/serviceConfig";

const router = Router();

router.get("/version", (req: Request, res: Response) => {
  res.json({
    version: packageInfo.version,
    service: SERVICE_ID,
  });
});

export default router;
