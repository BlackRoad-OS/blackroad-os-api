import { randomUUID } from "crypto";
import { NextFunction, Request, Response } from "express";
import { getApiConfig } from "../config/env";

/**
 * Basic request logger that also ensures every request has a request ID.
 * A structured logger can replace the console usage in the future.
 */
export function loggingMiddleware(req: Request, res: Response, next: NextFunction) {
  const start = Date.now();
  const cfg = getApiConfig();
  const requestId = req.headers["x-request-id"] || randomUUID();

  (req as any).requestId = requestId;
  res.setHeader("x-request-id", String(requestId));

  res.on("finish", () => {
    const duration = Date.now() - start;
    const message = `${req.method} ${req.originalUrl} ${res.statusCode} - ${duration}ms`;
    console.log(`[${requestId}] ${cfg.logLevel.toUpperCase()} ${message}`);
  });

  next();
}
