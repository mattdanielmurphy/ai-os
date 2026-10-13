import { readFile } from "fs/promises";
import { join } from "path";

const PORT = 3344;
const PRESETS_PATH = join(import.meta.dir, "presets.json");
const VOICES_PATH = join(import.meta.dir, "voices.json");

interface ClientSession {
  deepgramWs: WebSocket | null;
  clientWs: any;
  authenticated: boolean;
  settingsSent: boolean;
  settingsApplied: boolean;
}

const sessions = new Map<any, ClientSession>();

export function buildDeepgramSettings(config: {
  speed?: number;
  expressivity?: number;
  eot_threshold?: number;
  eager_eot_threshold?: number;
  eot_timeout_ms?: number;
  temperature?: number;
  voice_model?: string;
  listen_model?: string;
  think_model?: string;
  prompt?: string;
  greeting?: string;
  sample_rate_in?: number;
  sample_rate_out?: number;
}) {
  const isFlux = (config.voice_model || "").startsWith("flux-");

  const speakProvider: Record<string, any> = {
    type: "deepgram",
    model: config.voice_model || "flux-conor-en"
  };

  if (isFlux) {
    speakProvider.version = "v2";
    if (typeof config.speed === "number") {
      speakProvider.speed = config.speed;
    }
    if (typeof config.expressivity === "number") {
      speakProvider.expressivity = config.expressivity;
    }
  } else {
    // Aura / Aura-2
    if (typeof config.speed === "number") {
      speakProvider.speed = config.speed;
    }
  }

  const thinkProvider: Record<string, any> = {
    type: "google",
    model: config.think_model || "gemini-3.1-flash-lite"
  };

  if (typeof config.temperature === "number") {
    thinkProvider.temperature = config.temperature;
  }

  return {
    type: "Settings",
    audio: {
      input: {
        encoding: "linear16",
        sample_rate: config.sample_rate_in || 48000
      },
      output: {
        encoding: "linear16",
        sample_rate: config.sample_rate_out || 24000,
        container: "none"
      }
    },
    agent: {
      speak: {
        provider: speakProvider
      },
      listen: {
        provider: (() => {
          const rawEot = typeof config.eot_threshold === "number" ? config.eot_threshold : 0.58;
          const clampedEot = Math.min(1.0, Math.max(0.5, rawEot));
          const rawEager = typeof config.eager_eot_threshold === "number" ? config.eager_eot_threshold : 0.45;
          const clampedEager = Math.min(clampedEot, Math.max(0.3, Math.min(0.9, rawEager)));
          return {
            type: "deepgram",
            version: "v2",
            model: config.listen_model || "flux-general-en",
            eot_threshold: clampedEot,
            eager_eot_threshold: clampedEager,
            eot_timeout_ms: config.eot_timeout_ms || 2500
          };
        })()
      },
      think: {
        provider: thinkProvider,
        prompt: config.prompt || ""
      },
      greeting: config.greeting || "GET OUT OF BED RIGHT NOW!"
    }
  };
}

