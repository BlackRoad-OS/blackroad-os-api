import { randomUUID } from "crypto";
import { NextFunction, Request, Response } from "express";
import { getConfig } from "../config";

export function requestLogger(req: Request, res: Response, next: NextFunction) {
  const start = Date.now();
  const { LOG_LEVEL } = getConfig();
  const requestId = (req.headers["x-request-id"] as string) || randomUUID();

  (req as any).requestId = requestId;
  res.setHeader("x-request-id", String(requestId));

  res.on("finish", () => {
    const duration = Date.now() - start;
    const message = `${req.method} ${req.originalUrl} ${res.statusCode} - ${duration}ms`;
    console.log(`[${requestId}] ${LOG_LEVEL.toUpperCase()} ${message}`);
  });

  next();
}
