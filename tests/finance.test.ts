import express from "express";
import request from "supertest";
import { createFinanceRouter } from "../src/routes/finance";
import { errorHandler } from "../src/middleware/errorHandler";
import { OperatorClient } from "../src/clients/operatorClient";
import { CashForecast, FinanceSummary, FinancialStatements } from "../src/types/finance";

describe("finance routes", () => {
  let app: express.Express;
  let operatorClient: jest.Mocked<OperatorClient>;

  const summaryFixture: FinanceSummary = {
    currency: "USD",
    cashBalance: 100000,
    monthlyBurnRate: 20000,
    runwayMonths: 5,
    mrr: 50000,
    arr: 600000,
    generatedAt: new Date().toISOString(),
  };

  const forecastFixture: CashForecast = {
    currency: "USD",
    generatedAt: new Date().toISOString(),
    buckets: [
      { startDate: "2024-01-01", endDate: "2024-01-31", netChange: -10000, endingBalance: 90000 },
    ],
  };

  const statementsFixture: FinancialStatements = {
    period: "2024-Q1",
    incomeStatement: {
      period: "2024-Q1",
      currency: "USD",
      revenue: [{ account: "4000", label: "Revenue", amount: 150000 }],
      cogs: [{ account: "5000", label: "COGS", amount: 50000 }],
      operatingExpenses: [{ account: "6000", label: "Opex", amount: 75000 }],
      otherIncomeExpenses: [],
      netIncome: 25000,
    },
    balanceSheet: {
      period: "2024-Q1",
      currency: "USD",
      assets: [{ account: "1000", label: "Cash", amount: 100000 }],
      liabilities: [{ account: "2000", label: "AP", amount: 30000 }],
      equity: [{ account: "3000", label: "Equity", amount: 70000 }],
    },
    cashFlowStatement: {
      period: "2024-Q1",
      currency: "USD",
      operatingActivities: [{ account: "7000", label: "Ops", amount: 20000 }],
      investingActivities: [],
      financingActivities: [],
      netChangeInCash: 20000,
    },
  };

  beforeEach(() => {
    operatorClient = {
      getFinanceSummary: jest.fn().mockResolvedValue(summaryFixture),
      getCashForecast: jest.fn().mockResolvedValue(forecastFixture),
      getStatements: jest.fn().mockResolvedValue(statementsFixture),
    };

    app = express();
    app.use(express.json());
    app.use("/finance", createFinanceRouter(operatorClient));
    app.use(errorHandler);
  });

  it("returns finance summary", async () => {
    const res = await request(app).get("/finance/summary").expect(200);

    expect(res.body.data).toEqual(summaryFixture);
    expect(operatorClient.getFinanceSummary).toHaveBeenCalledTimes(1);
  });

  it("returns cash forecast", async () => {
    const res = await request(app).get("/finance/cash-forecast").expect(200);

    expect(res.body.data).toEqual(forecastFixture);
    expect(operatorClient.getCashForecast).toHaveBeenCalledTimes(1);
  });

  it("returns statements for valid period", async () => {
    const res = await request(app).get("/finance/statements/2024-Q1").expect(200);

    expect(res.body.data).toEqual(statementsFixture);
    expect(operatorClient.getStatements).toHaveBeenCalledWith("2024-Q1");
  });

  it("rejects invalid period", async () => {
    const res = await request(app).get("/finance/statements/2024-13").expect(400);

    expect(res.body.error.message).toContain("Invalid period format");
    expect(operatorClient.getStatements).not.toHaveBeenCalled();
  });

  it("propagates upstream errors", async () => {
    operatorClient.getFinanceSummary.mockRejectedValueOnce(new Error("boom"));

    const res = await request(app).get("/finance/summary").expect(500);

    expect(res.body.error.message).toBe("Internal server error");
  });
});
