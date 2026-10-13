let presets = {};
let activeWs = null;
let audioCtx = null;
let micStream = null;
let scriptProcessor = null;
let callStartTime = null;
let timerInterval = null;
let nextPlayTime = 0;
let analyser = null;
let animFrameId = null;

const elements = {
  presetSelect: document.getElementById("presetSelect"),
  personaDesc: document.getElementById("personaDesc"),
  speedSlider: document.getElementById("speedSlider"),
  speedVal: document.getElementById("speedVal"),
  eotSlider: document.getElementById("eotSlider"),
  eotVal: document.getElementById("eotVal"),
  voiceSelect: document.getElementById("voiceSelect"),
  thinkSelect: document.getElementById("thinkSelect"),
  greetingInput: document.getElementById("greetingInput"),
  promptInput: document.getElementById("promptInput"),
  apiKeyInput: document.getElementById("apiKeyInput"),
  saveKeyBtn: document.getElementById("saveKeyBtn"),
  connectionBadge: document.getElementById("connectionBadge"),
  startCallBtn: document.getElementById("startCallBtn"),
  endCallBtn: document.getElementById("endCallBtn"),
  callTimer: document.getElementById("callTimer"),
  transcriptBox: document.getElementById("transcriptBox"),
  clearLogBtn: document.getElementById("clearLogBtn"),
  jsonPreview: document.getElementById("jsonPreview"),
  copyJsonBtn: document.getElementById("copyJsonBtn"),
  canvas: document.getElementById("waveformCanvas")
};

// Initialize
async function init() {
  // Load saved API Key
  const savedKey = localStorage.getItem("deepgram_api_key");
  if (savedKey) {
    elements.apiKeyInput.value = savedKey;
  }

  // Load Presets
  try {
    const res = await fetch("/api/presets");
    presets = await res.json();
    populatePresets();
    loadPreset("drill_sergeant");
  } catch (err) {
    console.error("Failed to load presets:", err);
  }

  attachEventListeners();
  updateJsonPreview();
}

function populatePresets() {
  elements.presetSelect.innerHTML = "";
  for (const [key, p] of Object.entries(presets)) {
    const opt = document.createElement("option");
    opt.value = key;
    opt.textContent = p.name;
    elements.presetSelect.appendChild(opt);
  }
  const customOpt = document.createElement("option");
  customOpt.value = "custom";
  customOpt.textContent = "-- Custom Persona --";
  elements.presetSelect.appendChild(customOpt);
}

function loadPreset(key) {
  const p = presets[key];
  if (!p) return;

  elements.personaDesc.textContent = p.description;
  elements.speedSlider.value = p.speed || 1.25;
  elements.speedVal.textContent = parseFloat(p.speed || 1.25).toFixed(2);
  elements.eotSlider.value = p.eot_threshold || 0.6;
  elements.eotVal.textContent = parseFloat(p.eot_threshold || 0.6).toFixed(2);
  elements.voiceSelect.value = p.voice_model || "flux-conor-en";
  elements.thinkSelect.value = p.think_model || "gemini-3.1-flash-lite";
  elements.greetingInput.value = p.greeting || "";
  elements.promptInput.value = p.prompt || "";

  updateJsonPreview();
}

function getSettingsObject() {
  const speed = parseFloat(elements.speedSlider.value);
  const eot = parseFloat(elements.eotSlider.value);
  const eagerEot = Math.max(0.3, parseFloat((eot - 0.15).toFixed(2)));

  return {
    type: "Settings",
    audio: {
      input: {
        encoding: "linear16",
        sample_rate: 48000
      },
      output: {
        encoding: "linear16",
        sample_rate: 24000,
        container: "none"
      }
    },
    agent: {
      speak: {
        provider: {
          type: "deepgram",
          version: "v2",
          model: elements.voiceSelect.value.trim() || "flux-conor-en",
          speed: speed
        }
      },
      listen: {
        provider: {
          type: "deepgram",
          version: "v2",
          model: "flux-general-en",
          eot_threshold: eot,
          eager_eot_threshold: eagerEot,
          eot_timeout_ms: 3000
        }
      },
      think: {
        provider: {
          type: "google",
          model: elements.thinkSelect.value.trim() || "gemini-3.1-flash-lite"
        },
        prompt: elements.promptInput.value
      },
      greeting: elements.greetingInput.value
    }
  };
}

function updateJsonPreview() {
  const settings = getSettingsObject();
  elements.jsonPreview.textContent = JSON.stringify(settings, null, 2);
}

