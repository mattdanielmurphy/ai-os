---
title: "Update Daemon Test Configuration"
date: "2026-08-07"
conversation_id: "d57f150f-53cd-4c40-99bf-4b3a5855f32f"
source: "antigravity"
---

# Update Daemon Test Configuration

## User

In `/Users/matt/projects/jules-burner/tests/daemon/daemon.test.ts`, update `beforeEach` so it also unlinks `TEST_STATE_PATH` before each test, or ensure test 2 uses a fresh state file (e.g. `TEST_STATE_PATH_2 = "./tmp/test-state-2.json"`).

Please make this edit directly using replace_file_content.

---

## Assistant

Created At: 2026-08-07T12:19:11-06:00
Completed At: 2026-08-07T12:19:11-06:00
File Path: `file:///Users/matt/projects/jules-burner/tests/daemon/daemon.test.ts`
Total Lines: 224
Total Bytes: 7345
Showing lines 1 to 224
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { describe, test, expect, beforeEach, afterEach } from "bun:test";
2: import { Throttler } from "../../src/daemon/throttler";
3: import { JulesCLI } from "../../src/daemon/jules_cli";
4: import { PromptPackager } from "../../src/daemon/prompter";
5: import { Dispatcher } from "../../src/daemon/dispatcher";
6: import type { TaskCandidate } from "../../src/discovery/types";
7: import * as fs from "node:fs";
8: import * as path from "node:path";
9: 
10: const TEST_STATE_PATH = "./tmp/test-state.json";
11: const TEST_PROMPTS_DIR = "./tmp/test-prompts";
12: 
13: describe("Jules Dispatch Daemon & Throttler Suite", () => {
14:   beforeEach(() => {
15:     if (fs.existsSync(TEST_STATE_PATH)) {
16:       fs.unlinkSync(TEST_STATE_PATH);
17:     }
18:     if (fs.existsSync(TEST_PROMPTS_DIR)) {
19:       fs.rmSync(TEST_PROMPTS_DIR, { recursive: true, force: true });
20:     }
21:   });
22: 
23:   afterEach(() => {
24:     if (fs.existsSync(TEST_STATE_PATH)) {
25:       fs.unlinkSync(TEST_STATE_PATH);
26:     }
27:     if (fs.existsSync(TEST_PROMPTS_DIR)) {
28:       fs.rmSync(TEST_PROMPTS_DIR, { recursive: true, force: true });
29:     }
30:   });
31: 
32:   describe("Throttler", () => {
33:     test("tracks daily task quota and dispatches correctly", () => {
34:       const throttler = new Throttler({
35:         stateFilePath: TEST_STATE_PATH,
36:         dailyLimit: 3,
37:       });
38: 
39:       expect(throttler.canDispatch()).toBe(true);
40:       expect(throttler.getRemainingQuota()).toBe(3);
41: 
42:       throttler.recordDispatch("sess_1", "task_1");
43: 
<truncated 4804 bytes>
tterMs).toBeLessThanOrEqual(15000);
164:       }
165: 
166:       // Quota decremented by 5
167:       expect(throttler.getDispatchedCount()).toBe(5);
168:       expect(throttler.getRemainingQuota()).toBe(95);
169:     });
170: 
171:     test("halts dispatching when 100/day limit is reached", async () => {
172:       const mockExecutor = async (args: string[]) => ({
173:         exitCode: 0,
174:         stdout: "Session created. Session ID: sess_ok",
175:         stderr: "",
176:       });
177: 
178:       const throttler = new Throttler({
179:         stateFilePath: TEST_STATE_PATH,
180:         dailyLimit: 2,
181:       });
182: 
183:       const julesCLI = new JulesCLI({ executor: mockExecutor });
184:       const prompter = new PromptPackager(TEST_PROMPTS_DIR);
185: 
186:       const dispatcher = new Dispatcher({
187:         throttler,
188:         julesCLI,
189:         prompter,
190:         enableSleep: false,
191:       });
192: 
193:       const res1 = await dispatcher.runSingleTask({
194:         id: "t1",
195:         source: "self",
196:         title: "Task 1",
197:         description: "Task 1 description",
198:         complexity: "low",
199:       });
200:       expect(res1.success).toBe(true);
201: 
202:       const res2 = await dispatcher.runSingleTask({
203:         id: "t2",
204:         source: "self",
205:         title: "Task 2",
206:         description: "Task 2 description",
207:         complexity: "low",
208:       });
209:       expect(res2.success).toBe(true);
210: 
211:       // Third task should fail due to quota
212:       const res3 = await dispatcher.runSingleTask({
213:         id: "t3",
214:         source: "self",
215:         title: "Task 3",
216:         description: "Task 3 description",
217:         complexity: "low",
218:       });
219:       expect(res3.success).toBe(false);
220:       expect(res3.reason).toContain("Daily task quota limit reached");
221:     });
222:   });
223: });
224: 
The above content shows the entire, complete file contents of the requested file.

---
