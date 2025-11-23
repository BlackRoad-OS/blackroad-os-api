import { createApp } from "./server";
import { getConfig } from "./config";

async function main() {
  const config = getConfig();
  const app = createApp();

  app.listen(config.PORT, "0.0.0.0", () => {
    console.log(`blackroad-os-api listening on port ${config.PORT} (${config.NODE_ENV})`);
  });
}

main().catch((err) => {
  console.error("Fatal error starting API:", err);
  process.exit(1);
});
