import { Router, Request, Response } from "express";
import packageInfo from "../../package.json";
import {
  SERVICE_ID,
  SERVICE_NAME,
  SERVICE_BASE_URL,
  OS_ROOT,
} from "../config/serviceConfig";

const router = Router();

router.get("/info", (req: Request, res: Response) => {
  res.json({
    name: SERVICE_NAME,
    id: SERVICE_ID,
    baseUrl: SERVICE_BASE_URL,
    version: packageInfo.version,
    osRoot: OS_ROOT,
    time: new Date().toISOString(),
  });
});

export default router;
