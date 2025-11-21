import axios, { AxiosInstance, AxiosRequestConfig, Method } from "axios";
import type { Request } from "express";
import { env } from "../config/env";

type TargetService = "core" | "agents" | "operator";

const DEFAULT_TIMEOUT_MS = 15_000;

const createClient = (baseURL: string): AxiosInstance =>
  axios.create({
    baseURL,
    timeout: DEFAULT_TIMEOUT_MS,
  });

export const serviceClients: Record<TargetService, AxiosInstance> = {
  core: createClient(env.CORE_BASE_URL),
  agents: createClient(env.AGENTS_BASE_URL),
  operator: createClient(env.OPERATOR_BASE_URL),
};

export const forwardRequest = async (
  client: AxiosInstance,
  req: Request
) => {
  const method = req.method.toUpperCase() as Method;
  const config: AxiosRequestConfig = {
    url: req.originalUrl.replace(/^\/[a-z]+/, ""),
    method,
    params: req.query,
    data: req.body,
    headers: {
      ...req.headers,
      host: undefined,
      connection: undefined,
      "content-length": undefined,
    },
    responseType: "arraybuffer",
    validateStatus: () => true,
  };

  return client.request(config);
};
