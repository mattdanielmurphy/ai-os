import { getOrGenerateToken, validateRequestToken } from "./auth.js";
import { createBridgeServer } from "./server.js";

const rootDir = process.env.BRIDGE_ROOT || process.cwd();
const port = parseInt(process.env.PORT || "10000", 10);
const token = getOrGenerateToken();

const handler = createBridgeServer(rootDir, token, validateRequestToken);

Bun.serve({
  port,
  fetch: handler.fetch
});

console.log(`\n==================================================`);
console.log(`🚀 Live Codebase Context Bridge for Perplexity running!`);
console.log(` Root Directory : ${rootDir}`);
console.log(` Local URL      : http://localhost:${port}/?token=${token}`);
console.log(` Manifest URL   : http://localhost:${port}/manifest?token=${token}`);
console.log(`\n Access Token   : ${token}`);
console.log(`==================================================\n`);
