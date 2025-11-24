import { Router } from "express";
import { fetchAgentById, fetchAgents } from "../clients/operatorClient";
import { ApiRouteError } from "../middleware/errorHandler";
import { validateRequest } from "../middleware/validateRequest";
import { Agent, ApiResponse } from "../types/api";
import {
  AgentIdParams,
  AgentListQuery,
  agentIdParamsSchema,
  agentListQuerySchema,
} from "../validation/schemas";

export function createAgentsRouter() {
  const router = Router();

  router.get(
    "/",
    validateRequest({ query: agentListQuerySchema }),
    async (req, res, next) => {
      try {
        const { status, q } = req.query as AgentListQuery;
        const agents = await fetchAgents();
        const filtered = agents.filter((agent) => {
          const statusMatch = status ? agent.status === status : true;
          const query = q?.toLowerCase();
          const queryMatch = query
            ? agent.name.toLowerCase().includes(query) ||
              (agent.tags || []).some((tag) => tag.toLowerCase().includes(query))
            : true;
          return statusMatch && queryMatch;
        });

        const response: ApiResponse<Agent[]> = { ok: true, data: filtered };
        res.json(response);
      } catch (err) {
        next(err);
      }
    }
  );

  router.get(
    "/:id",
    validateRequest({ params: agentIdParamsSchema }),
    async (req, res, next) => {
      try {
        const { id } = req.params as AgentIdParams;
        const agent = await fetchAgentById(id);
        if (!agent) {
          const error: ApiRouteError = new Error("Agent not found");
          error.statusCode = 404;
          error.code = "AGENT_NOT_FOUND";
          throw error;
        }

        const response: ApiResponse<Agent> = { ok: true, data: agent };
        res.json(response);
      } catch (err) {
        next(err);
      }
    }
  );

  return router;
}
