import { createServer } from "./server";
import { getApiConfig } from "./config/env";

async function main() {
  const cfg = getApiConfig();
  const app = createServer();

  app.listen(cfg.port, "0.0.0.0", () => {
    console.log(`blackroad-os-api listening on port ${cfg.port} (${cfg.env})`);
  });
}

main().catch((err) => {
  console.error("Fatal error starting API:", err);
  process.exit(1);
});
