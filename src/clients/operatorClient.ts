import { getApiConfig } from "../config/env";
import { CashForecast, FinanceSummary, FinancialStatements } from "../types/finance";

export interface OperatorClient {
  getFinanceSummary(): Promise<FinanceSummary>;
  getCashForecast(): Promise<CashForecast>;
  getStatements(period: string): Promise<FinancialStatements>;
}

/**
 * HTTP client for talking to blackroad-os-operator.
 * TODO: wire to real operator endpoints when available.
 */
export class HttpOperatorClient implements OperatorClient {
  private readonly baseUrl: string;
  private readonly timeoutMs: number;

  constructor() {
    const cfg = getApiConfig();
    this.baseUrl = cfg.operatorBaseUrl;
    this.timeoutMs = cfg.requestTimeoutMs;
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

  async getStatements(period: string): Promise<FinancialStatements> {
    return this.get<FinancialStatements>(
      `/internal/finance/statements/${encodeURIComponent(period)}`
    );
  }
}
