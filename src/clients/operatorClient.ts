import { getConfig } from "../config";
import { Agent, ServiceHealth } from "../types/api";
import { CashForecast, CashForecastBucket, FinanceSummary } from "../types/finance";

const MOCK_AGENTS: Agent[] = [
  {
    id: "agent-1",
    name: "Atlas",
    role: "orchestrator",
    status: "running",
    lastHeartbeat: new Date().toISOString(),
    version: "1.2.0",
    tags: ["core", "ops"],
  },
  {
    id: "agent-2",
    name: "Ledger",
    role: "finance",
    status: "idle",
    lastHeartbeat: new Date().toISOString(),
    version: "0.9.5",
    tags: ["finance", "treasury"],
  },
];

const MOCK_HEALTH: ServiceHealth[] = [
  {
    id: "operator",
    name: "Operator",
    status: "healthy",
    latencyMs: 42,
    lastChecked: new Date().toISOString(),
  },
];

const MOCK_FINANCE_SUMMARY: FinanceSummary = {
  currency: "USD",
  cashBalance: 88000,
  monthlyBurnRate: 4200,
  runwayMonths: 18,
  mrr: 12500,
  arr: 150000,
  generatedAt: new Date().toISOString(),
};

const MOCK_CASH_FORECAST_BUCKETS: CashForecastBucket[] = [
  {
    startDate: new Date().toISOString(),
    endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    netChange: -4200,
    endingBalance: 83800,
  },
  {
    startDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    endDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
    netChange: 12500,
    endingBalance: 96300,
  },
  {
    startDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
    endDate: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000).toISOString(),
    netChange: -3200,
    endingBalance: 93100,
  },
];

export async function fetchOperatorHealth(): Promise<ServiceHealth[]> {
  const { OPERATOR_API_BASE_URL } = getConfig();
  // TODO: Replace mock with real HTTP call to `${OPERATOR_API_BASE_URL}/health`.
  void OPERATOR_API_BASE_URL;
  return MOCK_HEALTH;
}

export async function fetchAgents(): Promise<Agent[]> {
  const { OPERATOR_API_BASE_URL } = getConfig();
  // TODO: Replace mock with real HTTP call to `${OPERATOR_API_BASE_URL}/agents`.
  void OPERATOR_API_BASE_URL;
  return MOCK_AGENTS;
}

export async function fetchFinanceSummary(): Promise<FinanceSummary> {
  const { OPERATOR_API_BASE_URL } = getConfig();
  // TODO: Replace mock with real HTTP call to `${OPERATOR_API_BASE_URL}/internal/finance/summary`.
  void OPERATOR_API_BASE_URL;
  return MOCK_FINANCE_SUMMARY;
}

export async function fetchCashForecast(): Promise<CashForecast> {
  const { OPERATOR_API_BASE_URL } = getConfig();
  // TODO: Replace mock with real HTTP call to `${OPERATOR_API_BASE_URL}/internal/finance/cash-forecast`.
  void OPERATOR_API_BASE_URL;
  return {
    currency: "USD",
    buckets: MOCK_CASH_FORECAST_BUCKETS,
    generatedAt: new Date().toISOString(),
  };
}

export interface OperatorClient {
  getFinanceSummary(): Promise<FinanceSummary>;
  getCashForecast(): Promise<CashForecast>;
}

/**
 * HTTP client for talking to blackroad-os-operator.
 * TODO: wire to real operator endpoints when available.
 */
export class HttpOperatorClient implements OperatorClient {
  private readonly baseUrl: string;
  private readonly timeoutMs: number;

  constructor(timeoutMs = 5000) {
    const cfg = getConfig();
    this.baseUrl = cfg.OPERATOR_API_BASE_URL;
    this.timeoutMs = timeoutMs;
  }

  private async get<T>(path: string): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const res = await fetch(`${this.baseUrl}${path}`, {
        method: "GET",
        signal: controller.signal,
        headers: {
          "content-type": "application/json",
        },
      });

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        const error = new Error(`Operator error ${res.status}: ${text}`);
        (error as any).statusCode = 502;
        throw error;
      }

      return res.json() as Promise<T>;
    } catch (err: any) {
      if (err?.name === "AbortError" || controller.signal.aborted) {
        const timeoutError = new Error("Operator request timed out");
        (timeoutError as any).statusCode = 504;
        throw timeoutError;
      }

      const error = err instanceof Error ? err : new Error("Operator request failed");
      if (!(error as any).statusCode) {
        (error as any).statusCode = 502;
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  async getFinanceSummary(): Promise<FinanceSummary> {
    return this.get<FinanceSummary>("/internal/finance/summary");
  }

  async getCashForecast(): Promise<CashForecast> {
    return this.get<CashForecast>("/internal/finance/cash-forecast");
  }
}

export async function fetchAgentById(id: string): Promise<Agent | null> {
  const agents = await fetchAgents();
  return agents.find((agent) => agent.id === id) ?? null;
}
