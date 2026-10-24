#!/usr/bin/env bun
/**
 * Recover a gap in a live call transcript from an audio recording (e.g. Audio Hijack).
 *
 *   bun scripts/call_recover.ts <audio> <clock-of-audio-start HH:MM:SS> <out.md>
 *       [--left Tyler] [--right Matt]
 *
 * Sends the (stereo) audio to Deepgram prerecorded, one transcript per channel, and writes
 * "[HH:MM:SS] Name: text" lines (audio start clock + utterance offset) sorted by time,
 * in the same format as call_transcript.ts. Splicing into the call file is a separate step.
 * Key: $DEEPGRAM_API_KEY, else macOS keychain item "deepgram" (never printed).
 */
import { writeFileSync } from "fs";

const args = process.argv.slice(2);
const flag = (n: string, d: string) => { const i = args.indexOf(`--${n}`); return i >= 0 ? args[i + 1] : d; };
const [audio, startClock, out] = args;
if (!audio || !startClock || !out) { console.error("usage: call_recover.ts <audio> <HH:MM:SS> <out.md> [--left A] [--right B]"); process.exit(2); }
const names = [flag("left", "Tyler"), flag("right", "Matt")];

async function apiKey(): Promise<string> {
  if (process.env.DEEPGRAM_API_KEY) return process.env.DEEPGRAM_API_KEY.trim();
  const p = Bun.spawn(["security", "find-generic-password", "-s", "deepgram", "-w"], { stdout: "pipe", stderr: "ignore" });
  const k = (await new Response(p.stdout).text()).trim();
  if (!k) { console.error("No Deepgram key"); process.exit(2); }
  return k;
}

const qs = new URLSearchParams({ model: flag("model", "nova-3"), multichannel: "true", punctuate: "true",
  smart_format: "true", utterances: "true", language: "en" });
const res = await fetch(`https://api.deepgram.com/v1/listen?${qs}`, {
  method: "POST", headers: { Authorization: `Token ${await apiKey()}`, "Content-Type": "audio/mpeg" },
  body: Bun.file(audio),
});
if (!res.ok) { console.error(`deepgram ${res.status}: ${await res.text()}`); process.exit(1); }
const data: any = await res.json();
writeFileSync(out + ".json", JSON.stringify(data));

const [h, m, s] = startClock.split(":").map(Number);
const base = h * 3600 + m * 60 + s;
const pad = (n: number) => String(n).padStart(2, "0");
const clock = (t: number) => { t = Math.floor(base + t); return `${pad(Math.floor(t / 3600) % 24)}:${pad(Math.floor(t / 60) % 60)}:${pad(t % 60)}`; };
const lines = (data.results?.utterances ?? [])
  .filter((u: any) => u.transcript?.trim())
  .sort((a: any, b: any) => a.start - b.start)
  .map((u: any) => `[${clock(u.start)}] ${names[u.channel] ?? `Channel ${u.channel}`}: ${u.transcript.trim()}`);
writeFileSync(out, lines.join("\n") + "\n");
console.log(`${lines.length} lines → ${out}`);
