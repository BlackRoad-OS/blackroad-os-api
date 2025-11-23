import dotenv from "dotenv";

dotenv.config();

type NodeEnv = "development" | "test" | "production";

export type AppConfig = {
  NODE_ENV: NodeEnv;
  PORT: number;
  LOG_LEVEL: string;
  OPERATOR_API_BASE_URL: string;
  ROADCHAIN_BASE_URL?: string;
};

function parseNumber(value: string | undefined, fallback: number): number {
  const parsed = Number.parseInt(value ?? "", 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function getConfig(): AppConfig {
  const NODE_ENV = (process.env.NODE_ENV as NodeEnv) || "development";
  const PORT = parseNumber(process.env.PORT, 4000);
  const LOG_LEVEL = process.env.LOG_LEVEL || process.env.LOGLEVEL || "info";
  const OPERATOR_API_BASE_URL =
    process.env.OPERATOR_API_BASE_URL || "http://localhost:4100";
  const ROADCHAIN_BASE_URL = process.env.ROADCHAIN_BASE_URL;

  if (NODE_ENV === "production" && !process.env.OPERATOR_API_BASE_URL) {
    throw new Error("OPERATOR_API_BASE_URL is required in production");
  }

  return {
    NODE_ENV,
    PORT,
    LOG_LEVEL,
    OPERATOR_API_BASE_URL,
    ROADCHAIN_BASE_URL,
  };
}
