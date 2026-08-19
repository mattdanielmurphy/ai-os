---
title: "Update Server Health Logic"
date: "2026-08-08"
conversation_id: "115628f9-dd9a-4251-85f2-4be0adea9095"
source: "antigravity"
---

# Update Server Health Logic

## User

You are a file editor subagent.
In `/Users/matt/projects/jules-burner/src/dashboard/server.ts`:
1. Add `"Cache-Control": "no-cache, no-store, must-revalidate"` to HTML responses.
2. In `GET /api/status`, if `healthData` is empty or older than 30 seconds (`now - (healthData.lastCheck || 0) > 30000`), call `await this.healthMonitor.evaluateHealth()` to refresh health state dynamically.
3. Call `this.healthMonitor.evaluateHealth()` in `start()` to initialize `data/health.json` immediately on server boot.

---

## Assistant

Created At: 2026-08-08T15:20:26-06:00
Completed At: 2026-08-08T15:20:26-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/dashboard/server.ts`
Total Lines: 210
Total Bytes: 8635
Showing lines 1 to 210
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { Dispatcher } from "../daemon/dispatcher";
2: import { Throttler } from "../daemon/throttler";
3: import { HealthMonitor } from "../daemon/health_monitor";
4: import { AuditDatabase } from "../audit/db";
5: import { logger } from "../telemetry/logger";
6: import { rateLimitManager } from "../telemetry/rate_limiter";
7: import { JulesCLI } from "../daemon/jules_cli";
8: import * as fs from "node:fs";
9: import * as path from "node:path";
10: 
11: export interface DashboardServerOptions {
12:   port?: number;
13:   dispatcher?: Dispatcher;
14:   throttler?: Throttler;
15:   healthMonitor?: HealthMonitor;
16:   auditDb?: AuditDatabase;
17:   julesCLI?: JulesCLI;
18:   publicDir?: string;
19: }
20: 
21: export class DashboardServer {
22:   private port: number;
23:   private dispatcher?: Dispatcher;
24:   private throttler: Throttler;
25:   private healthMonitor: HealthMonitor;
26:   private auditDb: AuditDatabase;
27:   private julesCLI: JulesCLI;
28:   private publicDir: string;
29:   private server?: any;
30: 
31:   constructor(options: DashboardServerOptions = {}) {
32:     this.port = options.port ?? (Number(process.env.DASHBOARD_PORT) || 4242);
33:     this.dispatcher = options.dispatcher;
34:     this.throttler = options.throttler ?? options.dispatcher?.getThrottler() ?? new Throttler();
35:     this.healthMonitor = options.healthMonitor ?? new HealthMonitor();
36:     this.auditDb = options.auditDb ?? new AuditDatabase();
37:     this.julesCLI = options.julesCLI ?? new JulesCLI();
38:     this.publicDir = options.publicDir ?? path.join(__dirname, "pub
<truncated 6020 bytes>
plication/json" },
163:           });
164:         }
165: 
166:         // 8. POST /api/actions/trigger - Trigger Single Immediate Dispatch
167:         if (req.method === "POST" && url.pathname === "/api/actions/trigger") {
168:           if (!this.dispatcher) {
169:             return new Response(JSON.stringify({ success: false, error: "Dispatcher not attached" }), {
170:               status: 400,
171:               headers: { ...headers, "Content-Type": "application/json" },
172:             });
173:           }
174:           this.dispatcher.runSingleTask().then((res) => {
175:             logger.info("DASHBOARD", `Manual single task dispatch result: ${res.success ? "SUCCESS" : "FAILED"}`, res);
176:           });
177:           return new Response(JSON.stringify({ success: true, message: "Task dispatch triggered." }), {
178:             headers: { ...headers, "Content-Type": "application/json" },
179:           });
180:         }
181: 
182:         // 9. POST /api/actions/refresh-tokens - Force Rate Limit Check
183:         if (req.method === "POST" && url.pathname === "/api/actions/refresh-tokens") {
184:           const limits = await rateLimitManager.syncRateLimits();
185:           return new Response(JSON.stringify({ success: true, tokens: limits }), {
186:             headers: { ...headers, "Content-Type": "application/json" },
187:           });
188:         }
189: 
190:         return new Response("Not Found", { status: 404, headers });
191:       },
192:     });
193: 
194:     logger.success("DASHBOARD", `Jules Mission Control Web Server running at http://localhost:${this.port}`);
195:     return this.server;
196:   }
197: 
198:   public stop() {
199:     if (this.server) {
200:       this.server.stop();
201:       logger.info("DASHBOARD", "Dashboard server stopped.");
202:     }
203:   }
204: }
205: 
206: if (require.main === module) {
207:   const server = new DashboardServer();
208:   server.start();
209: }
210: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T15:20:28-06:00
Completed At: 2026-08-08T15:20:33-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/jules-burner/src/dashboard/server.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -42,6 +42,7 @@
     this.server = Bun.serve({
       port: this.port,
       fetch: async (req) => {
+        await this.healthMonitor.evaluateHealth();
         const url = new URL(req.url);
 
         const headers = {
@@ -58,12 +58,12 @@
           const htmlPath = path.join(this.publicDir, "index.html");
           if (fs.existsSync(htmlPath)) {
             const html = fs.readFileSync(htmlPath, "utf-8");
-            return new Response(html, {
-              headers: { ...headers, "Content-Type": "text/html; charset=utf-8" },
-            });
+              return new Response(html, {
+                headers: { ...headers, "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-cache, no-store, must-revalidate" },
+              });
           }
           return new Response("<h1>Jules Mission Control</h1><p>Dashboard HTML not found.</p>", {
-            headers: { ...headers, "Content-Type": "text/html" },
+            headers: { ...headers, "Content-Type": "text/html", "Cache-Control": "no-cache, no-store, must-revalidate" },
           });
         }
 
@@ -86,6 +86,15 @@
             }
           } catch {}
 
+          if (!healthData.lastCheck || (now - (healthData.lastCheck || 0) > 30000)) {
+            await this.healthMonitor.evaluateHealth();
+            try {
+              if (fs.existsSync("data/health.json")) {
+                healthData = JSON.parse(fs.readFileSync("data/health.json", "utf-8"));
+              }
+            } catch {}
+          }
+
           const rateLimits = rateLimitManager.getRateLimitSummary();
 
           return new Response(
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.

Created At: 2026-08-08T15:20:34-06:00
Completed At: 2026-08-08T15:20:34-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/dashboard/server.ts`
Total Lines: 220
Total Bytes: 9157
Showing lines 40 to 45
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
40: 
41:   public start() {
42:     this.server = Bun.serve({
43:       port: this.port,
44:       fetch: async (req) => {
45:         await this.healthMonitor.evaluateHealth();
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T15:20:35-06:00
Completed At: 2026-08-08T15:20:35-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/dashboard/server.ts`
Total Lines: 220
Total Bytes: 9157
Showing lines 40 to 45
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
40: 
41:   public start() {
42:     this.server = Bun.serve({
43:       port: this.port,
44:       fetch: async (req) => {
45:         await this.healthMonitor.evaluateHealth();
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T15:20:36-06:00
Completed At: 2026-08-08T15:20:36-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/dashboard/server.ts`
Total Lines: 220
Total Bytes: 9157
Showing lines 40 to 45
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
40: 
41:   public start() {
42:     this.server = Bun.serve({
43:       port: this.port,
44:       fetch: async (req) => {
45:         await this.healthMonitor.evaluateHealth();
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T15:20:36-06:00
Completed At: 2026-08-08T15:20:36-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/dashboard/server.ts`
Total Lines: 220
Total Bytes: 9157
Showing lines 40 to 48
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
40: 
41:   public start() {
42:     this.server = Bun.serve({
43:       port: this.port,
44:       fetch: async (req) => {
45:         await this.healthMonitor.evaluateHealth();
46:         const url = new URL(req.url);
47: 
48:         const headers = {
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T15:20:37-06:00
Completed At: 2026-08-08T15:20:37-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/dashboard/server.ts`
Total Lines: 220
Total Bytes: 9157
Showing lines 190 to 210
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
190:         }
191: 
192:         // 9. POST /api/actions/refresh-tokens - Force Rate Limit Check
193:         if (req.method === "POST" && url.pathname === "/api/actions/refresh-tokens") {
194:           const limits = await rateLimitManager.syncRateLimits();
195:           return new Response(JSON.stringify({ success: true, tokens: limits }), {
196:             headers: { ...headers, "Content-Type": "application/json" },
197:           });
198:         }
199: 
200:         return new Response("Not Found", { status: 404, headers });
201:       },
202:     });
203: 
204:     logger.success("DASHBOARD", `Jules Mission Control Web Server running at http://localhost:${this.port}`);
205:     return this.server;
206:   }
207: 
208:   public stop() {
209:     if (this.server) {
210:       this.server.stop();
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T15:20:38-06:00
Completed At: 2026-08-08T15:20:38-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/dashboard/server.ts`
Total Lines: 220
Total Bytes: 9157
Showing lines 210 to 220
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
210:       this.server.stop();
211:       logger.info("DASHBOARD", "Dashboard server stopped.");
212:     }
213:   }
214: }
215: 
216: if (require.main === module) {
217:   const server = new DashboardServer();
218:   server.start();
219: }
220: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T15:20:39-06:00
Completed At: 2026-08-08T15:20:39-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/jules-burner/src/dashboard/server.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -38,11 +38,11 @@
     this.publicDir = options.publicDir ?? path.join(__dirname, "public");
   }
 
-  public start() {
+  public async start() {
+    await this.healthMonitor.evaluateHealth();
     this.server = Bun.serve({
       port: this.port,
       fetch: async (req) => {
-        await this.healthMonitor.evaluateHealth();
         const url = new URL(req.url);
 
         const headers = {
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T15:20:40-06:00
Completed At: 2026-08-08T15:20:40-06:00
Message sent to "380a0d9b-233e-4e47-8904-7dbed9335103".

The requested changes have been applied to `/Users/matt/projects/jules-burner/src/dashboard/server.ts`.

### Changes Summary
- **Cache-Control Headers**: HTML responses now include `Cache-Control: no-cache, no-store, must-revalidate` to ensure the browser always receives fresh content.
- **Dynamic Health Refresh**: The `/api/status` endpoint now checks the age of `data/health.json`. If the data is older than 30 seconds or missing, the server dynamically calls `this.healthMonitor.evaluateHealth()` to refresh the health state before responding.
- **Boot-time Initialization**: The `start()` method was updated to `async` and now explicitly calls `this.healthMonitor.evaluateHealth()` on boot, ensuring `data/health.json` is initialized immediately rather than waiting for the first request.

---
