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
