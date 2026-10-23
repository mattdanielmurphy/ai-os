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

import { noteCall, takeDraft, readDraft, flushStaleDraft, DRAFT_IDLE_MS } from "./server.ts";
const tmpDirs = () => { const r = mkdtempSync(join(import.meta.dir, "..", "..", "tmp", "draft-")); return { dir: join(r, "state"), calls: join(r, "calls") }; };
test("note_call builds one live note per call and dedupes", () => {
  const { dir, calls } = tmpDirs();
  const t = Date.UTC(2026, 9, 22, 20, 0);
  noteCall({ todos: ["Call dentist Monday"], said: "I need the dentist" }, t, dir, calls);
  const d = noteCall({ todos: ["Call dentist Monday"], facts: ["Plays pickleball"] }, t + 60_000, dir, calls);
  expect(d.todos).toEqual(["Call dentist Monday"]);
  expect(d.facts).toEqual(["Plays pickleball"]);
  const note = readFileSync(join(calls, d.file), "utf8");
  expect(note).toContain("- Call dentist Monday");
  expect(note).toContain("I need the dentist");
  // a note long after the last one starts a new call
  expect(noteCall({ said: "hi" }, t + 60_000 + DRAFT_IDLE_MS + 1, dir, calls).started).not.toBe(d.started);
});
test("takeDraft closes the draft", () => {
  const { dir, calls } = tmpDirs();
  noteCall({ said: "x" }, Date.now(), dir, calls);
  expect(takeDraft(dir)?.said).toEqual(["x"]);
  expect(readDraft(dir)).toBeNull();
});
test("a quiet draft goes to the coordinator and pulls the transcript, once", () => {
  const { dir, calls } = tmpDirs();
  const t = Date.now();
  const d = noteCall({ todos: ["Buy paddles"] }, t, dir, calls);
  const sent: string[] = []; let pulls = 0;
  const q = (title: string, body: string) => { sent.push(body); };
  expect(flushStaleDraft(t + 60_000, dir, calls, q, () => pulls++)).toBe(false);
  expect(flushStaleDraft(t + DRAFT_IDLE_MS + 1, dir, calls, q, () => pulls++)).toBe(true);
  expect(sent[0]).toContain("- Buy paddles");
  expect(pulls).toBe(1);
  expect(readFileSync(join(calls, d.file), "utf8")).toContain("Ended without save_call");
  expect(flushStaleDraft(t + 2 * DRAFT_IDLE_MS, dir, calls, q, () => pulls++)).toBe(false);
});

import { overlayResult } from "./server.ts";
test("overlay maps claude-control exits", () => {
  expect(overlayResult(0, "granted t12\n")).toMatchObject({ state: "granted", ticket: "t12" });
  expect(overlayResult(3, "stopped: ...").state).toBe("stopped");
  expect(overlayResult(1, "cancelled: Matt said not now").state).toBe("cancelled");
  expect(overlayResult(1, "hammerspoon unreachable").message).toContain("hammerspoon unreachable");
  expect(overlayResult(0, "").state).toBe("failed");
});
