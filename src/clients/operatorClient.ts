import { getConfig } from "../config";
import { Agent, ServiceHealth } from "../types/api";

const MOCK_AGENTS: Agent[] = [
  {
    id: "agent-1",
    name: "Atlas",
    role: "orchestrator",
    status: "running",
    lastHeartbeat: new Date().toISOString(),
    version: "1.2.0",
    tags: ["core", "ops"],
  },
  {
    id: "agent-2",
    name: "Ledger",
    role: "finance",
    status: "idle",
    lastHeartbeat: new Date().toISOString(),
    version: "0.9.5",
    tags: ["finance", "treasury"],
  },
];

const MOCK_HEALTH: ServiceHealth[] = [
  {
    id: "operator",
    name: "Operator",
    status: "healthy",
    latencyMs: 42,
    lastChecked: new Date().toISOString(),
  },
];

export async function fetchOperatorHealth(): Promise<ServiceHealth[]> {
  const { OPERATOR_API_BASE_URL } = getConfig();
  // TODO: Replace mock with real HTTP call to `${OPERATOR_API_BASE_URL}/health`.
  void OPERATOR_API_BASE_URL;
  return MOCK_HEALTH;
}

export async function fetchAgents(): Promise<Agent[]> {
  const { OPERATOR_API_BASE_URL } = getConfig();
  // TODO: Replace mock with real HTTP call to `${OPERATOR_API_BASE_URL}/agents`.
  void OPERATOR_API_BASE_URL;
  return MOCK_AGENTS;
}

export async function fetchAgentById(id: string): Promise<Agent | null> {
  const agents = await fetchAgents();
  return agents.find((agent) => agent.id === id) ?? null;
}
