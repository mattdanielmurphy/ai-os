// Mac connector: a small remote MCP server so Claude's voice chat (claude.ai custom
// connector) can search Matt's notes, read files on his Mac and hand tasks to the
// Everything project coordinator, in seconds.
//
//   bun server.ts          serve on 127.0.0.1:PORT at /mcp/<MAC_CONNECTOR_TOKEN>
//   bun server.ts --init   add MAC_CONNECTOR_TOKEN to ai-os/.env if missing and copy the
//                          public connector URL to the clipboard (never printed)
//
// Exposed publicly by Tailscale Funnel (see README.md). The long secret path is the
// auth; files are read-only and secret files are refused; tasks go through the voice
// task inbox (scripts/voice_task_inbox.py).
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { z } from "zod";
import { homedir } from "node:os";
import { join, resolve } from "node:path";
import { readFileSync, appendFileSync, existsSync, mkdirSync, writeFileSync, readdirSync, statSync, realpathSync, renameSync } from "node:fs";
import { randomBytes, createHash } from "node:crypto";

const HOME = homedir();
const AIOS = join(HOME, "projects", "ai-os");
const ENV_FILE = join(AIOS, ".env");
const QUEUE = join(AIOS, "tmp", "voice-task-inbox", "queue");
const WATCHER = join(AIOS, "scripts", "voice_task_inbox.py");
const LOG = join(AIOS, "tmp", "mac-connector.log");
// Replies from Mac agents to voice Claude (scripts/voice_reply.py writes them).
const OUTBOX = join(AIOS, "tmp", "voice-outbox");
export const ACT_URL_FILE = join(AIOS, "tmp", "mac-connector-act-url");
const PORT = Number(process.env.PORT ?? 8777);
const PUBLIC_HOST = "macbook-pro.tail491454.ts.net"; // claude.ai only connects on 443
const VAULT = join(HOME, "Library", "Mobile Documents", "iCloud~md~obsidian", "Documents", "Personal");
const CALLS = join(VAULT, "Voice calls");
const PATH_ENV = `${HOME}/.bun/bin:${HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin`;

function log(msg: string) {
  try { appendFileSync(LOG, `${new Date().toISOString()} ${msg}\n`); } catch {}
}