function attachEventListeners() {
  elements.presetSelect.addEventListener("change", (e) => {
    if (e.target.value !== "custom") {
      loadPreset(e.target.value);
    } else {
      elements.personaDesc.textContent = "Custom user-configured persona.";
    }
  });

  elements.speedSlider.addEventListener("input", (e) => {
    elements.speedVal.textContent = parseFloat(e.target.value).toFixed(2);
    updateJsonPreview();
  });

  elements.eotSlider.addEventListener("input", (e) => {
    elements.eotVal.textContent = parseFloat(e.target.value).toFixed(2);
    updateJsonPreview();
  });

  [elements.voiceSelect, elements.thinkSelect, elements.greetingInput, elements.promptInput].forEach((el) => {
    el.addEventListener("input", updateJsonPreview);
  });

  elements.saveKeyBtn.addEventListener("click", () => {
    const key = elements.apiKeyInput.value.trim();
    if (key) {
      localStorage.setItem("deepgram_api_key", key);
      alert("Deepgram API Key saved to local browser storage!");
    }
  });

  elements.copyJsonBtn.addEventListener("click", () => {
    const jsonText = elements.jsonPreview.textContent;
    navigator.clipboard.writeText(jsonText).then(() => {
      const orig = elements.copyJsonBtn.textContent;
      elements.copyJsonBtn.textContent = "Copied! ✓";
      setTimeout(() => (elements.copyJsonBtn.textContent = orig), 2000);
    });
  });

  elements.clearLogBtn.addEventListener("click", () => {
    elements.transcriptBox.innerHTML = '<div class="transcript-placeholder">Conversation log cleared.</div>';
  });

  elements.startCallBtn.addEventListener("click", startCall);
  elements.endCallBtn.addEventListener("click", endCall);
}

function setBadge(text, className) {
  elements.connectionBadge.textContent = text;
  elements.connectionBadge.className = `badge ${className}`;
}

function appendTranscript(sender, text) {
  const placeholder = elements.transcriptBox.querySelector(".transcript-placeholder");
  if (placeholder) placeholder.remove();

  const bubble = document.createElement("div");
  bubble.className = `msg-bubble ${sender === "agent" ? "msg-agent" : "msg-user"}`;
  bubble.innerHTML = `
    <div class="msg-sender">${sender === "agent" ? "Drill Instructor" : "You"}</div>
    <div class="msg-content">${escapeHtml(text)}</div>
  `;
  elements.transcriptBox.appendChild(bubble);
  elements.transcriptBox.scrollTop = elements.transcriptBox.scrollHeight;
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Live Audio Call Handling
async function startCall() {
  const apiKey = elements.apiKeyInput.value.trim() || localStorage.getItem("deepgram_api_key");
  if (!apiKey) {
    alert("Please enter a Deepgram API Key before starting a call.");
    elements.apiKeyInput.focus();
    return;
  }

  setBadge("CONNECTING", "status-connecting");
  elements.startCallBtn.disabled = true;
  elements.endCallBtn.disabled = false;

  try {
    // Setup AudioContext (48kHz sample rate)
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 48000 });
    nextPlayTime = audioCtx.currentTime;

    // Mic input
    micStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: 48000,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });

    const micSource = audioCtx.createMediaStreamSource(micStream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    micSource.connect(analyser);

    // Setup ScriptProcessor to capture PCM Linear16
    scriptProcessor = audioCtx.createScriptProcessor(4096, 1, 1);
    micSource.connect(scriptProcessor);
    scriptProcessor.connect(audioCtx.destination); // Required for scriptProcessor to fire in Chrome

    // Connect to local proxy WebSocket
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    activeWs = new WebSocket(`${wsProtocol}//${window.location.host}/ws/agent`);
    activeWs.binaryType = "arraybuffer";

    activeWs.onopen = () => {
      const settings = getSettingsObject();
      activeWs.send(JSON.stringify({
        type: "connect_deepgram",
        apiKey: apiKey,
        settings: settings
      }));
    };

    activeWs.onmessage = (event) => {
      if (typeof event.data === "string") {
        handleServerJson(JSON.parse(event.data));
      } else {
        // Binary Linear16 PCM audio chunk received from Deepgram TTS
        playPcmChunk(event.data, 24000);
      }
    };

    activeWs.onerror = (err) => {
      console.error("WebSocket Error:", err);
      appendTranscript("agent", "[Error: Connection failed]");
      endCall();
    };

    activeWs.onclose = () => {
      endCall();
    };

    // Feed mic PCM data to WebSocket
    scriptProcessor.onaudioprocess = (e) => {
      if (!activeWs || activeWs.readyState !== WebSocket.OPEN) return;
      const inputData = e.inputBuffer.getChannelData(0);
      const pcm16 = floatTo16BitPCM(inputData);
      activeWs.send(pcm16.buffer);
    };

    // Start UI Call Timer and Waveform
    startTimer();
    startWaveformAnimation();
  } catch (err) {
    console.error("Failed to start call:", err);
    alert("Audio initialization error: " + err.message);
    endCall();
  }
}

