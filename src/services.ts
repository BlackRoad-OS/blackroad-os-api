export type ServiceDescriptor = {
  id: string;
  name: string;
  baseUrl: string;
  healthEndpoint: string;
  infoEndpoint: string;
};

export const apiService: ServiceDescriptor = {
  id: "api",
  name: "BlackRoad OS – Public API",
  baseUrl: process.env.SERVICE_BASE_URL || "https://api.blackroad.systems",
  healthEndpoint: "/health",
  infoEndpoint: "/info",
};

export const coreService: ServiceDescriptor = {
  id: "core",
  name: "BlackRoad OS – Core",
  baseUrl: process.env.CORE_BASE_URL || "https://core.blackroad.systems",
  healthEndpoint: "/health",
  infoEndpoint: "/info",
};

export const operatorService: ServiceDescriptor = {
  id: "operator",
  name: "BlackRoad OS – Operator",
  baseUrl: process.env.OPERATOR_BASE_URL || "https://operator.blackroad.systems",
  healthEndpoint: "/health",
  infoEndpoint: "/info",
};

export const servicesRegistry = {
  api: apiService,
  core: coreService,
  operator: operatorService,
};
