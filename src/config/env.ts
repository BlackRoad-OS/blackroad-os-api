/**
 * Centralized API configuration loader.
 *
 * Values are sourced from environment variables and provide typed access for the
 * HTTP server. The operator base URL points to the blackroad-os-operator
 * service, which powers the finance agents.
 */
import dotenv from "dotenv";

dotenv.config();

export interface ApiConfig {
  /**
   * Deployment environment indicator (dev, staging, prod, test).
   */
  env: "dev" | "staging" | "prod" | "test";
  /**
   * TCP port the HTTP server should bind to.
   */
  port: number;
  /**
   * Log verbosity for request/response logging.
   */
  logLevel: "debug" | "info" | "warn" | "error";
  /**
   * Base URL for the blackroad-os-operator service that provides finance data.
   */
  operatorBaseUrl: string;
  /**
   * Timeout in milliseconds for outbound requests to upstream services.
   */
  requestTimeoutMs: number;
}

/**
 * Load and normalize API configuration from environment variables.
 */
export function getApiConfig(): ApiConfig {
  const env = (process.env.NODE_ENV as ApiConfig["env"]) || "dev";
  const port = Number.parseInt(process.env.PORT || "3001", 10);
  const logLevel =
    (process.env.LOG_LEVEL as ApiConfig["logLevel"]) || process.env.LOGLEVEL || "info";
  const operatorBaseUrl = process.env.OPERATOR_BASE_URL || "http://localhost:4000";
  const requestTimeoutMs = Number.parseInt(process.env.REQUEST_TIMEOUT_MS || "5000", 10);

  return {
    env,
    port: Number.isFinite(port) ? port : 3001,
    logLevel,
    operatorBaseUrl,
    requestTimeoutMs: Number.isFinite(requestTimeoutMs) ? requestTimeoutMs : 5000,
  };
}