function handleServerJson(msg) {
  if (msg.type === "status") {
    if (msg.status === "deepgram_connected") {
      setBadge("IN CALL", "status-active");
    } else if (msg.status === "settings_sent") {
      const greeting = elements.greetingInput.value.trim();
      if (greeting) {
        appendTranscript("agent", greeting);
      }
    }
  } else if (msg.type === "deepgram_event") {
    const data = msg.data;
    if (data.type === "ConversationText") {
      if (data.role === "user") {
        appendTranscript("user", data.content);
        setBadge("AGENT THINKING", "status-connecting");
      } else if (data.role === "agent" || data.role === "assistant") {
        appendTranscript("agent", data.content);
        setBadge("SPEAKING", "status-speaking");
      }
    } else if (data.type === "UserStartedSpeaking") {
      setBadge("LISTENING", "status-active");
    } else if (data.type === "AgentStartedSpeaking") {
      setBadge("SPEAKING", "status-speaking");
    } else if (data.type === "EndOfTurn") {
      setBadge("AGENT THINKING", "status-connecting");
    }
  } else if (msg.type === "error") {
    alert(msg.error);
    endCall();
  }
}

function playPcmChunk(arrayBuffer, sampleRate = 24000) {
  if (!audioCtx) return;

  const int16 = new Int16Array(arrayBuffer);
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) {
    float32[i] = int16[i] / 32768.0;
  }

  const audioBuffer = audioCtx.createBuffer(1, float32.length, sampleRate);
  audioBuffer.getChannelData(0).set(float32);

  const source = audioCtx.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioCtx.destination);

  const startTime = Math.max(audioCtx.currentTime, nextPlayTime);
  source.start(startTime);
  nextPlayTime = startTime + audioBuffer.duration;
}

function floatTo16BitPCM(float32Array) {
  const pcm16 = new Int16Array(float32Array.length);
  for (let i = 0; i < float32Array.length; i++) {
    let s = Math.max(-1, Math.min(1, float32Array[i]));
    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return pcm16;
}

function startTimer() {
  callStartTime = Date.now();
  elements.callTimer.textContent = "00:00";
  timerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - callStartTime) / 1000);
    const m = String(Math.floor(elapsed / 60)).padStart(2, "0");
    const s = String(elapsed % 60).padStart(2, "0");
    elements.callTimer.textContent = `${m}:${s}`;
  }, 1000);
}

function endCall() {
  clearInterval(timerInterval);
  timerInterval = null;

  if (activeWs) {
    if (activeWs.readyState === WebSocket.OPEN) {
      activeWs.send(JSON.stringify({ type: "disconnect_deepgram" }));
      activeWs.close();
    }
    activeWs = null;
  }

  if (scriptProcessor) {
    scriptProcessor.disconnect();
    scriptProcessor = null;
  }

  if (micStream) {
    micStream.getTracks().forEach((t) => t.stop());
    micStream = null;
  }

  if (audioCtx) {
    audioCtx.close().catch(() => {});
    audioCtx = null;
  }

  if (animFrameId) {
    cancelAnimationFrame(animFrameId);
    animFrameId = null;
  }

  elements.startCallBtn.disabled = false;
  elements.endCallBtn.disabled = true;
  setBadge("IDLE", "status-idle");
  elements.callTimer.textContent = "00:00";

  // Clear waveform canvas
  const ctx = elements.canvas.getContext("2d");
  ctx.clearRect(0, 0, elements.canvas.width, elements.canvas.height);
}

function startWaveformAnimation() {
  const canvas = elements.canvas;
  const ctx = canvas.getContext("2d");
  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  function draw() {
    animFrameId = requestAnimationFrame(draw);
    analyser.getByteTimeDomainData(dataArray);

    ctx.fillStyle = "#161b22";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.lineWidth = 2;
    ctx.strokeStyle = "#58a6ff";
    ctx.beginPath();

    const sliceWidth = (canvas.width * 1.0) / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0;
      const y = (v * canvas.height) / 2;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      x += sliceWidth;
    }

    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();
  }

  draw();
}

window.addEventListener("DOMContentLoaded", init);
