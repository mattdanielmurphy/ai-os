import { readFile } from "fs/promises";
import { join } from "path";

const PORT = 3344;
const PRESETS_PATH = join(import.meta.dir, "presets.json");

interface ClientSession {
  deepgramWs: WebSocket | null;
  clientWs: any;
  authenticated: boolean;
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
  const speakProvider: Record<string, any> = {
    type: "deepgram",
    version: "v2",
    model: config.voice_model || "flux-conor-en",
    speed: typeof config.speed === "number" ? config.speed : 1.25
  };

  if (typeof config.expressivity === "number") {
    speakProvider.expressivity = config.expressivity;
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
        provider: {
          type: "deepgram",
          version: "v2",
          model: config.listen_model || "flux-general-en",
          eot_threshold: typeof config.eot_threshold === "number" ? config.eot_threshold : 0.6,
          eager_eot_threshold: typeof config.eager_eot_threshold === "number" ? config.eager_eot_threshold : 0.45,
          eot_timeout_ms: config.eot_timeout_ms || 3000
        }
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
        authenticated: false
      });
    },

    message(ws, message) {
      const session = sessions.get(ws);
      if (!session) return;

      // Binary audio stream from client mic -> Deepgram
      if (typeof message !== "string") {
        if (session.deepgramWs && session.deepgramWs.readyState === WebSocket.OPEN) {
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

          session.deepgramWs = dgWs;
          let settingsSent = false;

          const sendSettings = () => {
            if (!settingsSent && dgWs.readyState === WebSocket.OPEN) {
              settingsSent = true;
              dgWs.send(JSON.stringify(settings));
              ws.send(JSON.stringify({ type: "status", status: "settings_sent", settings }));
            }
          };

          dgWs.onopen = () => {
            ws.send(JSON.stringify({ type: "status", status: "deepgram_connected" }));
            // Deepgram sends Welcome first, but in case it is delayed, fallback send after 400ms
            setTimeout(sendSettings, 400);
          };

          dgWs.onmessage = (event) => {
            if (typeof event.data === "string") {
              try {
                const parsed = JSON.parse(event.data);
                if (parsed.type === "Welcome") {
                  sendSettings();
                }
                ws.send(JSON.stringify({ type: "deepgram_event", data: parsed }));
              } catch {
                ws.send(JSON.stringify({ type: "deepgram_event", raw: event.data }));
              }
            } else {
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
