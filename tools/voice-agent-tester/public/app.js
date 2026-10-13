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

// Audio and Speech State (for No-Spoiler Revealing)
let pendingAgentUtterance = "";
let activeAudioSourcesCount = 0;
let agentAudioDoneTimer = null;

const elements = {
  presetSelect: document.getElementById("presetSelect"),
  personaDesc: document.getElementById("personaDesc"),

  // Paired Inputs
  speedSlider: document.getElementById("speedSlider"),
  speedNum: document.getElementById("speedNum"),
  expressivitySlider: document.getElementById("expressivitySlider"),
  expressivityNum: document.getElementById("expressivityNum"),
  eotSlider: document.getElementById("eotSlider"),
  eotNum: document.getElementById("eotNum"),
  eagerEotSlider: document.getElementById("eagerEotSlider"),
  eagerEotNum: document.getElementById("eagerEotNum"),
  eotTimeoutSlider: document.getElementById("eotTimeoutSlider"),
  eotTimeoutNum: document.getElementById("eotTimeoutNum"),
  tempSlider: document.getElementById("tempSlider"),
  tempNum: document.getElementById("tempNum"),

  // Voice & Model
  voicePresetSelect: document.getElementById("voicePresetSelect"),
  voiceSelect: document.getElementById("voiceSelect"),
  thinkPresetSelect: document.getElementById("thinkPresetSelect"),
  thinkSelect: document.getElementById("thinkSelect"),

  // Text inputs
  greetingInput: document.getElementById("greetingInput"),
  promptInput: document.getElementById("promptInput"),
  apiKeyInput: document.getElementById("apiKeyInput"),
  saveKeyBtn: document.getElementById("saveKeyBtn"),

  // Stage & Status
  connectionBadge: document.getElementById("connectionBadge"),
  speakingPill: document.getElementById("speakingPill"),
  startCallBtn: document.getElementById("startCallBtn"),
  endCallBtn: document.getElementById("endCallBtn"),
  callTimer: document.getElementById("callTimer"),
  transcriptBox: document.getElementById("transcriptBox"),
  clearLogBtn: document.getElementById("clearLogBtn"),
  hideUntilSpokenCheckbox: document.getElementById("hideUntilSpokenCheckbox"),

  // JSON Export
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

  // Check Secure Context for Microphone (navigator.mediaDevices)
  const isSecure = window.isSecureContext && navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
  const notice = document.getElementById("secureContextNotice");
  if (!isSecure && notice) {
    notice.style.display = "flex";
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

  // Sync inputs
  setPairedValue(elements.speedSlider, elements.speedNum, p.speed !== undefined ? p.speed : 1.30);
  setPairedValue(elements.expressivitySlider, elements.expressivityNum, p.expressivity !== undefined ? p.expressivity : 2);
  setPairedValue(elements.eotSlider, elements.eotNum, p.eot_threshold !== undefined ? p.eot_threshold : 0.58);
  setPairedValue(elements.eagerEotSlider, elements.eagerEotNum, p.eager_eot_threshold !== undefined ? p.eager_eot_threshold : 0.45);
  setPairedValue(elements.eotTimeoutSlider, elements.eotTimeoutNum, p.eot_timeout_ms !== undefined ? p.eot_timeout_ms : 2500);
  setPairedValue(elements.tempSlider, elements.tempNum, p.temperature !== undefined ? p.temperature : 0.70);

  const voice = p.voice_model || "flux-conor-en";
  elements.voiceSelect.value = voice;
  syncDropdownToValue(elements.voicePresetSelect, voice);

  const model = p.think_model || "gemini-3.1-flash-lite";
  elements.thinkSelect.value = model;
  syncDropdownToValue(elements.thinkPresetSelect, model);

  elements.greetingInput.value = p.greeting || "";
  elements.promptInput.value = p.prompt || "";

  updateJsonPreview();
}

function setPairedValue(slider, numInput, value) {
  numInput.value = value;
  slider.value = value;
}

function syncDropdownToValue(selectEl, value) {
  let matched = false;
  for (const opt of selectEl.options) {
    if (opt.value === value) {
      selectEl.value = value;
      matched = true;
      break;
    }
  }
  if (!matched) {
    selectEl.value = "custom";
  }
}

function getSettingsObject() {
  const speed = parseFloat(elements.speedNum.value);
  const expressivity = parseInt(elements.expressivityNum.value, 10);
  const eot = parseFloat(elements.eotNum.value);
  const eagerEot = parseFloat(elements.eagerEotNum.value);
  const eotTimeout = parseInt(elements.eotTimeoutNum.value, 10);
  const temp = parseFloat(elements.tempNum.value);

  const speakProvider = {
    type: "deepgram",
    version: "v2",
    model: elements.voiceSelect.value.trim() || "flux-conor-en",
    speed: isNaN(speed) ? 1.3 : speed
  };

  if (!isNaN(expressivity)) {
    speakProvider.expressivity = expressivity;
  }

  const thinkProvider = {
    type: "google",
    model: elements.thinkSelect.value.trim() || "gemini-3.1-flash-lite"
  };

  if (!isNaN(temp)) {
    thinkProvider.temperature = temp;
  }

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
        provider: speakProvider
      },
      listen: {
        provider: {
          type: "deepgram",
          version: "v2",
          model: "flux-general-en",
          eot_threshold: isNaN(eot) ? 0.58 : eot,
          eager_eot_threshold: isNaN(eagerEot) ? 0.45 : eagerEot,
          eot_timeout_ms: isNaN(eotTimeout) ? 2500 : eotTimeout
        }
      },
      think: {
        provider: thinkProvider,
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

function bindPairedInput(slider, numInput) {
  slider.addEventListener("input", (e) => {
    numInput.value = e.target.value;
    updateJsonPreview();
  });
  numInput.addEventListener("input", (e) => {
    const val = parseFloat(e.target.value);
    if (!isNaN(val)) {
      slider.value = val;
      updateJsonPreview();
    }
  });
}

function attachEventListeners() {
  elements.presetSelect.addEventListener("change", (e) => {
    if (e.target.value !== "custom") {
      loadPreset(e.target.value);
    } else {
      elements.personaDesc.textContent = "Custom user-configured persona.";
    }
  });

  // Bind all paired sliders & inputs
  bindPairedInput(elements.speedSlider, elements.speedNum);
  bindPairedInput(elements.expressivitySlider, elements.expressivityNum);
  bindPairedInput(elements.eotSlider, elements.eotNum);
  bindPairedInput(elements.eagerEotSlider, elements.eagerEotNum);
  bindPairedInput(elements.eotTimeoutSlider, elements.eotTimeoutNum);
  bindPairedInput(elements.tempSlider, elements.tempNum);

  // Voice Presets
  elements.voicePresetSelect.addEventListener("change", (e) => {
    if (e.target.value !== "custom") {
      elements.voiceSelect.value = e.target.value;
      updateJsonPreview();
    }
  });
  elements.voiceSelect.addEventListener("input", (e) => {
    syncDropdownToValue(elements.voicePresetSelect, e.target.value.trim());
    updateJsonPreview();
  });

  // LLM Presets
  elements.thinkPresetSelect.addEventListener("change", (e) => {
    if (e.target.value !== "custom") {
      elements.thinkSelect.value = e.target.value;
      updateJsonPreview();
    }
  });
  elements.thinkSelect.addEventListener("input", (e) => {
    syncDropdownToValue(elements.thinkPresetSelect, e.target.value.trim());
    updateJsonPreview();
  });

  elements.greetingInput.addEventListener("input", updateJsonPreview);
  elements.promptInput.addEventListener("input", updateJsonPreview);

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
    pendingAgentUtterance = "";
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

function revealPendingAgentUtterance() {
  if (pendingAgentUtterance && pendingAgentUtterance.trim().length > 0) {
    appendTranscript("agent", pendingAgentUtterance.trim());
    pendingAgentUtterance = "";
  }
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Media Capture Helper
async function getAudioStream() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    return await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: 48000,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });
  }

  const legacyGetUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
  if (legacyGetUserMedia) {
    return new Promise((resolve, reject) => {
      legacyGetUserMedia.call(navigator, { audio: true }, resolve, reject);
    });
  }

  throw new Error("SECURE_CONTEXT_REQUIRED");
}