function envToken(): string {
  if (!existsSync(ENV_FILE)) return "";
  const m = readFileSync(ENV_FILE, "utf8").match(/^\s*MAC_CONNECTOR_TOKEN\s*=\s*['"]?([A-Za-z0-9_-]+)/m);
  return m ? m[1] : "";
}

// Matt's secret files never leave the Mac, whatever the request.
const SECRET = [/(^|\/)\.env(\.|$)/, /credential/i, /secret/i, /(^|\/)\.ssh\//, /\/Keychains\//,
  /\.(pem|key|p12|pfx|keychain-db)$/i, /(^|\/)id_(rsa|ed25519|ecdsa)/, /\/ai-os\/private\//, /token/i];

function safePath(p: string): string {
  const abs = resolve(p.replace(/^~(?=$|\/)/, HOME));
  const real = existsSync(abs) ? realpathSync(abs) : abs;
  if (!real.startsWith(HOME + "/") && real !== HOME) throw new Error("Only files inside Matt's home folder can be read.");
  if (SECRET.some((r) => r.test(real))) throw new Error("That file holds secrets, so it can't be read through the connector.");
  return real;
}

async function run(cmd: string[], timeoutMs = 20000): Promise<string> {
  const p = Bun.spawn(cmd, { stdout: "pipe", stderr: "pipe", env: { ...process.env, PATH: PATH_ENV }, cwd: HOME });
  const timer = setTimeout(() => p.kill(), timeoutMs);
  const out = await new Response(p.stdout).text();
  await p.exited;
  clearTimeout(timer);
  return out;
}

// Voice Claude can't be pushed to, so updates ride along on every tool result it gets.
function takeUpdates(): string[] {
  if (!existsSync(OUTBOX)) return [];
  const seen = join(OUTBOX, "seen");
  const out: string[] = [];
  for (const f of readdirSync(OUTBOX).filter((n) => n.endsWith(".json")).sort()) {
    try {
      const u = JSON.parse(readFileSync(join(OUTBOX, f), "utf8"));
      out.push(`• ${u.title}: ${u.text}`);
      mkdirSync(seen, { recursive: true });
      renameSync(join(OUTBOX, f), join(seen, f));
    } catch {}
  }
  return out;
}
const withUpdates = (t: string) => {
  const u = takeUpdates();
  return u.length ? `${t}\n\n📬 UPDATE FROM MATT'S MAC AGENTS (tell Matt now, before anything else):\n${u.join("\n")}` : t;
};
const text = (t: string) => ({ content: [{ type: "text" as const, text: withUpdates(t) }] });
const fail = (e: unknown) => ({ content: [{ type: "text" as const, text: withUpdates(String((e as Error).message ?? e)) }], isError: true });

function buildServer(): McpServer {
  const server = new McpServer({ name: "matts-mac", version: "0.1.0" }, {
    instructions: "Matt's Mac. After you send_task during a call, start EVERY later reply by calling check_updates " +
      "(instant) and tell Matt about any update first: it's how his Mac agents report back. If he says he'll wait for a " +
      "result, call wait_for_update. Use search_notes for anything about Matt, his projects, notes or past AI threads; " +
      "find_files / list_folder / read_file for files; send_task to hand real work to his project coordinator " +
      "(it runs on his Mac with full access). For his morning check-in, call checkin_today first. During voice calls, " +
      "call note_call whenever Matt mentions a to-do or new fact (and every few minutes with what he said), so an abrupt " +
      "hang-up loses nothing; run save_call at the end. Before ANY action that moves or resizes windows, clicks, " +
      "types or opens apps or dialogs on his Mac (any tool, e.g. Claude in Chrome), call overlay_on and wait for " +
      "'granted'; call overlay_off right after.",
  });

  server.registerTool("check_updates", {
    description: "Instant. Returns replies from Matt's Mac agents to tasks you sent (send_task). Call it at the start of " +
      "every reply after you've sent a task in this call, and tell Matt right away if there is one.",
    inputSchema: {},
  }, async () => {
    const u = takeUpdates();
    return { content: [{ type: "text" as const, text: u.length ? `📬 Updates (tell Matt now):\n${u.join("\n")}` : "No new updates." }] };
  });

  server.registerTool("wait_for_update", {
    description: "Wait up to `seconds` (max 50) for a reply from Matt's Mac agents. Only when Matt says he'll wait for a result.",
    inputSchema: { seconds: z.number().int().min(5).max(50).optional() },
  }, async ({ seconds }) => {
    const until = Date.now() + (seconds ?? 45) * 1000;
    while (Date.now() < until) {
      const u = takeUpdates();
      if (u.length) return { content: [{ type: "text" as const, text: `📬 Updates (tell Matt now):\n${u.join("\n")}` }] };
      await Bun.sleep(2000);
    }
    return { content: [{ type: "text" as const, text: "Nothing yet. The agent is still working; check again on your next reply." }] };
  });

  server.registerTool("search_notes", {
    description: "Keyword search over Matt's Obsidian vault and his past Claude, Gemini and Antigravity threads (QMD). " +
      "Returns matching files with snippets; open one with get_note.",
    inputSchema: { query: z.string().describe("A few distinctive keywords"), limit: z.number().int().min(1).max(20).optional() },
  }, async ({ query, limit }) => {
    try {
      const out = await run(["qmd", "search", query, "--format", "json", "-n", String(limit ?? 6)]);
      const hits = JSON.parse(out || "[]") as any[];
      if (!hits.length) return text("No matches. Try other keywords.");
      return text(hits.map((h) => `${h.file} (line ${h.line}) — ${h.title}\n${String(h.snippet ?? "").slice(0, 600)}`).join("\n\n"));
    } catch (e) { return fail(e); }
  });

  server.registerTool("get_note", {
    description: "Open a note or thread found by search_notes (pass its qmd:// file), optionally from a line.",
    inputSchema: { file: z.string(), from_line: z.number().int().min(1).optional(), lines: z.number().int().min(1).max(400).optional() },
  }, async ({ file, from_line, lines }) => {
    try {
      const ref = from_line ? `${file}:${from_line}:${lines ?? 120}` : file;
      const out = await run(["qmd", "get", ref]);
      return text(out.slice(0, 30000) || "Nothing found at that path.");
    } catch (e) { return fail(e); }
  });

  server.registerTool("find_files", {
    description: "Find files on Matt's Mac by name (Spotlight), inside his home folder.",
    inputSchema: { name: z.string().describe("Part of the file name"), limit: z.number().int().min(1).max(50).optional() },
  }, async ({ name, limit }) => {
    try {
      const out = await run(["mdfind", "-onlyin", HOME, "-name", name]);
      const files = out.split("\n").filter((f) => f && !SECRET.some((r) => r.test(f)) && !f.includes("/node_modules/") && !f.includes("/Library/"));
      return text(files.slice(0, limit ?? 20).join("\n") || "No files found.");
    } catch (e) { return fail(e); }
  });

  server.registerTool("list_folder", {
    description: "List a folder on Matt's Mac (e.g. ~/projects, ~/Desktop).",
    inputSchema: { path: z.string() },
  }, async ({ path }) => {
    try {
      const dir = safePath(path);
      const rows = readdirSync(dir).filter((n) => !n.startsWith(".")).slice(0, 300).map((n) => {
        try { return statSync(join(dir, n)).isDirectory() ? `${n}/` : n; } catch { return n; }
      });
      return text(rows.join("\n") || "(empty)");
    } catch (e) { return fail(e); }
  });

  server.registerTool("read_file", {
    description: "Read a text file on Matt's Mac (code, markdown, notes, configs). Secret files are refused.",
    inputSchema: { path: z.string(), max_chars: z.number().int().min(100).max(100000).optional() },
  }, async ({ path, max_chars }) => {
    try {
      const f = safePath(path);
      const body = readFileSync(f, "utf8");
      const cap = max_chars ?? 30000;
      return text(body.length > cap ? body.slice(0, cap) + `\n\n[truncated: ${body.length} chars total]` : body);
    } catch (e) { return fail(e); }
  });

  server.registerTool("send_task", {
    description: "Hand a task to Matt's project coordinator (Claude on his Mac with full access). It's posted into his " +
      "Everything project chat within seconds. Use for real work: coding, research, " +
      "changes on his Mac, reminders, anything you can't do yourself.",
    inputSchema: {
      title: z.string().describe("Short title, under 8 words"),
      ask: z.string().describe("What Matt wants, in his own words where possible"),
      context: z.string().optional().describe("Anything from the conversation the coordinator needs to act"),
      urgent: z.boolean().optional(),
    },
  }, async ({ title, ask, context, urgent }) => {
    try {
      const body = [`Ask: ${ask}`, context ? `Context: ${context}` : "", `Urgent: ${urgent ? "yes" : "no"}`].filter(Boolean).join("\n\n");
      queueTask(title, body);
      log(`task queued: ${title}`);
      return text("Sent. It's posted into Matt's project chat within seconds (or as soon as his Mac is unlocked), with a brief on-screen banner first.");
    } catch (e) { return fail(e); }
  });

  server.registerTool("note_call", {
    description: "Call this DURING a voice call, right away whenever Matt mentions a to-do, a reminder or a new fact " +
      "about himself, and every few minutes with what he said since the last note. Saves it to his Mac at once, so " +
      "nothing is lost if the call ends abruptly. Still run save_call at the end.",
    inputSchema: {
      facts: z.array(z.string()).optional().describe("New facts about Matt, his life, projects or setup"),
      todos: z.array(z.string()).optional().describe("Reminders, calendar events, emails or tasks, with dates/times"),
      said: z.string().optional().describe("What Matt said since the last note, as close to word for word as you can"),
    },
  }, async ({ facts, todos, said }) => {
    try {
      const d = noteCall({ facts, todos, said });
      log(`call noted: ${d.file}`);
      return text("Noted.");
    } catch (e) { return fail(e); }
  });

  server.registerTool("save_call", {
    description: "Run this at the END of every voice call with Matt. Saves the call as a searchable note on his Mac " +
      "(Obsidian vault, indexed for all his agents) and hands any new facts and to-dos to his project coordinator, " +
      "which files the facts and makes the reminders, calendar events and emails.",
    inputSchema: {
      title: z.string().describe("What the call was about, under 8 words"),
      summary: z.string().describe("A few sentences: what was discussed and decided"),
      matt_said: z.string().describe("Everything Matt said, as close to word for word as you can, in order"),
      facts: z.array(z.string()).optional().describe("New facts about Matt, his life, projects or setup worth remembering"),
      todos: z.array(z.string()).optional().describe("Reminders, calendar events, emails or tasks to act on, with dates/times"),
    },
  }, async ({ title, summary, matt_said, facts, todos }) => {
    try {
      const now = new Date();
      const day = now.toLocaleDateString("en-CA", { timeZone: "America/Edmonton" });
      const hm = now.toLocaleTimeString("en-GB", { timeZone: "America/Edmonton", hour: "2-digit", minute: "2-digit" }).replace(":", "");
      const safeTitle = title.replace(/[\/:*?"<>|#^\[\]]/g, "").trim().slice(0, 60) || "Voice call";
      const list = (xs?: string[]) => (xs?.length ? xs.map((x) => `- ${x}`).join("\n") : "- (none)");
      // Fold in anything noted live during the call (note_call), then retire the draft note.
      const draft = takeDraft();
      facts = uniq([...(draft?.facts ?? []), ...(facts ?? [])]);
      todos = uniq([...(draft?.todos ?? []), ...(todos ?? [])]);
      mkdirSync(CALLS, { recursive: true });
      const name = `${day} ${hm} ${safeTitle}.md`;
      writeFileSync(join(CALLS, name), [
        "---", `title: ${JSON.stringify(safeTitle)}`, `created: ${day}`, `updated: ${day}`, "type: daily", "tags: [journal, ai-os]", "source: voice-chat", "---", "",
        `# ${safeTitle}`, "", "## Summary", summary, "", "## New facts", list(facts), "", "## To-dos", list(todos), "", "## What Matt said", matt_said, "",
        ...(draft?.said.length ? ["## Noted live during the call", draft.said.join("\n\n"), ""] : []),
      ].join("\n"));
      if (draft) trashDraftNote(draft);
      try { appendFileSync(join(VAULT, "log.md"), `\n- ${day}: Voice call saved: [[Voice calls/${name.replace(/\.md$/, "")}]]\n`); } catch {}
      Bun.spawn(["qmd", "update"], { stdout: "ignore", stderr: "ignore", env: { ...process.env, PATH: PATH_ENV } }).unref();
      if (facts?.length || todos?.length) {
        queueTask(`File voice call: ${safeTitle}`, [
          `From a voice call, saved at "Voice calls/${name}" in the Obsidian vault.`,
          facts?.length ? `New facts to file (memory / ABOUT_MATT / the right note):\n${list(facts)}` : "",
          todos?.length ? `To-dos to act on (reminders, calendar, email):\n${list(todos)}` : "",
          "Urgent: no",
        ].filter(Boolean).join("\n\n"));
      }
      log(`call saved: ${name}`);
      return text(`Saved as "Voice calls/${name}".` + (facts?.length || todos?.length ? " Facts and to-dos were sent to the coordinator." : ""));
    } catch (e) { return fail(e); }
  });

  server.registerTool("checkin_today", {
    description: "Call this FIRST when Matt opens a chat with \"Morning check-in\" (or asks to do his check-in). " +
      "Returns today's check-in instructions (his habits, calendar, recent notes); follow them for the rest of the chat.",
    inputSchema: {},
  }, async () => {
    try {
      const day = today();
      const f = join(CHECKIN, "data", `checkin-${day}.md`);
      if (!existsSync(f)) return text(`Today's check-in (${day}) isn't prepared yet; it's built at 7:45. ` +
        "Tell Matt, and just have a short, warm morning chat about his day instead.");
      const mode = readFileSync(join(import.meta.dir, "..", "checkin", "chat_mode.md"), "utf8").split("\n---\n", 2)[1].trim();
      log(`checkin_today ${day}`);
      return text(`${mode}\n\n---\n\n${readFileSync(f, "utf8")}`);
    } catch (e) { return fail(e); }
  });

  server.registerTool("checkin_record", {
    description: "Record today's morning check-in, once Matt has talked (see checkin_today): his talking minutes for the " +
      "habit ladder and 3-5 short bullets for his habit log.",
    inputSchema: {
      minutes: z.number().int().min(1).max(120).describe("Minutes Matt talked (about 130 words a minute, rounded up)"),
      bullets: z.array(z.string()).min(1).max(8).describe("3-5 short bullets, his words where possible"),
    },
  }, async ({ minutes, bullets }) => {
    try {
      const day = today();
      const p = Bun.spawnSync(["/usr/bin/python3", join(CHECKIN, "ladder.py"), "record", "--date", day, `reflection=${minutes}`],
        { stdout: "pipe", stderr: "pipe", env: { ...process.env, PATH: PATH_ENV } });
      if (p.exitCode !== 0) throw new Error(`ladder record failed: ${p.stderr.toString().slice(0, 300)}`);
      appendCheckinLog(day, bullets);
      log(`checkin_record ${day} ${minutes}m ${bullets.length} bullets`);
      return text(`Recorded ${minutes} min and ${bullets.length} bullets for ${day}.`);
    } catch (e) { return fail(e); }
  });

  // The orange take-control overlay (~/.hammerspoon/bin/claude-control), so remote sessions warn Matt
  // before touching his screen. Auto-releases after 60s on the Hammerspoon side if a session dies.
  server.registerTool("overlay_on", {
    description: "Call BEFORE doing anything that changes Matt's screen: moving or resizing windows, clicking, typing, " +
      "opening apps, files or dialogs. Shows his orange 'hands off' overlay, waits ~3s (he can press Esc), and returns " +
      "'granted' when you may go. If it says 'cancelled' or 'stopped', don't do the action; tell Matt. Turns itself off " +
      "after 60s; call overlay_off as soon as you're done (or overlay_on again for another 60s).",
    inputSchema: {
      reason: z.string().describe("What you're about to do and why, in a few words, e.g. 'Resizing Chrome to test the layout'"),
      light: z.boolean().optional().describe("true = small corner pill, no glow, for low-impact changes he can type " +
        "through (open a file/app, focus a window, play/pause, volume). Default false = full glow: clicking, typing, resizing."),
    },
  }, async ({ reason, light }) => {
    const r = await overlayOn(reason, light ?? false);
    log(`overlay_on ${r.state}${light ? " light" : ""}: ${reason.slice(0, 80)}`);
    return r.state === "granted" ? text("granted: overlay is on. Go ahead, then call overlay_off.") : fail(new Error(r.message));
  });

  server.registerTool("overlay_off", {
    description: "Turn off Matt's orange overlay after your on-screen action is finished.",
    inputSchema: {},
  }, async () => {
    const was = await overlayOff();
    log(`overlay_off ${was ?? "none"}`);
    return text(was ? "Overlay off." : "Overlay was already off.");
  });

  // Called by Matt's review page (services/review) through the claude.ai "My Mac" connector, so the page
  // never opens a tab (a tab would steal focus from its comment box).
  server.registerTool("dictate", {
    description: "Only for Matt's review page: start, stop or toggle TypeWhisper dictation on his Mac. Text lands " +
      "in whatever field has focus. Voice chat: don't call this.",
    inputSchema: { action: z.enum(["start", "stop", "toggle", "status"]).optional() },
  }, async ({ action }) => {
    const p = Bun.spawnSync([join(AIOS, "scripts", "dictate.sh"), action ?? "toggle"], { stdout: "pipe", stderr: "pipe", env: { ...process.env, PATH: PATH_ENV } });
    log(`dictate ${action ?? "toggle"} exit=${p.exitCode}`);
    if (p.exitCode !== 0) return fail(new Error(p.stderr.toString().trim().slice(0, 200) || `dictate.sh exit ${p.exitCode}`));
    return text(p.stdout.toString().trim() || "ok");
  });

  server.registerTool("review_done", {
    description: "Only for Matt's review page: tell the thread that published the page that he finished reviewing.",
    inputSchema: { page: z.string(), thread: z.string().optional() },
  }, async ({ page, thread }) => {
    const r = actRequest(new URL(`https://x/act/x/review-done?page=${encodeURIComponent(page)}&thread=${encodeURIComponent(thread ?? "")}`));
    if (!r.body) return fail(new Error(r.title));
    queueTask(r.title, r.body);
    log(`review_done ${page}`);
    return text("Sent to the coordinator.");
  });

  server.registerTool("practice_done", {
    description: "Only for Matt's logic practice page: record today's habit-gate study step and wake the threads holding his messages.",
    inputSchema: {},
  }, async () => {
    try {
      const r = practiceDone();
      return text(r.threads.length ? "Unlocked. Claude picks up your message in the thread." : "Unlocked.");
    } catch (e) { return fail(e as Error); }
  });

  return server;
}

// One overlay ticket at a time for the whole connector. A fixed agent id means Matt's Stop blocks the
// connector's overlay asks for 2h (claude-control's rule), and the ticket survives across tool calls.
const CONTROL = join(HOME, ".hammerspoon", "bin", "claude-control");
const CONTROL_AGENT = "my_mac_connector";
let overlayTicket: string | null = null;

export function overlayResult(code: number, out: string): { state: string; ticket?: string; message: string } {
  const m = out.match(/granted (t\d+)/);
  if (code === 0 && m) return { state: "granted", ticket: m[1], message: "granted" };
  if (code === 3) return { state: "stopped", message: "stopped: Matt pressed Stop. Don't do the action or retry another way; tell him what you were about to do." };
  if (/cancelled/.test(out)) return { state: "cancelled", message: "cancelled: Matt said not now. Don't do the action; tell him what you need and wait." };
  return { state: "failed", message: `Overlay didn't turn on (${out.trim().split("\n").pop() || `exit ${code}`}). Don't touch his screen; tell Matt.` };
}

async function control(args: string[], timeoutMs: number): Promise<{ code: number; out: string }> {
  const p = Bun.spawn([CONTROL, ...args], { stdout: "pipe", stderr: "pipe", cwd: HOME,
    env: { ...process.env, PATH: PATH_ENV, CLAUDE_CODE_SESSION_ID: CONTROL_AGENT } });
  const timer = setTimeout(() => p.kill(), timeoutMs);
  const out = await new Response(p.stdout).text();
  const code = await p.exited;
  clearTimeout(timer);
  return { code, out };
}

export async function overlayOn(reason: string, light: boolean) {
  await overlayOff();  // re-asking while holding would queue behind ourselves
  // Short queue wait: an MCP call shouldn't hang for claude-control's full 3 min.
  const { code, out } = await control(["ask", reason.slice(0, 200), "3", ...(light ? ["--light"] : [])], 45_000);
  const r = overlayResult(code, out);
  if (r.ticket) overlayTicket = r.ticket;
  return r;
}

export async function overlayOff(): Promise<string | null> {
  const t = overlayTicket;
  overlayTicket = null;
  if (t) await control(["done", t], 8_000);
  return t;
}

const CHECKIN = join(AIOS, "services", "checkin");
const today = () => new Date().toLocaleDateString("en-CA", { timeZone: "America/Edmonton" });

// Add bullets under "## Morning check-in" in the day's habit log (the heading is created if missing).
export function appendCheckinLog(day: string, bullets: string[], vault = VAULT) {
  const dir = join(vault, "habits", "logs");
  mkdirSync(dir, { recursive: true });
  const f = join(dir, `${day}.md`);
  const body = existsSync(f) ? readFileSync(f, "utf8") : "";
  const lines = bullets.map((b) => `- ${b.replace(/^\s*[-*]\s*/, "").trim()}`).join("\n");
  const at = body.indexOf("## Morning check-in");
  let out: string;
  if (at < 0) {
    out = (body.trim() ? body.replace(/\s*$/, "\n\n") : "") + `## Morning check-in\n${lines}\n`;
  } else {
    const next = body.indexOf("\n## ", at + 1);
    const end = next < 0 ? body.length : next;
    out = body.slice(0, end).replace(/\s*$/, "\n") + lines + "\n" + (next < 0 ? "" : "\n" + body.slice(next + 1));
  }
  writeFileSync(f, out);
}

// Practice page Done: habit_gate.py records the step and writes the note naming the threads to wake.
export function practiceDone(gate = join(CHECKIN, "habit_gate.py")): { threads: string[]; note: string } {
  const p = Bun.spawnSync(["python3", gate, "page-done"], { stdout: "pipe", stderr: "pipe", env: { ...process.env, PATH: PATH_ENV } });
  if (p.exitCode !== 0) throw new Error(`habit_gate page-done failed: ${p.stderr.toString().slice(0, 200)}`);
  const r = JSON.parse(p.stdout.toString());
  if (r.threads.length) queueTask("Practice done", r.note);
  log(`practice_done threads=${r.threads.length}`);
  return r;
}

// Mid-call notes (note_call): written to the vault the moment voice Claude sends them, so a call that
// ends abruptly (Matt hangs up, the app closes) still leaves its facts and to-dos on the Mac. save_call
// folds the draft into the final note; a draft idle for DRAFT_IDLE_MS is handed to the coordinator by
// flushStaleDraft (timer below), which also pulls the transcript early.
type Draft = { file: string; started: number; last: number; facts: string[]; todos: string[]; said: string[] };
const DRAFT_DIR = join(AIOS, "tmp", "voice-calls");
export const DRAFT_IDLE_MS = 20 * 60_000;
const uniq = (xs: string[]) => [...new Set(xs.map((x) => x.trim()).filter(Boolean))];
const edm = (t: number) => {
  const d = new Date(t);
  return { day: d.toLocaleDateString("en-CA", { timeZone: "America/Edmonton" }),
    hm: d.toLocaleTimeString("en-GB", { timeZone: "America/Edmonton", hour: "2-digit", minute: "2-digit" }) };
};

export function readDraft(dir = DRAFT_DIR): Draft | null {
  try { return JSON.parse(readFileSync(join(dir, "draft.json"), "utf8")); } catch { return null; }
}

function renderDraft(d: Draft, ended = false): string {
  const { day, hm } = edm(d.started);
  const list = (xs: string[]) => (xs.length ? xs.map((x) => `- ${x}`).join("\n") : "- (none yet)");
  return ["---", `title: "Voice call ${hm}"`, `created: ${day}`, `updated: ${edm(d.last).day}`, "type: daily",
    "tags: [journal, ai-os]", "source: voice-chat-live", "---", "", `# Voice call ${hm}`, "",
    ended ? `Ended without save_call (last note ${edm(d.last).hm}); facts and to-dos went to the coordinator, and the ` +
      "full transcript lands in Voice calls/Transcripts/." : "Saved live during the call; save_call replaces this note when the call ends.",
    "", "## New facts", list(d.facts), "", "## To-dos", list(d.todos), "", "## What Matt said", d.said.join("\n\n") || "(nothing yet)", ""].join("\n");
}

export function noteCall(add: { facts?: string[]; todos?: string[]; said?: string }, now = Date.now(), dir = DRAFT_DIR, calls = CALLS): Draft {
  let d = readDraft(dir);
  if (!d || now - d.last > DRAFT_IDLE_MS) {
    const { day, hm } = edm(now);
    d = { file: `${day} ${hm.replace(":", "")} Voice call (live).md`, started: now, last: now, facts: [], todos: [], said: [] };
  }
  d.facts = uniq([...d.facts, ...(add.facts ?? [])]);
  d.todos = uniq([...d.todos, ...(add.todos ?? [])]);
  if (add.said?.trim()) d.said.push(add.said.trim());
  d.last = now;
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, "draft.json"), JSON.stringify(d));
  mkdirSync(calls, { recursive: true });
  writeFileSync(join(calls, d.file), renderDraft(d));
  return d;
}

// Close the open draft: its state moves to done/ (kept, never deleted) and the caller decides the note's fate.
export function takeDraft(dir = DRAFT_DIR): Draft | null {
  const d = readDraft(dir);
  if (!d) return null;
  mkdirSync(join(dir, "done"), { recursive: true });
  renameSync(join(dir, "draft.json"), join(dir, "done", `${d.started}.json`));
  return d;
}

function trashDraftNote(d: Draft, calls = CALLS) {
  try { renameSync(join(calls, d.file), join(HOME, ".Trash", `${Date.now()} ${d.file}`)); } catch {}
}

// The call went quiet without save_call: hand the noted facts and to-dos to the coordinator now and pull
// the transcript (scripts/pull_voice_chats.py flags it for review) instead of waiting for the 3:30 run.
export function flushStaleDraft(now = Date.now(), dir = DRAFT_DIR, calls = CALLS, queue = queueTask, pull = pullTranscripts): boolean {
  const d = readDraft(dir);
  if (!d || now - d.last <= DRAFT_IDLE_MS) return false;
  takeDraft(dir);
  try { writeFileSync(join(calls, d.file), renderDraft(d, true)); } catch {}
  const list = (xs: string[]) => xs.map((x) => `- ${x}`).join("\n");
  if (d.facts.length || d.todos.length) {
    queue(`File voice call: unsaved call ${edm(d.started).hm}`, [
      `A voice call ended without save_call. What voice Claude noted live is at "Voice calls/${d.file}" in the Obsidian vault.`,
      d.facts.length ? `New facts to file (memory / ABOUT_MATT / the right note):\n${list(d.facts)}` : "",
      d.todos.length ? `To-dos to act on (reminders, calendar, email):\n${list(d.todos)}` : "",
      "A \"Review unsaved voice calls\" task for the same call may follow with the full transcript; skip what's already handled here.",
      "Urgent: no",
    ].filter(Boolean).join("\n\n"));
  }
  pull();
  return true;
}

function pullTranscripts() {
  Bun.spawn(["/usr/bin/python3", join(AIOS, "scripts", "pull_voice_chats.py")],
    { stdout: "ignore", stderr: "ignore", env: { ...process.env, PATH: PATH_ENV } }).unref();
}

// Queue a task for the coordinator and kick the watcher so it's delivered right away.
function queueTask(title: string, body: string) {
  mkdirSync(QUEUE, { recursive: true });
  writeFileSync(join(QUEUE, `${Date.now()}-${randomBytes(3).toString("hex")}.json`), JSON.stringify({ title, body }));
  Bun.spawn(["/usr/bin/python3", WATCHER], { stdout: "ignore", stderr: "ignore", env: { ...process.env, PATH: PATH_ENV } }).unref();
}

// Links on Matt's artifact pages (e.g. a review page's Done button) hit /act/<actToken>/...
// The act token is derived from the connector token, so a page never carries the MCP token
// and a leaked page link can only queue a short, fixed-shape note for the coordinator.
export const actToken = (token: string) => createHash("sha256").update(`${token}:act`).digest("base64url").slice(0, 32);

const ID = /^[A-Za-z0-9_-]{1,80}$/;
export function actRequest(url: URL): { status: number; title: string; body?: string; run?: string } {
  const [, , , action] = url.pathname.split("/");
  if (action === "ping") return { status: 204, title: "ping" };
  if (action === "practice-done") return { status: 200, title: "Practice done", run: "practice-done" };
  if (action !== "review-done") return { status: 404, title: "Unknown action" };
  const page = url.searchParams.get("page") ?? "", thread = url.searchParams.get("thread") ?? "";
  if (!ID.test(page) || (thread && !ID.test(thread))) return { status: 400, title: "Bad link" };
  return { status: 200, title: "Review done", body: [
    `Matt finished reviewing on artifact https://claude.ai/artifact/${page} (Done button).`,
    thread ? `Route to thread ${thread} (message_thread) so its agent reads his ticks and notes from the page's db (ArtifactData, collection "reviews").` : "Find the thread that published this page and route it there.",
    "Urgent: no",
  ].join("\n\n") };
}

const htmlPage = (msg: string, status = 200) => new Response(
  `<!doctype html><meta name=viewport content="width=device-width"><title>${msg}</title>` +
  `<body style="font:600 22px -apple-system,sans-serif;display:grid;place-items:center;height:90vh;color:#234">${msg}</body>`,
  { status, headers: { "content-type": "text/html; charset=utf-8" } });

function init() {
  let token = envToken();
  if (!token) {
    token = randomBytes(24).toString("base64url");
    appendFileSync(ENV_FILE, `\nMAC_CONNECTOR_TOKEN=${token}\n`);
  }
  const p = Bun.spawnSync(["pbcopy"], { stdin: Buffer.from(`https://${PUBLIC_HOST}/mcp/${token}`) });
  console.log(p.exitCode === 0 ? "Connector URL copied to the clipboard." : "pbcopy failed");
}

if (!import.meta.main) {
  // imported (tests): don't serve
} else if (process.argv.includes("--init")) {
  init();
} else {
  const token = envToken();
  if (!token) { console.error("MAC_CONNECTOR_TOKEN missing; run `bun server.ts --init`"); process.exit(1); }
  const secretPath = `/mcp/${token}`;
  setInterval(() => { try { if (flushStaleDraft()) log("stale call draft flushed"); } catch (e) { log(`draft flush failed: ${e}`); } }, 2 * 60_000);
  Bun.serve({
    port: PORT,
    hostname: "127.0.0.1",
    idleTimeout: 120,
    async fetch(req) {
      const url = new URL(req.url);
      const shown = url.pathname.replace(token, "<token>").replace(actToken(token), "<act>");
      log(`${req.method} ${shown} ua=${(req.headers.get("user-agent") ?? "").slice(0, 60)} accept=${req.headers.get("accept") ?? ""}`);
      if (url.pathname === "/health") return new Response("ok");
      if (url.pathname.startsWith(`/act/${actToken(token)}/`)) {
        const r = actRequest(url);
        if (r.body) { queueTask(r.title, r.body); log(`act queued: ${r.title}`); }
        if (r.run === "practice-done") {
          try { practiceDone(); return htmlPage("Unlocked ✓ Claude picks up your message in the thread."); }
          catch (e) { log(String(e)); return htmlPage("Couldn't record it. Reply 👍 in the thread.", 500); }
        }
        if (r.status === 204) { log(`act ping from ${req.headers.get("origin") ?? "?"}`); return new Response(null, { status: 204, headers: { "access-control-allow-origin": "*" } }); }
        return htmlPage(r.status === 200 ? "Sent ✓ You can close this tab." : r.title, r.status);
      }
      if (url.pathname !== secretPath) return new Response("Not found", { status: 404 });
      // Stateless server: no standalone SSE stream to open, so GET/DELETE get 405 (as in the SDK's
      // stateless example) instead of hanging open.
      if (req.method !== "POST") return new Response("Method not allowed", { status: 405, headers: { allow: "POST" } });
      // Stateless: a fresh server + transport per request.
      const transport = new WebStandardStreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
      await buildServer().connect(transport);
      return transport.handleRequest(req);
    },
  });
  // Page builders (services/review) read the act base URL from here; it never holds the MCP token.
  writeFileSync(ACT_URL_FILE, `https://${PUBLIC_HOST}/act/${actToken(token)}`, { mode: 0o600 });
  log(`listening on 127.0.0.1:${PORT}`);
  console.log(`mac-connector listening on 127.0.0.1:${PORT}`);
}
