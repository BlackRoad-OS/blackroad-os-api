import { Router } from "express";
import { fetchAgentById, fetchAgents } from "../clients/operatorClient";
import { ApiRouteError } from "../middleware/errorHandler";
import { Agent, ApiResponse } from "../types/api";

export function createAgentsRouter() {
  const router = Router();

  router.get("/", async (req, res, next) => {
    try {
      const { status, q } = req.query;
      const agents = await fetchAgents();
      const filtered = agents.filter((agent) => {
        const statusMatch = status ? agent.status === status : true;
        const query = (q as string | undefined)?.toLowerCase();
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
  });

  router.get("/:id", async (req, res, next) => {
    try {
      const agent = await fetchAgentById(req.params.id);
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
  });

  return router;
}
