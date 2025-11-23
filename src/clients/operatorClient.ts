import { getConfig } from "../config";
import { Agent, ServiceHealth } from "../types/api";
import { CashForecast, FinanceSummary } from "../types/finance";

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
