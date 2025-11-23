import { Router } from "express";
import { ApiResponse, EventRecord } from "../types/api";

const MOCK_EVENTS: EventRecord[] = [
  {
    id: "evt-001",
    timestamp: new Date().toISOString(),
    source: "operator",
    type: "job.started",
    summary: "Orchestrator kicked off batch",
    severity: "info",
  },
  {
    id: "evt-002",
    timestamp: new Date(Date.now() - 60000).toISOString(),
    source: "core",
    type: "ledger.append",
    summary: "RoadChain journal entry committed",
    psShaInfinity: "ps-sha-∞-example",
    severity: "warning",
  },
  {
    id: "evt-003",
    timestamp: new Date(Date.now() - 120000).toISOString(),
    source: "finance",
    type: "forecast.updated",
    summary: "Finance snapshot refreshed",
    severity: "info",
  },
];

export function createEventsRouter() {
  const router = Router();

  router.get("/", (req, res) => {
    const { limit = "50", severity, source } = req.query;
    const parsedLimit = Math.max(1, Math.min(Number(limit) || 50, 200));
    const filtered = MOCK_EVENTS.filter((event) => {
      const severityMatch = severity ? event.severity === severity : true;
      const sourceMatch = source ? event.source === source : true;
      return severityMatch && sourceMatch;
    }).slice(0, parsedLimit);

    const response: ApiResponse<EventRecord[]> = { ok: true, data: filtered };
    res.json(response);
  });

  return router;
}
