import { Request, Response, NextFunction } from "express";
import { SERVICE_ID } from "../config/serviceConfig";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const status = res.statusCode >= 400 ? res.statusCode : 500;

  if (process.env.NODE_ENV !== "test") {
    console.error(err);
  }

  res.status(status).json({
    ok: false,
    error: err.message || "Internal Server Error",
    service: SERVICE_ID,
  });
};
