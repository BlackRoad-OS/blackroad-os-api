export const SERVICE_ID = "api";
export const SERVICE_NAME = "BlackRoad OS – Public API";
export const SERVICE_BASE_URL =
  process.env.SERVICE_BASE_URL || "https://api.blackroad.systems";
export const OS_ROOT = process.env.OS_ROOT || "https://blackroad.systems";

export const CORE_BASE_URL =
  process.env.CORE_BASE_URL || "https://core.blackroad.systems";
export const CORE_VERIFICATION_BASE_URL =
  process.env.CORE_VERIFICATION_BASE_URL || `${CORE_BASE_URL}/internal`;
export const OPERATOR_BASE_URL =
  process.env.OPERATOR_BASE_URL || "https://operator.blackroad.systems";

export const serviceConfig = {
  SERVICE_ID,
  SERVICE_NAME,
  SERVICE_BASE_URL,
  OS_ROOT,
  CORE_BASE_URL,
  CORE_VERIFICATION_BASE_URL,
  OPERATOR_BASE_URL,
};
