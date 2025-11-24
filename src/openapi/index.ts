import { OpenApiGeneratorV3, OpenAPIRegistry } from "@asteasolutions/zod-to-openapi";
import {
  ApiErrorSchema,
  agentIdParamsSchema,
  agentListQuerySchema,
  agentSchema,
  apiSuccessSchema,
  cashForecastSchema,
  eventRecordSchema,
  eventsQuerySchema,
  healthResponseSchema,
  financeSnapshotSchema,
  financeSummarySchema,
  roadChainBlockSchema,
  serviceHealthSchema,
  systemOverviewSchema,
} from "../validation/schemas";

function jsonResponse(schema: any) {
  return {
    content: {
      "application/json": {
        schema,
      },
    },
  } as const;
}

export function buildOpenAPIDocument() {
  const registry = new OpenAPIRegistry();

  const ApiError = registry.register("ApiError", ApiErrorSchema);
  const Agent = registry.register("Agent", agentSchema);
  const ServiceHealth = registry.register("ServiceHealth", serviceHealthSchema);
  const HealthResponse = registry.register("HealthResponse", healthResponseSchema);
  const SystemOverview = registry.register("SystemOverview", systemOverviewSchema);
  const FinanceSnapshot = registry.register("FinanceSnapshot", financeSnapshotSchema);
  const FinanceSummary = registry.register("FinanceSummary", financeSummarySchema);
  const CashForecast = registry.register("CashForecast", cashForecastSchema);
  const EventRecord = registry.register("EventRecord", eventRecordSchema);
  const RoadChainBlock = registry.register("RoadChainBlock", roadChainBlockSchema);

  registry.registerPath({
    method: "get",
    path: "/api/v1/health",
    description: "API and dependency health",
    tags: ["health"],
    responses: {
      200: {
        description: "Aggregated service health",
        ...jsonResponse(apiSuccessSchema(HealthResponse)),
      },
    },
  });

  registry.registerPath({
    method: "get",
    path: "/api/v1/system/overview",
    description: "System overview",
    tags: ["system"],
    responses: {
      200: {
        description: "Overall system overview",
        ...jsonResponse(apiSuccessSchema(SystemOverview)),
      },
    },
  });

  registry.registerPath({
    method: "get",
    path: "/api/v1/agents",
    description: "List agents with optional filters",
    tags: ["agents"],
    request: {
      query: agentListQuerySchema,
    },
    responses: {
      200: {
        description: "Agents matching filters",
        ...jsonResponse(apiSuccessSchema(Agent.array())),
      },
      400: {
        description: "Invalid filters",
        ...jsonResponse(ApiError),
      },
    },
  });

  registry.registerPath({
    method: "get",
    path: "/api/v1/agents/{id}",
    description: "Fetch a single agent by ID",
    tags: ["agents"],
    request: {
      params: agentIdParamsSchema,
    },
    responses: {
      200: {
        description: "Agent found",
        ...jsonResponse(apiSuccessSchema(Agent)),
      },
      404: {
        description: "Agent not found",
        ...jsonResponse(ApiError),
      },
    },
  });

  registry.registerPath({
    method: "get",
    path: "/api/v1/finance/snapshot",
    description: "Finance snapshot",
    tags: ["finance"],
    responses: {
      200: {
        description: "Finance snapshot",
        ...jsonResponse(apiSuccessSchema(FinanceSnapshot)),
      },
    },
  });

  registry.registerPath({
    method: "get",
    path: "/api/v1/finance/summary",
    description: "Finance summary",
    tags: ["finance"],
    responses: {
      200: {
        description: "Finance summary",
        ...jsonResponse(apiSuccessSchema(FinanceSummary)),
      },
    },
  });

  registry.registerPath({
    method: "get",
    path: "/api/v1/finance/cash-forecast",
    description: "Cash forecast",
    tags: ["finance"],
    responses: {
      200: {
        description: "Cash forecast",
        ...jsonResponse(apiSuccessSchema(CashForecast)),
      },
    },
  });

  registry.registerPath({
    method: "get",
    path: "/api/v1/events",
    description: "Event feed with filters",
    tags: ["events"],
    request: { query: eventsQuerySchema },
    responses: {
      200: {
        description: "Filtered events",
        ...jsonResponse(apiSuccessSchema(EventRecord.array())),
      },
      400: {
        description: "Invalid filters",
        ...jsonResponse(ApiError),
      },
    },
  });

  registry.registerPath({
    method: "get",
    path: "/api/v1/roadchain/blocks",
    description: "RoadChain block headers",
    tags: ["roadchain"],
    responses: {
      200: {
        description: "Recent blocks",
        ...jsonResponse(apiSuccessSchema(RoadChainBlock.array())),
      },
    },
  });

  const generator = new OpenApiGeneratorV3(registry.definitions);

  return generator.generateDocument({
    openapi: "3.0.3",
    info: {
      title: "BlackRoad OS API",
      version: "0.2.0",
      description: "Typed HTTP surface for BlackRoad OS",
    },
    servers: [
      { url: "http://localhost:4000", description: "Local development" },
      { url: "https://api.blackroad.systems", description: "Production" },
    ],
  });
}
