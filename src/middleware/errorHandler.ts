import { NextFunction, Request, Response } from "express";
import { getConfig } from "../config";

export interface ApiRouteError extends Error {
  statusCode?: number;
  code?: string;
  details?: unknown;
}

export function errorHandler(
  err: ApiRouteError,
  req: Request,
  res: Response,
  _next: NextFunction
) {
  const { NODE_ENV } = getConfig();
  const statusCode = err.statusCode || 500;
  const code = err.code || (statusCode >= 500 ? "INTERNAL_SERVER_ERROR" : "BAD_REQUEST");
  const requestId = (req as any).requestId;

  if (statusCode >= 500) {
    console.error(`[${requestId || "unknown"}]`, err);
  }

  res.status(statusCode).json({
    ok: false,
    error: {
      code,
      message: statusCode >= 500 ? "Internal server error" : err.message,
      details: NODE_ENV === "development" || NODE_ENV === "test" ? err.details ?? err.stack : undefined,
    },
  });
}
