import { extendZodWithOpenApi } from "@asteasolutions/zod-to-openapi";
import { z } from "zod";

extendZodWithOpenApi(z);

export const ApiErrorSchema = z.object({
  ok: z.literal(false),
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.unknown().optional(),
  }),
});

export const apiSuccessSchema = <T extends z.ZodTypeAny>(schema: T) =>
  z.object({
    ok: z.literal(true),
    data: schema,
  });

export const serviceHealthSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: z.enum(["healthy", "degraded", "down"]),
  latencyMs: z.number().optional(),
  lastChecked: z.string(),
});

export const healthResponseSchema = z.object({
  overallStatus: z.enum(["healthy", "degraded", "down"]),
  services: z.array(serviceHealthSchema),
});

export const systemOverviewSchema = z.object({
  overallStatus: z.enum(["healthy", "degraded", "down"]),
  services: z.array(serviceHealthSchema),
  jobsProcessedLast24h: z.number().optional(),
  errorsLast24h: z.number().optional(),
  notes: z.string().optional(),
});

export const agentStatusSchema = z.enum(["idle", "running", "error", "offline"]);

export const agentSchema = z.object({
  id: z.string(),
  name: z.string(),
  role: z.string(),
  status: agentStatusSchema,
  lastHeartbeat: z.string(),
  version: z.string().optional(),
  tags: z.array(z.string()).optional(),
});

export const agentListQuerySchema = z
  .object({
    status: agentStatusSchema.optional(),
    q: z
      .string()
      .trim()
      .min(1, "Query must be at least 1 character")
      .max(120, "Query must be 120 characters or fewer")
      .optional(),
  })
  .strict();

export const agentIdParamsSchema = z.object({
  id: z.string().trim().min(1, "Agent id cannot be empty"),
});

export const financeSnapshotSchema = z.object({
  timestamp: z.string(),
  monthlyInfraCostUsd: z.number().optional(),
  monthlyRevenueUsd: z.number().optional(),
  estimatedSavingsUsd: z.number().optional(),
  walletBalanceUsd: z.number().optional(),
  notes: z.string().optional(),
});

export const financeSummarySchema = z.object({
  currency: z.string(),
  cashBalance: z.number(),
  monthlyBurnRate: z.number(),
  runwayMonths: z.number(),
  mrr: z.number().optional(),
  arr: z.number().optional(),
  generatedAt: z.string(),
});

export const cashForecastBucketSchema = z.object({
  startDate: z.string(),
  endDate: z.string(),
  netChange: z.number(),
  endingBalance: z.number(),
});

export const cashForecastSchema = z.object({
  currency: z.string(),
  buckets: z.array(cashForecastBucketSchema),
  generatedAt: z.string(),
});

export const eventSeveritySchema = z.enum(["info", "warning", "error"]);

export const eventRecordSchema = z.object({
  id: z.string(),
  timestamp: z.string(),
  source: z.string(),
  type: z.string(),
  summary: z.string(),
  psShaInfinity: z.string().optional(),
  severity: eventSeveritySchema.optional(),
});

export const eventsQuerySchema = z
  .object({
    limit: z.coerce.number().int().min(1).max(200).default(50),
    severity: eventSeveritySchema.optional(),
    source: z
      .string()
      .trim()
      .min(1, "Source must be at least 1 character")
      .max(64, "Source must be 64 characters or fewer")
      .optional(),
  })
  .strict();

export const roadChainBlockSchema = z.object({
  height: z.number(),
  hash: z.string(),
  prevHash: z.string(),
  timestamp: z.string(),
  eventIds: z.array(z.string()),
});

export type AgentListQuery = z.infer<typeof agentListQuerySchema>;
export type AgentIdParams = z.infer<typeof agentIdParamsSchema>;
export type EventsQuery = z.infer<typeof eventsQuerySchema>;
