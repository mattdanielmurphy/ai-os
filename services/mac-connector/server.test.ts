import { test, expect } from "bun:test";
import { mkdtempSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { appendCheckinLog } from "./server.ts";

const vault = () => { const v = mkdtempSync(join(import.meta.dir, "..", "..", "tmp", "vault-")); mkdirSync(join(v, "habits", "logs"), { recursive: true }); return v; };
const log = (v: string) => readFileSync(join(v, "habits", "logs", "2026-10-21.md"), "utf8");

test("creates the heading in a new log", () => {
  const v = vault();
  appendCheckinLog("2026-10-21", ["Tired", "- Logic midterm"], v);
  expect(log(v)).toBe("## Morning check-in\n- Tired\n- Logic midterm\n");
});

test("adds under an existing heading, before the next section", () => {
  const v = vault();
  writeFileSync(join(v, "habits", "logs", "2026-10-21.md"), "## Morning check-in\n- one\n\n## Gratitude\n- sun\n");
  appendCheckinLog("2026-10-21", ["two"], v);
  expect(log(v)).toBe("## Morning check-in\n- one\n- two\n\n## Gratitude\n- sun\n");
});

test("appends a new section after other sections", () => {
  const v = vault();
  writeFileSync(join(v, "habits", "logs", "2026-10-21.md"), "## Gratitude\n- sun\n");
  appendCheckinLog("2026-10-21", ["hi"], v);
  expect(log(v)).toBe("## Gratitude\n- sun\n\n## Morning check-in\n- hi\n");
});

import { actToken, actRequest } from "./server.ts";
test("act token is derived, not the connector token", () => {
  expect(actToken("abc")).not.toContain("abc");
  expect(actToken("abc")).toHaveLength(32);
  expect(actToken("abc")).toBe(actToken("abc"));
});
test("review-done queues a fixed-shape note", () => {
  const ok = actRequest(new URL("https://h/act/x/review-done?page=AbC123&thread=cmsg_01XYZ"));
  expect(ok.status).toBe(200);
  expect(ok.body).toContain("artifact/AbC123");
  expect(ok.body).toContain("cmsg_01XYZ");
  expect(actRequest(new URL("https://h/act/x/review-done?page=a%20b")).status).toBe(400);
  expect(actRequest(new URL("https://h/act/x/rm-rf?page=a")).status).toBe(404);
});
test("practice-done runs the gate step, no note in the link", () => {
  const r = actRequest(new URL("https://h/act/x/practice-done"));
  expect(r.run).toBe("practice-done");
  expect(r.body).toBeUndefined();
});