// Live Audio Call Handling
async function startCall() {
  const apiKey = elements.apiKeyInput.value.trim() || localStorage.getItem("deepgram_api_key");
  if (!apiKey) {
    alert("Please enter a Deepgram API Key before starting a call.");
    elements.apiKeyInput.focus();
    return;
  }

  // Pre-check for secure context / getUserMedia support
  const hasGetUserMedia = !!(
    (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) ||
    navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia
  );

  if (!hasGetUserMedia) {
    const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
    if (!isLocalhost) {
      if (confirm("Browser security blocks microphone access on http://*.test domains. Switch to http://localhost:3344 now to enable your mic?")) {
        window.location.href = `http://localhost:${window.location.port || 3344}`;
        return;
      }
    } else {
      alert("Microphone access is unavailable or blocked in your browser settings.");
    }
    return;
  }

  setBadge("CONNECTING", "status-connecting");
  elements.startCallBtn.disabled = true;
  elements.endCallBtn.disabled = false;
  pendingAgentUtterance = "";
  activeAudioSourcesCount = 0;

  try {
    // Setup AudioContext (48kHz sample rate)
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 48000 });
    nextPlayTime = audioCtx.currentTime;

    // Mic input
    micStream = await getAudioStream();

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
        if (!elements.hideUntilSpokenCheckbox.checked) {
          appendTranscript("agent", greeting);
        } else {
          pendingAgentUtterance = greeting;
          elements.speakingPill.style.display = "block";
        }
      }
    }
  } else if (msg.type === "deepgram_event") {
    const data = msg.data;
    if (data.type === "ConversationText") {
      if (data.role === "user") {
        // User finished speaking, reveal any leftover agent utterance first
        revealPendingAgentUtterance();
        appendTranscript("user", data.content);
        setBadge("AGENT THINKING", "status-connecting");
      } else if (data.role === "agent" || data.role === "assistant") {
        if (!elements.hideUntilSpokenCheckbox.checked) {
          appendTranscript("agent", data.content);
        } else {
          // Buffer the agent utterance and reveal ONLY when playback completes
          pendingAgentUtterance += (pendingAgentUtterance ? " " : "") + data.content;
          elements.speakingPill.style.display = "block";
        }
        setBadge("SPEAKING", "status-speaking");
      }
    } else if (data.type === "UserStartedSpeaking") {
      // User started talking; if agent was speaking, reveal whatever was said so far
      revealPendingAgentUtterance();
      elements.speakingPill.style.display = "none";
      setBadge("LISTENING", "status-active");
    } else if (data.type === "AgentStartedSpeaking") {
      elements.speakingPill.style.display = "block";
      setBadge("SPEAKING", "status-speaking");
    } else if (data.type === "AgentAudioDone") {
      // Deepgram finished sending audio frames; wait for audio playback queue to complete
      if (audioCtx) {
        const remainingDelayMs = Math.max(0, (nextPlayTime - audioCtx.currentTime) * 1000) + 120;
        clearTimeout(agentAudioDoneTimer);
        agentAudioDoneTimer = setTimeout(() => {
          elements.speakingPill.style.display = "none";
          revealPendingAgentUtterance();
          setBadge("IN CALL", "status-active");
        }, remainingDelayMs);
      } else {
        revealPendingAgentUtterance();
        elements.speakingPill.style.display = "none";
      }
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

  activeAudioSourcesCount++;
  elements.speakingPill.style.display = "block";

  source.onended = () => {
    activeAudioSourcesCount = Math.max(0, activeAudioSourcesCount - 1);
    // When last scheduled buffer ends playback, reveal dialogue if no more audio queued
    if (activeAudioSourcesCount === 0 && (audioCtx.currentTime >= nextPlayTime - 0.08)) {
      elements.speakingPill.style.display = "none";
      revealPendingAgentUtterance();
    }
  };
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
  clearTimeout(agentAudioDoneTimer);

  // Reveal any leftover pending text so transcript is complete
  revealPendingAgentUtterance();

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
  elements.speakingPill.style.display = "none";
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

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.lineWidth = 2;
    ctx.strokeStyle = "#0969da";
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
