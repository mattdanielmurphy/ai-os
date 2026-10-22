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
      "(it runs on his Mac with full access). For his morning check-in, call checkin_today first.",
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
      mkdirSync(CALLS, { recursive: true });
      const name = `${day} ${hm} ${safeTitle}.md`;
      writeFileSync(join(CALLS, name), [
        "---", `title: ${JSON.stringify(safeTitle)}`, `created: ${day}`, `updated: ${day}`, "type: daily", "tags: [journal, ai-os]", "source: voice-chat", "---", "",
        `# ${safeTitle}`, "", "## Summary", summary, "", "## New facts", list(facts), "", "## To-dos", list(todos), "", "## What Matt said", matt_said, "",
      ].join("\n"));
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

  return server;
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
export function actRequest(url: URL): { status: number; title: string; body?: string } {
  const [, , , action] = url.pathname.split("/");
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
