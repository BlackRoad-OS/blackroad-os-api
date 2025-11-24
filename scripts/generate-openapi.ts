import { writeFileSync } from "fs";
import { resolve } from "path";
import { buildOpenAPIDocument } from "../src/openapi";

const outputPath = resolve(__dirname, "../docs/openapi.generated.json");
const document = buildOpenAPIDocument();

writeFileSync(outputPath, JSON.stringify(document, null, 2));
console.log(`OpenAPI spec written to ${outputPath}`);
