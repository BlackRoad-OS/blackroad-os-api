import { Request, Response, NextFunction } from "express";
import { SERVICE_ID } from "../config/serviceConfig";

export const loggingMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const start = process.hrtime.bigint();

  res.on("finish", () => {
    const end = process.hrtime.bigint();
    const durationMs = Number(end - start) / 1_000_000;

    const logEntry = {
      ts: new Date().toISOString(),
      method: req.method,
      path: req.originalUrl || req.url,
      status: res.statusCode,
      duration_ms: Number(durationMs.toFixed(3)),
      service_id: SERVICE_ID,
    };

    console.log(JSON.stringify(logEntry));
  });

  next();
};
