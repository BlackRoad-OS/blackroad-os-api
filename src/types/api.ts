export type ApiSuccess<T> = {
  ok: true;
  data: T;
};

export type ApiError = {
  ok: false;
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
};

export type ApiResponse<T> = ApiSuccess<T> | ApiError;

export type ServiceHealth = {
  id: string;
  name: string;
  status: "healthy" | "degraded" | "down";
  latencyMs?: number;
  lastChecked: string;
};

export type SystemOverview = {
  overallStatus: "healthy" | "degraded" | "down";
  services: ServiceHealth[];
  jobsProcessedLast24h?: number;
  errorsLast24h?: number;
  notes?: string;
};

export type Agent = {
  id: string;
  name: string;
  role: string;
  status: "idle" | "running" | "error" | "offline";
  lastHeartbeat: string;
  version?: string;
  tags?: string[];
};

export type FinanceSnapshot = {
  timestamp: string;
  monthlyInfraCostUsd?: number;
  monthlyRevenueUsd?: number;
  estimatedSavingsUsd?: number;
  walletBalanceUsd?: number;
  notes?: string;
};

export type EventRecord = {
  id: string;
  timestamp: string;
  source: string;
  type: string;
  summary: string;
  psShaInfinity?: string;
  severity?: "info" | "warning" | "error";
};

export type RoadChainBlock = {
  height: number;
  hash: string;
  prevHash: string;
  timestamp: string;
  eventIds: string[];
};