const server = Bun.serve({
  port: PORT,
  fetch(req, server) {
    const url = new URL(req.url);

    // WebSocket upgrade
    if (url.pathname === "/ws/agent") {
      const upgraded = server.upgrade(req);
      if (upgraded) return undefined;
      return new Response("WebSocket upgrade failed", { status: 400 });
    }

    // API Routes
    if (url.pathname === "/api/presets") {
      try {
        const file = Bun.file(PRESETS_PATH);
        return new Response(file, {
          headers: { "Content-Type": "application/json" }
        });
      } catch (e: any) {
        return new Response(JSON.stringify({ error: e.message }), { status: 500 });
      }
    }

    if (url.pathname === "/api/voices") {
      try {
        const file = Bun.file(VOICES_PATH);
        return new Response(file, {
          headers: { "Content-Type": "application/json" }
        });
      } catch (e: any) {
        return new Response(JSON.stringify({ error: e.message }), { status: 500 });
      }
    }

    if (url.pathname === "/api/build-settings" && req.method === "POST") {
      return req.json().then((body) => {
        const settings = buildDeepgramSettings(body);
        return new Response(JSON.stringify(settings, null, 2), {
          headers: { "Content-Type": "application/json" }
        });
      });
    }

    // Static files
    let filePath = join(import.meta.dir, "public", url.pathname === "/" ? "index.html" : url.pathname.slice(1));
    const file = Bun.file(filePath);
    return file.exists().then((exists) => {
      if (exists) {
        return new Response(file);
      }
      return new Response("Not Found", { status: 404 });
    });
  },

  websocket: {
    open(ws) {
      sessions.set(ws, {
        deepgramWs: null,
        clientWs: ws,
        authenticated: false,
        settingsSent: false,
        settingsApplied: false
      });
    },

    message(ws, message) {
      const session = sessions.get(ws);
      if (!session) return;

      // Binary audio stream from client mic -> Deepgram
      // CRITICAL: Gate mic streaming on settingsApplied so mic audio does not flood/corrupt Deepgram handshake
      if (typeof message !== "string") {
        if (session.settingsApplied && session.deepgramWs && session.deepgramWs.readyState === WebSocket.OPEN) {
          session.deepgramWs.send(message);
        }
        return;
      }

      // JSON control message from browser client
      try {
        const data = JSON.parse(message);
        if (data.type === "connect_deepgram") {
          const { apiKey, settings } = data;
          if (!apiKey) {
            ws.send(JSON.stringify({ type: "error", error: "Missing Deepgram API Key" }));
            return;
          }

          const dgEndpoint = "wss://agent.deepgram.com/v1/agent/converse";
          const authToken = apiKey.startsWith("Token ") || apiKey.startsWith("Bearer ")
            ? apiKey
            : `Token ${apiKey.trim()}`;

          const dgWs = new WebSocket(dgEndpoint, {
            headers: {
              Authorization: authToken
            }
          });
          dgWs.binaryType = "arraybuffer";

          session.deepgramWs = dgWs;
          session.settingsSent = false;
          session.settingsApplied = false;

          const sendSettings = () => {
            if (!session.settingsSent && dgWs.readyState === WebSocket.OPEN) {
              session.settingsSent = true;
              console.log("[Server] Sending settings to Deepgram:", JSON.stringify(settings, null, 2));
              dgWs.send(JSON.stringify(settings));
              ws.send(JSON.stringify({ type: "status", status: "settings_sent", settings }));
            }
          };

          dgWs.onopen = () => {
            console.log("[Server] Connected to Deepgram Voice Agent WebSocket");
            ws.send(JSON.stringify({ type: "status", status: "deepgram_connected" }));
            // Deepgram sends Welcome first, but in case it is delayed, fallback send after 350ms
            setTimeout(sendSettings, 350);
          };

          dgWs.onmessage = (event) => {
            if (typeof event.data === "string") {
              try {
                const parsed = JSON.parse(event.data);
                console.log("[Server <- Deepgram event]:", parsed.type, parsed.message || parsed.warning || parsed.error || "");
                if (parsed.type === "Welcome") {
                  sendSettings();
                } else if (parsed.type === "SettingsApplied") {
                  session.settingsApplied = true;
                  console.log("[Server] Deepgram SettingsApplied confirmed! Audio streaming active.");
                  ws.send(JSON.stringify({ type: "status", status: "settings_applied" }));
                }
                ws.send(JSON.stringify({ type: "deepgram_event", data: parsed }));
              } catch {
                console.log("[Server <- Deepgram raw]:", event.data);
                ws.send(JSON.stringify({ type: "deepgram_event", raw: event.data }));
              }
            } else {
              const byteLen = event.data?.byteLength || event.data?.length || 0;
              // Deepgram raw Linear16 PCM audio chunk from TTS -> forward binary to browser
              ws.send(event.data);
            }
          };

          dgWs.onerror = (err: any) => {
            const errMsg = err.message || "Expected 101 status code (Handshake rejected)";
            ws.send(JSON.stringify({
              type: "error",
              error: `Deepgram connection error: ${errMsg}. Check that your Deepgram API Key is valid and has Voice Agent access enabled.`
            }));
          };

          dgWs.onclose = (event) => {
            let reasonText = event.reason || "";
            if (event.code === 1002 && !reasonText) {
              reasonText = "Handshake rejected (often 401 Unauthorized - verify your Deepgram API key)";
            }
            ws.send(JSON.stringify({
              type: "status",
              status: "deepgram_closed",
              code: event.code,
              reason: reasonText
            }));
            session.deepgramWs = null;
          };
        } else if (data.type === "disconnect_deepgram") {
          if (session.deepgramWs) {
            session.deepgramWs.close();
            session.deepgramWs = null;
          }
          ws.send(JSON.stringify({ type: "status", status: "disconnected" }));
        } else if (data.type === "update_speak") {
          // Mid-call TTS update
          if (session.deepgramWs && session.deepgramWs.readyState === WebSocket.OPEN) {
            session.deepgramWs.send(JSON.stringify({
              type: "UpdateSpeak",
              speak: data.speak
            }));
            ws.send(JSON.stringify({ type: "status", status: "update_sent", updateType: "UpdateSpeak", speak: data.speak }));
          }
        } else if (data.type === "update_listen") {
          // Mid-call STT / EOT update
          if (session.deepgramWs && session.deepgramWs.readyState === WebSocket.OPEN) {
            const listen = { ...(data.listen || {}) };
            if (listen.provider) {
              const rawEot = typeof listen.provider.eot_threshold === "number" ? listen.provider.eot_threshold : 0.58;
              listen.provider.eot_threshold = Math.min(1.0, Math.max(0.5, rawEot));
              const rawEager = typeof listen.provider.eager_eot_threshold === "number" ? listen.provider.eager_eot_threshold : 0.45;
              listen.provider.eager_eot_threshold = Math.min(listen.provider.eot_threshold, Math.max(0.3, Math.min(0.9, rawEager)));
            }
            session.deepgramWs.send(JSON.stringify({
              type: "UpdateListen",
              listen: listen
            }));
            ws.send(JSON.stringify({ type: "status", status: "update_sent", updateType: "UpdateListen", listen: listen }));
          }
        } else if (data.type === "update_think") {
          // Mid-call LLM / Prompt update
          if (session.deepgramWs && session.deepgramWs.readyState === WebSocket.OPEN) {
            session.deepgramWs.send(JSON.stringify({
              type: "UpdateThink",
              think: data.think
            }));
            ws.send(JSON.stringify({ type: "status", status: "update_sent", updateType: "UpdateThink", think: data.think }));
          }
        } else if (data.type === "inject_user_message") {
          // Inject simulated user message (e.g. silence re-engagement nudge)
          if (session.deepgramWs && session.deepgramWs.readyState === WebSocket.OPEN) {
            session.deepgramWs.send(JSON.stringify({
              type: "InjectUserMessage",
              content: data.content
            }));
            ws.send(JSON.stringify({ type: "status", status: "inject_user_message_sent", content: data.content }));
          }
        } else if (data.type === "inject_agent_message") {
          // Force agent to speak direct message
          if (session.deepgramWs && session.deepgramWs.readyState === WebSocket.OPEN) {
            session.deepgramWs.send(JSON.stringify({
              type: "InjectAgentMessage",
              message: data.message,
              behavior: data.behavior || "default"
            }));
            ws.send(JSON.stringify({ type: "status", status: "inject_agent_message_sent", message: data.message }));
          }
        }
      } catch (e: any) {
        ws.send(JSON.stringify({ type: "error", error: "Invalid client message: " + e.message }));
      }
    },

    close(ws) {
      const session = sessions.get(ws);
      if (session?.deepgramWs) {
        session.deepgramWs.close();
      }
      sessions.delete(ws);
    }
  }
});

console.log(`Morning Call Tester server running at http://localhost:${PORT}`);
console.log(`Puma-dev domain: http://morning-call.test`);
