import { Router } from "express";
import { fetchRoadChainBlocks } from "../clients/roadchainClient";
import { ApiResponse, RoadChainBlock } from "../types/api";

export function createRoadchainRouter() {
  const router = Router();

  router.get("/blocks", async (_req, res, next) => {
    try {
      const blocks = await fetchRoadChainBlocks();
      const response: ApiResponse<RoadChainBlock[]> = { ok: true, data: blocks };
      res.json(response);
    } catch (err) {
      next(err);
    }
  });

  return router;
}
