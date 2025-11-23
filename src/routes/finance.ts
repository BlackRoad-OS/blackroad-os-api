import { Router } from "express";
import { HttpOperatorClient, OperatorClient } from "../clients/operatorClient";
import { ApiError } from "../middleware/errorHandler";

const PERIOD_REGEX = /^(\d{4}-(0[1-9]|1[0-2])|\d{4}-Q[1-4])$/;

export function createFinanceRouter(operatorClient: OperatorClient = new HttpOperatorClient()): Router {
  const router = Router();

  router.get("/summary", async (_req, res, next) => {
    try {
      const summary = await operatorClient.getFinanceSummary();
      res.json({ data: summary });
    } catch (err) {
      next(err);
    }
  });

  router.get("/cash-forecast", async (_req, res, next) => {
    try {
      const forecast = await operatorClient.getCashForecast();
      res.json({ data: forecast });
    } catch (err) {
      next(err);
    }
  });

  router.get("/statements/:period", async (req, res, next) => {
    try {
      const { period } = req.params;
      if (!PERIOD_REGEX.test(period)) {
        const error: ApiError = new Error(
          "Invalid period format. Use YYYY-MM or YYYY-Q{1-4}."
        );
        error.statusCode = 400;
        throw error;
      }

      const statements = await operatorClient.getStatements(period);
      res.json({ data: statements });
    } catch (err) {
      next(err);
    }
  });

  return router;
}
