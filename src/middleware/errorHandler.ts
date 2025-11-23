import { NextFunction, Request, Response } from "express";

export interface ApiError extends Error {
  statusCode?: number;
  details?: unknown;
}

/**
 * Express error handler that ensures consistent JSON error responses.
 */
export function errorHandler(err: ApiError, req: Request, res: Response, _next: NextFunction) {
  const statusCode = err.statusCode || 500;
  const requestId = (req as any).requestId;
  // TODO: formalize error code taxonomy and mapping from upstream services.

  const payload = {
    error: {
      message: statusCode === 500 ? "Internal server error" : err.message,
      statusCode,
      requestId,
      details: statusCode === 500 ? undefined : err.details,
    },
  };

  console.error(`[${requestId || "unknown"}]`, err);

  res.status(statusCode).json(payload);
}
