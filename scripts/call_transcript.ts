#!/usr/bin/env bun
/**
 * Live call transcript: stereo audio from a virtual device -> Deepgram live -> ~/calls/<date>-<who>.md
 *
 *   bun scripts/call_transcript.ts [who] [--device "BlackHole 16ch"] [--left Matt] [--right <Who>]
 *
 * Audio Hijack sends Matt's mic to the left channel and the call app to the right,
 * into BlackHole. Each channel is transcribed separately (Deepgram multichannel), and every
 * final line is appended (and flushed) as "[HH:MM:SS] Name: text", so any model can read the
 * file mid-call. A raw WAV backup of what was streamed goes next to it.
 *
 * Key: $DEEPGRAM_API_KEY, else macOS keychain item "deepgram" (never printed).
 * Start/stop with scripts/call-transcript (start | stop | status | tail).
 */
import { appendFileSync, mkdirSync, existsSync } from "fs";
import { homedir } from "os";
import { join } from "path";

const args = process.argv.slice(2);
const flag = (name: string, def: string) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
};
const who = (args.find((a, i) => !a.startsWith("--") && !args[i - 1]?.startsWith("--")) || "tyler").toLowerCase();
const device = flag("device", "BlackHole 16ch");
const names = [flag("left", "Matt"), flag("right", who[0].toUpperCase() + who.slice(1))];
const model = flag("model", "nova-3");
const RATE = 16000;

async function apiKey(): Promise<string> {
  if (process.env.DEEPGRAM_API_KEY) return process.env.DEEPGRAM_API_KEY.trim();
  const p = Bun.spawn(["security", "find-generic-password", "-s", "deepgram", "-w"], { stdout: "pipe", stderr: "ignore" });
  const out = (await new Response(p.stdout).text()).trim();
  await p.exited;
  if (!out) {
    console.error('No Deepgram key. Add it once: security add-generic-password -U -s deepgram -a "$USER" -w');
    process.exit(2);
  }
  return out;
}

const pad = (n: number) => String(n).padStart(2, "0");
const now = new Date();
const day = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
const dir = join(homedir(), "calls");
mkdirSync(dir, { recursive: true });
const md = join(dir, `${day}-${who}.md`);
const stamp = `${pad(now.getHours())}${pad(now.getMinutes())}`;
const wav = join(dir, `${day}-${who}-${stamp}.wav`);
const clock = () => { const d = new Date(); return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`; };
// appendFileSync opens, writes and closes each time, so every line is on disk immediately.
const write = (line: string) => appendFileSync(md, line + "\n");

if (!existsSync(md)) write(`# Call with ${names[1]} — ${day}\n\nLeft channel = ${names[0]}, right channel = ${names[1]}. Live transcript, final lines only.\n`);
write(`\n<!-- session started ${clock()} (backup: ${wav}) -->`);

const key = await apiKey();

// ffmpeg: read the virtual device, keep channels 1-2, 16 kHz s16le to stdout + a WAV backup.
const ff = Bun.spawn([
  "ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "avfoundation", "-i", `:${device}`,
  "-af", "pan=stereo|c0=c0|c1=c1", "-ar", String(RATE),
  "-f", "s16le", "-acodec", "pcm_s16le", "pipe:1",
  "-af", "pan=stereo|c0=c0|c1=c1", "-ar", String(RATE), "-acodec", "pcm_s16le", wav,
], { stdout: "pipe", stderr: "inherit" });

const qs = new URLSearchParams({
  model, encoding: "linear16", sample_rate: String(RATE), channels: "2", multichannel: "true",
  punctuate: "true", smart_format: "true", interim_results: "false", language: "en",
});
let ws: WebSocket;
let stopping = false;
let pending: Uint8Array[] = [];
let dropped = false;

function connect() {
  ws = new WebSocket(`${process.env.DG_URL || "wss://api.deepgram.com/v1/listen"}?${qs}`, { headers: { Authorization: `Token ${key}` } } as any);
  ws.binaryType = "arraybuffer";
  ws.onopen = () => {
    console.log(`connected · ${device} → ${md}`);
    if (dropped) write(`<!-- transcription back at ${clock()} -->`);
    dropped = false;
    for (const c of pending) ws.send(c);
    pending = [];
  };
  ws.onmessage = (ev) => {
    let m: any;
    try { m = JSON.parse(String(ev.data)); } catch { return; }
    if (m.type !== "Results" || !m.is_final) return;
    const text = m.channel?.alternatives?.[0]?.transcript?.trim();
    if (!text) return;
    const ch = m.channel_index?.[0] ?? 0;
    const line = `[${clock()}] ${names[ch] ?? `Channel ${ch}`}: ${text}`;
    write(line);
    console.log(line);
    lastSpeech = Date.now();
    reminded = false;
  };
  ws.onerror = (e: any) => console.error("deepgram error:", e?.message ?? e);
  ws.onclose = (e) => {
    if (stopping) return;
    console.error(`deepgram closed (${e.code} ${e.reason}); reconnecting in 2s`);
    if (!dropped) write(`<!-- transcription dropped at ${clock()}, reconnecting -->`);
    dropped = true;
    setTimeout(connect, 2000);
  };
}
connect();

// Hang-up reminder: a toast when FaceTime closes or nobody has spoken for a while.
// (Starting/stopping on its own when a FaceTime call to Tyler begins/ends is the next step.)
const SILENT_MS = Number(flag("silence", "90")) * 1000;
let lastSpeech = Date.now();
let reminded = false;
const notify = (title: string, body: string) =>
  Bun.spawn([join(homedir(), ".hammerspoon/bin/claude-notify"), title, body, "--kind", "needs"], { stdout: "ignore", stderr: "ignore" });
setInterval(async () => {
  if (stopping || reminded) return;
  const p = Bun.spawn(["pgrep", "-x", "FaceTime"], { stdout: "ignore" });
  const facetime = (await p.exited) === 0;
  const quiet = Date.now() - lastSpeech > SILENT_MS;
  if (!facetime || quiet) {
    reminded = true;
    notify("Call over? Stop the transcript", `${!facetime ? "FaceTime closed" : `No one has spoken for ${SILENT_MS / 1000}s`}. Run: call-transcript stop`);
    console.log(`reminder sent (${!facetime ? "FaceTime closed" : "silence"})`);
  }
}, 10000);

async function stop() {
  if (stopping) return;
  stopping = true;
  write(`<!-- session ended ${clock()} -->`);
  try { ws.send(JSON.stringify({ type: "CloseStream" })); } catch {}
  ff.kill("SIGINT"); // lets ffmpeg finish the WAV header
  setTimeout(() => process.exit(0), 2500);
}
process.on("SIGINT", stop);
process.on("SIGTERM", stop);

for await (const chunk of ff.stdout as any as AsyncIterable<Uint8Array>) {
  if (ws.readyState === WebSocket.OPEN) ws.send(chunk);
  else if (!stopping) { pending.push(chunk); if (pending.length > 500) pending.shift(); }
}
if (!stopping) { console.error("audio input ended"); await stop(); }
