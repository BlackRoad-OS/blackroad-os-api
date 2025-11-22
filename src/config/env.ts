import dotenv from "dotenv";

dotenv.config();

const parsePort = (value: string | undefined, fallback: number): number => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

export const env = {
  PORT: parsePort(process.env.PORT, 8080),
  HOST: process.env.HOST || "0.0.0.0",
  CORE_BASE_URL: process.env.CORE_BASE_URL || "http://localhost:3001",
  AGENTS_BASE_URL: process.env.AGENTS_BASE_URL || "http://localhost:3002",
  OPERATOR_BASE_URL: process.env.OPERATOR_BASE_URL || "http://localhost:3003",
  SERVICE_VERSION:
    process.env.SERVICE_VERSION || process.env.npm_package_version || "dev",
};
