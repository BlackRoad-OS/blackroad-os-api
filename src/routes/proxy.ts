import { Router } from "express";
import { AxiosInstance } from "axios";
import { forwardRequest } from "../lib/httpClient";

const mapProxyHeaders = (headers: Record<string, any>) => {
  const excluded = new Set([
    "transfer-encoding",
    "content-encoding",
    "content-length",
    "connection",
  ]);

  return Object.entries(headers).reduce<Record<string, string>>((acc, [key, value]) => {
    if (!excluded.has(key.toLowerCase()) && typeof value === "string") {
      acc[key] = value;
    }
    return acc;
  }, {});
};

export const createProxyRouter = (client: AxiosInstance) => {
  const router = Router();

  router.use(async (req, res, next) => {
    try {
      const response = await forwardRequest(client, req);
      res
        .status(response.status)
        .set(mapProxyHeaders(response.headers))
        .send(response.data);
    } catch (error) {
      next(error);
    }
  });

  return router;
};
