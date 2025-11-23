import { Router } from "express";
import { ApiResponse, FinanceSnapshot } from "../types/api";

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

  return router;
}
