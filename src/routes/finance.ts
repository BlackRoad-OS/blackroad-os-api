import { Router } from "express";
import { fetchCashForecast, fetchFinanceSummary } from "../clients/operatorClient";
import { ApiResponse, FinanceSnapshot } from "../types/api";
import { CashForecast, FinanceSummary } from "../types/finance";

function buildMockFinanceSnapshot(): FinanceSnapshot {
  const now = new Date().toISOString();
  return {
    timestamp: now,
    monthlyInfraCostUsd: 4200,
    monthlyRevenueUsd: 12500,
    estimatedSavingsUsd: 3100,
    walletBalanceUsd: 88000,
    notes: "Mock finance snapshot. Wire to real treasury metrics in operator/core.",
  };
}

export function createFinanceRouter() {
  const router = Router();

  router.get("/snapshot", (_req, res) => {
    const response: ApiResponse<FinanceSnapshot> = {
      ok: true,
      data: buildMockFinanceSnapshot(),
    };

    res.json(response);
  });

  router.get("/summary", async (_req, res, next) => {
    try {
      const summary = await fetchFinanceSummary();
      const response: ApiResponse<FinanceSummary> = { ok: true, data: summary };
      res.json(response);
    } catch (err) {
      next(err);
    }
  });

  router.get("/cash-forecast", async (_req, res, next) => {
    try {
      const forecast = await fetchCashForecast();
      const response: ApiResponse<CashForecast> = { ok: true, data: forecast };
      res.json(response);
    } catch (err) {
      next(err);
    }
  });

  return router;
}
