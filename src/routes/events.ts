import { Router } from "express";
import { validateRequest } from "../middleware/validateRequest";
import { ApiResponse, EventRecord } from "../types/api";
import { EventsQuery, eventsQuerySchema } from "../validation/schemas";

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

  router.get(
    "/",
    validateRequest({ query: eventsQuerySchema }),
    (req, res) => {
      const { limit, severity, source } = req.query as unknown as EventsQuery;
      const filtered = MOCK_EVENTS.filter((event) => {
        const severityMatch = severity ? event.severity === severity : true;
        const sourceMatch = source ? event.source === source : true;
        return severityMatch && sourceMatch;
      }).slice(0, limit ?? 50);

      const response: ApiResponse<EventRecord[]> = { ok: true, data: filtered };
      res.json(response);
    }
  );

  return router;
}
