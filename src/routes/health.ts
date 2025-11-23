import { Router } from "express";

const api = Router();

api.get("/api/health", (_req, res) => {
  res.status(200).json({ status: "ok", service: "blackroad-os-api" });
});

export default api;
