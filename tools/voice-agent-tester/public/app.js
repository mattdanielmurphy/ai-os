let presets = {};
let allVoices = [];
let favouriteVoiceIds = [];
let activeWs = null;
let audioCtx = null;
let micStream = null;
let scriptProcessor = null;
let callStartTime = null;
let timerInterval = null;
let nextPlayTime = 0;
let analyser = null;
let animFrameId = null;

// Audio and Speech State
let pendingAgentUtterance = "";
let activeAudioSourcesCount = 0;
let agentAudioDoneTimer = null;
let lastAgentUtterance = "";
let lastUserUtterance = "";

// Silence Re-engagement State
let silenceTimeoutId = null;
let silenceCountdownInterval = null;
let silenceRemainingSec = 0;
let isMidCallUpdateDebounceTimer = null;
let isAudioPlaying = false;

const STORAGE_KEY = "voice_agent_tester_settings_v2";
const FAVOURITES_KEY = "voice_agent_tester_favourite_voices";

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

  // Silence Re-engagement Controls
  silenceThresholdSlider: document.getElementById("silenceThresholdSlider"),
  silenceThresholdNum: document.getElementById("silenceThresholdNum"),
  silenceReengageCheckbox: document.getElementById("silenceReengageCheckbox"),
  silencePill: document.getElementById("silencePill"),

  // Voice & Model
  voiceSearchInput: document.getElementById("voiceSearchInput"),
  voicePresetSelect: document.getElementById("voicePresetSelect"),
  starVoiceBtn: document.getElementById("starVoiceBtn"),
  voiceMetaBox: document.getElementById("voiceMetaBox"),
  voiceSelect: document.getElementById("voiceSelect"),
  thinkPresetSelect: document.getElementById("thinkPresetSelect"),
  thinkSelect: document.getElementById("thinkSelect"),

  // Text inputs
  greetingInput: document.getElementById("greetingInput"),
  promptInput: document.getElementById("promptInput"),
  apiKeyInput: document.getElementById("apiKeyInput"),
  saveKeyBtn: document.getElementById("saveKeyBtn"),

  // Stage & Status
  midCallNotice: document.getElementById("midCallNotice"),
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

// ==========================================
// 1. Initialization & Voice Catalog Loading
// ==========================================
async function init() {
  loadFavourites();

  // Load Presets & Voice Catalog concurrently
  try {
    const [presetsRes, voicesRes] = await Promise.all([
      fetch("/api/presets").catch(() => null),
      fetch("/api/voices").catch(() => null)
    ]);

    if (presetsRes && presetsRes.ok) {
      presets = await presetsRes.json();
      populatePresets();
    }

    if (voicesRes && voicesRes.ok) {
      allVoices = await voicesRes.json();
    } else {
      allVoices = getFallbackVoices();
    }
  } catch (err) {
    console.error("Initialization fetch error:", err);
    allVoices = getFallbackVoices();
  }

  // Populate voice dropdown with favorites pinned to top
  renderVoiceOptions();

  // Restore all settings from browser storage (Requirement 1)
  const hadStoredSettings = loadSettingsFromStorage();
  if (!hadStoredSettings) {
    loadPreset("drill_sergeant");
  }

  // Check Secure Context for Microphone (navigator.mediaDevices)
  const isSecure = window.isSecureContext && navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
  const notice = document.getElementById("secureContextNotice");
  if (!isSecure && notice) {
    notice.style.display = "flex";
  }

  attachEventListeners();
  updateVoiceMetadataBox();
  updateJsonPreview();
}

// Load starred favourite voices from localStorage
function loadFavourites() {
  try {
    const stored = localStorage.getItem(FAVOURITES_KEY);
    if (stored) {
      favouriteVoiceIds = JSON.parse(stored);
    } else {
      // Sensible defaults including Miles (specifically requested by user) and Conor
      favouriteVoiceIds = ["flux-miles-en", "flux-conor-en", "flux-kit-en"];
      localStorage.setItem(FAVOURITES_KEY, JSON.stringify(favouriteVoiceIds));
    }
  } catch {
    favouriteVoiceIds = ["flux-miles-en", "flux-conor-en", "flux-kit-en"];
  }
}

function saveFavourites() {
  try {
    localStorage.setItem(FAVOURITES_KEY, JSON.stringify(favouriteVoiceIds));
  } catch (e) {
    console.error("Failed to save favourites:", e);
  }
}

function toggleFavouriteCurrentVoice() {
  const currentVoiceId = elements.voiceSelect.value.trim();
  if (!currentVoiceId) return;

  const idx = favouriteVoiceIds.indexOf(currentVoiceId);
  if (idx >= 0) {
    favouriteVoiceIds.splice(idx, 1);
  } else {
    favouriteVoiceIds.unshift(currentVoiceId);
  }

  saveFavourites();
  renderVoiceOptions(elements.voiceSearchInput.value.trim());
  updateStarButtonState();
  showMidCallNotice(idx >= 0 ? `Unstarred ${currentVoiceId}` : `⭐ Starred ${currentVoiceId} as favourite!`);
}

function updateStarButtonState() {
  const currentVoiceId = elements.voiceSelect.value.trim();
  const isFav = favouriteVoiceIds.includes(currentVoiceId);
  if (isFav) {
    elements.starVoiceBtn.textContent = "⭐";
    elements.starVoiceBtn.classList.add("starred");
    elements.starVoiceBtn.title = "Unstar favourite voice";
  } else {
    elements.starVoiceBtn.textContent = "☆";
    elements.starVoiceBtn.classList.remove("starred");
    elements.starVoiceBtn.title = "Star as favourite (pins to top)";
  }
}

// Render the voice catalog dropdown with favorites pinned to top
function renderVoiceOptions(filterText = "") {
  const select = elements.voicePresetSelect;
  const currentValue = elements.voiceSelect.value || "flux-conor-en";
  select.innerHTML = "";

  const query = filterText.toLowerCase().trim();

  // Filter voices if search query present
  const matches = (v) => {
    if (!query) return true;
    return (
      v.name.toLowerCase().includes(query) ||
      v.id.toLowerCase().includes(query) ||
      (v.accent && v.accent.toLowerCase().includes(query)) ||
      (v.langName && v.langName.toLowerCase().includes(query)) ||
      (v.traits && v.traits.toLowerCase().includes(query)) ||
      (v.family && v.family.toLowerCase().includes(query))
    );
  };

  // 1. Favourites Group (Pinned to Top)
  const favVoices = allVoices.filter((v) => favouriteVoiceIds.includes(v.id) && matches(v));
  if (favVoices.length > 0) {
    const favGroup = document.createElement("optgroup");
    favGroup.label = "⭐ Favourites (Pinned to Top)";
    favVoices.forEach((v) => {
      const opt = document.createElement("option");
      opt.value = v.id;
      opt.textContent = `⭐ ${v.name} (${v.family}, ${v.accent || v.langName}, ${v.gender})`;
      favGroup.appendChild(opt);
    });
    select.appendChild(favGroup);
  }

  // 2. Standard Groups
  const categories = [
    { label: "Deepgram Flux (v2 - Expressive, English)", filter: (v) => v.family === "Flux" },
    { label: "Deepgram Aura-2 (English - en)", filter: (v) => v.family === "Aura-2" && v.language === "en" },
    { label: "Deepgram Aura-2 (Spanish - es)", filter: (v) => v.family === "Aura-2" && v.language === "es" },
    { label: "Deepgram Aura-2 (French - fr)", filter: (v) => v.family === "Aura-2" && v.language === "fr" },
    { label: "Deepgram Aura-2 (German - de)", filter: (v) => v.family === "Aura-2" && v.language === "de" },
    { label: "Deepgram Aura-2 (Italian - it)", filter: (v) => v.family === "Aura-2" && v.language === "it" },
    { label: "Deepgram Aura-2 (Dutch - nl)", filter: (v) => v.family === "Aura-2" && v.language === "nl" },
    { label: "Deepgram Aura-2 (Japanese - ja)", filter: (v) => v.family === "Aura-2" && v.language === "ja" },
    { label: "Deepgram Aura 1 (Classic English)", filter: (v) => v.family === "Aura 1" }
  ];

  categories.forEach((cat) => {
    const groupVoices = allVoices.filter((v) => cat.filter(v) && matches(v));
    if (groupVoices.length > 0) {
      const groupEl = document.createElement("optgroup");
      groupEl.label = cat.label;
      groupVoices.forEach((v) => {
        const opt = document.createElement("option");
        opt.value = v.id;
        opt.textContent = `${v.name} (${v.accent || v.langName}, ${v.gender})${v.featured ? " ✨" : ""}`;
        groupEl.appendChild(opt);
      });
      select.appendChild(groupEl);
    }
  });

  const customOpt = document.createElement("option");
  customOpt.value = "custom";
  customOpt.textContent = "-- Custom Voice Handle --";
  select.appendChild(customOpt);

  syncDropdownToValue(select, currentValue);
  updateStarButtonState();
}

function updateVoiceMetadataBox() {
  const currentId = elements.voiceSelect.value.trim();
  const voice = allVoices.find((v) => v.id === currentId);
  if (voice) {
    const featBadge = voice.featured ? '<span class="voice-meta-tag featured">Featured</span>' : "";
    const langBadge = `<span class="voice-meta-tag lang">${voice.langName || voice.language}</span>`;
    const famBadge = `<span class="voice-meta-tag">${voice.family}</span>`;
    elements.voiceMetaBox.innerHTML = `
      ${featBadge}${famBadge}${langBadge}
      <strong>${voice.name}</strong> (${voice.accent || ""}, ${voice.gender}, ${voice.age || "Adult"})
      — <em>${voice.traits || "Conversational speech"}</em>
    `;
  } else {
    elements.voiceMetaBox.textContent = `Custom voice identifier: ${currentId || "(none)"}`;
  }
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

  updateStarButtonState();
  updateVoiceMetadataBox();
  updateJsonPreview();
  saveSettingsToStorage();
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

// ==========================================
// 2. Settings Persistence (Requirement 1)
// ==========================================
function saveSettingsToStorage() {
  try {
    const settingsState = {
      preset: elements.presetSelect.value,
      speed: parseFloat(elements.speedNum.value),
      expressivity: parseInt(elements.expressivityNum.value, 10),
      eot: parseFloat(elements.eotNum.value),
      eagerEot: parseFloat(elements.eagerEotNum.value),
      eotTimeout: parseInt(elements.eotTimeoutNum.value, 10),
      temp: parseFloat(elements.tempNum.value),
      silenceThreshold: parseInt(elements.silenceThresholdNum.value, 10) || 5,
      silenceReengage: elements.silenceReengageCheckbox.checked,
      voice: elements.voiceSelect.value.trim(),
      think: elements.thinkSelect.value.trim(),
      greeting: elements.greetingInput.value,
      prompt: elements.promptInput.value,
      hideUntilSpoken: elements.hideUntilSpokenCheckbox.checked,
      apiKey: elements.apiKeyInput.value.trim()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settingsState));
  } catch (err) {
    console.error("Failed to save settings to localStorage:", err);
  }
}

function loadSettingsFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      // Legacy API key migration
      const legacyKey = localStorage.getItem("deepgram_api_key");
      if (legacyKey) elements.apiKeyInput.value = legacyKey;
      return false;
    }

    const s = JSON.parse(raw);
    if (s.preset && presets[s.preset]) {
      elements.presetSelect.value = s.preset;
      elements.personaDesc.textContent = presets[s.preset].description;
    } else if (s.preset === "custom") {
      elements.presetSelect.value = "custom";
      elements.personaDesc.textContent = "Custom user-configured persona.";
    }

    if (s.speed !== undefined) setPairedValue(elements.speedSlider, elements.speedNum, s.speed);
    if (s.expressivity !== undefined) setPairedValue(elements.expressivitySlider, elements.expressivityNum, s.expressivity);
    const validEot = Math.min(1.0, Math.max(0.5, s.eot !== undefined ? s.eot : 0.58));
    setPairedValue(elements.eotSlider, elements.eotNum, validEot);
    const validEager = Math.min(validEot, Math.max(0.3, Math.min(0.9, s.eagerEot !== undefined ? s.eagerEot : 0.45)));
    setPairedValue(elements.eagerEotSlider, elements.eagerEotNum, validEager);
    if (s.eotTimeout !== undefined) setPairedValue(elements.eotTimeoutSlider, elements.eotTimeoutNum, s.eotTimeout);
    if (s.temp !== undefined) setPairedValue(elements.tempSlider, elements.tempNum, s.temp);

    if (s.silenceThreshold !== undefined) {
      setPairedValue(elements.silenceThresholdSlider, elements.silenceThresholdNum, s.silenceThreshold);
    }
    if (s.silenceReengage !== undefined) {
      elements.silenceReengageCheckbox.checked = s.silenceReengage;
    }

    if (s.voice) {
      elements.voiceSelect.value = s.voice;
      syncDropdownToValue(elements.voicePresetSelect, s.voice);
    }

    if (s.think) {
      elements.thinkSelect.value = s.think;
      syncDropdownToValue(elements.thinkPresetSelect, s.think);
    }

    if (s.greeting !== undefined) elements.greetingInput.value = s.greeting;
    if (s.prompt !== undefined) elements.promptInput.value = s.prompt;
    if (s.hideUntilSpoken !== undefined) elements.hideUntilSpokenCheckbox.checked = s.hideUntilSpoken;
    if (s.apiKey) elements.apiKeyInput.value = s.apiKey;

    updateStarButtonState();
    updateVoiceMetadataBox();
    return true;
  } catch (err) {
    console.error("Failed to load settings from storage:", err);
    return false;
  }
}

// Build settings object for Deepgram protocol
function getSettingsObject() {
  const speed = parseFloat(elements.speedNum.value);
  const expressivity = parseInt(elements.expressivityNum.value, 10);
  const eot = parseFloat(elements.eotNum.value);
  const eagerEot = parseFloat(elements.eagerEotNum.value);
  const eotTimeout = parseInt(elements.eotTimeoutNum.value, 10);
  const temp = parseFloat(elements.tempNum.value);
  const voice = elements.voiceSelect.value.trim() || "flux-conor-en";
  const isFlux = voice.startsWith("flux-");

  const speakProvider = {
    type: "deepgram",
    model: voice
  };

  if (isFlux) {
    speakProvider.version = "v2";
    speakProvider.speed = isNaN(speed) ? 1.3 : speed;
    if (!isNaN(expressivity)) {
      speakProvider.expressivity = expressivity;
    }
  } else {
    speakProvider.speed = isNaN(speed) ? 1.0 : speed;
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
        provider: (() => {
          const rawEot = isNaN(eot) ? 0.58 : eot;
          const validEot = Math.min(1.0, Math.max(0.5, rawEot));
          const rawEager = isNaN(eagerEot) ? 0.45 : eagerEot;
          const validEager = Math.min(validEot, Math.max(0.3, Math.min(0.9, rawEager)));
          return {
            type: "deepgram",
            version: "v2",
            model: "flux-general-en",
            eot_threshold: validEot,
            eager_eot_threshold: validEager,
            eot_timeout_ms: isNaN(eotTimeout) ? 2500 : eotTimeout
          };
        })()
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

// ==========================================
// 3. Real-Time Mid-Call Updates (Requirement 2)
// ==========================================
function isCallActive() {
  return activeWs && activeWs.readyState === WebSocket.OPEN;
}

function showMidCallNotice(text) {
  if (!elements.midCallNotice) return;
  elements.midCallNotice.textContent = text;
  elements.midCallNotice.style.display = "inline-flex";
  // Reset animation
  elements.midCallNotice.style.animation = "none";
  elements.midCallNotice.offsetHeight; // trigger reflow
  elements.midCallNotice.style.animation = "fadeInOut 3.2s forwards";
}

function scheduleMidCallUpdate(type, label = "") {
  if (!isCallActive()) return;

  clearTimeout(isMidCallUpdateDebounceTimer);
  isMidCallUpdateDebounceTimer = setTimeout(() => {
    dispatchMidCallUpdate(type, label);
  }, 120);
}

function dispatchMidCallUpdate(type, label = "") {
  if (!isCallActive()) return;

  const currentSettings = getSettingsObject();

  if (type === "speak" || type === "all") {
    activeWs.send(JSON.stringify({
      type: "update_speak",
      speak: currentSettings.agent.speak
    }));
  }

  if (type === "listen" || type === "all") {
    activeWs.send(JSON.stringify({
      type: "update_listen",
      listen: currentSettings.agent.listen
    }));
  }

  if (type === "think" || type === "all") {
    activeWs.send(JSON.stringify({
      type: "update_think",
      think: currentSettings.agent.think
    }));
  }

  showMidCallNotice(`⚡ Applied ${label || type} mid-call!`);
}

// ==========================================
// 4. Smart Silence Re-Engagement Watchdog (Requirement 3)
// ==========================================
function clearSilenceWatchdog() {
  clearTimeout(silenceTimeoutId);
  clearInterval(silenceCountdownInterval);
  silenceTimeoutId = null;
  silenceCountdownInterval = null;
  elements.silencePill.style.display = "none";
  elements.silencePill.classList.remove("task-active");
}

// Detect if last turns constitute an assigned task that the user agreed to do
function detectAssignedTask(agentUtterance, userUtterance) {
  if (!agentUtterance || !userUtterance) return { isTask: false, durationSec: 5 };

  const agentLower = agentUtterance.toLowerCase();
  const userLower = userUtterance.toLowerCase();

  // Task imperative cues from agent
  const taskActionKeywords = [
    "pushup", "push-up", "jumping jack", "squat", "water", "drink", "mirror",
    "wash", "brush", "bed", "get out of bed", "stand up", "walk", "stretch",
    "shoes", "touch", "count", "do this", "task", "run", "grab", "bring", "check",
    "exercise", "breathe", "breath", "minute", "seconds"
  ];

  // User agreement / acknowledgment cues
  const userAgreementKeywords = [
    "ok", "okay", "i will", "i'm going", "im going", "i am going", "doing that",
    "doing it", "on it", "alright", "give me a sec", "give me a minute",
    "give me 30", "working on it", "starting now", "wait a minute", "hold on",
    "one sec", "one minute", "let me do"
  ];

  const agentGaveTask = taskActionKeywords.some((k) => agentLower.includes(k));
  const userAgreed = userAgreementKeywords.some((k) => userLower.includes(k));

  if (agentGaveTask && userAgreed) {
    // Attempt duration extraction from user or agent dialogue
    const textCombined = `${agentLower} ${userLower}`;
    let estimatedSec = 50; // default estimated duration for tasks

    if (textCombined.includes("2 minute") || textCombined.includes("two minute")) {
      estimatedSec = 120;
    } else if (textCombined.includes("minute") || textCombined.includes("60 sec")) {
      estimatedSec = 60;
    } else if (textCombined.includes("30 sec") || textCombined.includes("thirty sec")) {
      estimatedSec = 30;
    } else if (textCombined.includes("45 sec")) {
      estimatedSec = 45;
    } else if (textCombined.includes("10 push") || textCombined.includes("ten push")) {
      estimatedSec = 35;
    } else if (textCombined.includes("20 push") || textCombined.includes("twenty push")) {
      estimatedSec = 50;
    }

    return { isTask: true, durationSec: estimatedSec };
  }

  return { isTask: false, durationSec: 5 };
}

function startSilenceWatchdog() {
  clearSilenceWatchdog();

  // Check if feature is enabled and call is actively underway
  if (!elements.silenceReengageCheckbox.checked || !isCallActive()) return;

  const taskEvaluation = detectAssignedTask(lastAgentUtterance, lastUserUtterance);
  let timeoutSec;

  if (taskEvaluation.isTask) {
    timeoutSec = taskEvaluation.durationSec;
    elements.silencePill.classList.add("task-active");
    elements.silencePill.textContent = `⏳ Task active: ~${timeoutSec}s estimated before check-in`;
  } else {
    timeoutSec = parseInt(elements.silenceThresholdNum.value, 10) || 5;
    elements.silencePill.classList.remove("task-active");
    elements.silencePill.textContent = `⏱️ User silent: ${timeoutSec}s threshold`;
  }

  elements.silencePill.style.display = "block";
  silenceRemainingSec = timeoutSec;

  silenceCountdownInterval = setInterval(() => {
    silenceRemainingSec = Math.max(0, silenceRemainingSec - 1);
    if (taskEvaluation.isTask) {
      elements.silencePill.textContent = `⏳ Task in progress (${silenceRemainingSec}s remaining)...`;
    } else {
      elements.silencePill.textContent = `⏱️ Silence: ${silenceRemainingSec}s before re-engage`;
    }
  }, 1000);

  silenceTimeoutId = setTimeout(() => {
    triggerSilenceReengagement(taskEvaluation.isTask, timeoutSec);
  }, timeoutSec * 1000);
}

function triggerSilenceReengagement(wasTask, durationSec) {
  clearSilenceWatchdog();
  if (!isCallActive()) return;

  let promptInstruction = "";
  if (wasTask) {
    promptInstruction = `[System Event: ${durationSec} seconds have elapsed since the user committed to doing the task ("${lastUserUtterance.replace(/"/g, "'")}"). In character, check in on whether they have finished the task and demand a status report immediately!]`;
  } else {
    promptInstruction = `[System Event: The user has been completely silent and has not responded for ${durationSec} seconds after you said: "${lastAgentUtterance.replace(/"/g, "'")}". As a real person being blatantly ignored, demand immediately in character that they answer you!]`;
  }

  // Inject prompt directly to Deepgram Voice Agent via WebSocket
  activeWs.send(JSON.stringify({
    type: "inject_user_message",
    content: promptInstruction
  }));

  // Append subtle status badge in transcript
  const badge = document.createElement("div");
  badge.className = "transcript-system-event";
  badge.textContent = `⏱️ Silence threshold reached (${durationSec}s) — prompting agent to re-engage`;
  elements.transcriptBox.appendChild(badge);
  elements.transcriptBox.scrollTop = elements.transcriptBox.scrollHeight;
}

// ==========================================
// 5. Input Binding & Event Listeners
// ==========================================
function bindPairedInput(slider, numInput, onUpdate) {
  slider.addEventListener("input", (e) => {
    numInput.value = e.target.value;
    updateJsonPreview();
    saveSettingsToStorage();
    if (onUpdate) onUpdate();
  });
  numInput.addEventListener("input", (e) => {
    const val = parseFloat(e.target.value);
    if (!isNaN(val)) {
      slider.value = val;
      updateJsonPreview();
      saveSettingsToStorage();
      if (onUpdate) onUpdate();
    }
  });
}

function attachEventListeners() {
  // Preset Dropdown
  elements.presetSelect.addEventListener("change", (e) => {
    if (e.target.value !== "custom") {
      loadPreset(e.target.value);
    } else {
      elements.personaDesc.textContent = "Custom user-configured persona.";
    }
    saveSettingsToStorage();
    scheduleMidCallUpdate("all", "Preset persona");
  });

  // Sliders with real-time mid-call dispatch
  bindPairedInput(elements.speedSlider, elements.speedNum, () => {
    scheduleMidCallUpdate("speak", `Speed ${elements.speedNum.value}x`);
  });

  bindPairedInput(elements.expressivitySlider, elements.expressivityNum, () => {
    scheduleMidCallUpdate("speak", `Expressivity ${elements.expressivityNum.value}`);
  });

  bindPairedInput(elements.eotSlider, elements.eotNum, () => {
    scheduleMidCallUpdate("listen", `EOT ${elements.eotNum.value}`);
  });

  bindPairedInput(elements.eagerEotSlider, elements.eagerEotNum, () => {
    scheduleMidCallUpdate("listen", `Eager EOT ${elements.eagerEotNum.value}`);
  });

  bindPairedInput(elements.eotTimeoutSlider, elements.eotTimeoutNum, () => {
    scheduleMidCallUpdate("listen", `Timeout ${elements.eotTimeoutNum.value}ms`);
  });

  bindPairedInput(elements.tempSlider, elements.tempNum, () => {
    scheduleMidCallUpdate("think", `Temp ${elements.tempNum.value}`);
  });

  bindPairedInput(elements.silenceThresholdSlider, elements.silenceThresholdNum, () => {
    saveSettingsToStorage();
    if (isCallActive() && !isAudioPlaying) {
      startSilenceWatchdog();
    }
  });

  elements.silenceReengageCheckbox.addEventListener("change", () => {
    saveSettingsToStorage();
    if (isCallActive()) {
      if (elements.silenceReengageCheckbox.checked && !isAudioPlaying) {
        startSilenceWatchdog();
      } else {
        clearSilenceWatchdog();
      }
    }
  });

  // Voice Catalog Filter & Search
  elements.voiceSearchInput.addEventListener("input", (e) => {
    renderVoiceOptions(e.target.value);
  });

  // Star / Favourite Button
  elements.starVoiceBtn.addEventListener("click", toggleFavouriteCurrentVoice);

  // Voice Presets Dropdown
  elements.voicePresetSelect.addEventListener("change", (e) => {
    if (e.target.value !== "custom") {
      elements.voiceSelect.value = e.target.value;
      updateStarButtonState();
      updateVoiceMetadataBox();
      updateJsonPreview();
      saveSettingsToStorage();
      scheduleMidCallUpdate("speak", `Voice ${e.target.value}`);
    }
  });

  elements.voiceSelect.addEventListener("input", (e) => {
    syncDropdownToValue(elements.voicePresetSelect, e.target.value.trim());
    updateStarButtonState();
    updateVoiceMetadataBox();
    updateJsonPreview();
    saveSettingsToStorage();
    scheduleMidCallUpdate("speak", `Voice ${e.target.value.trim()}`);
  });

  // LLM Model Dropdown
  elements.thinkPresetSelect.addEventListener("change", (e) => {
    if (e.target.value !== "custom") {
      elements.thinkSelect.value = e.target.value;
      updateJsonPreview();
      saveSettingsToStorage();
      scheduleMidCallUpdate("think", `Model ${e.target.value}`);
    }
  });

  elements.thinkSelect.addEventListener("input", (e) => {
    syncDropdownToValue(elements.thinkPresetSelect, e.target.value.trim());
    updateJsonPreview();
    saveSettingsToStorage();
    scheduleMidCallUpdate("think", `Model ${e.target.value.trim()}`);
  });

  elements.greetingInput.addEventListener("input", () => {
    updateJsonPreview();
    saveSettingsToStorage();
  });

  elements.promptInput.addEventListener("input", () => {
    updateJsonPreview();
    saveSettingsToStorage();
    scheduleMidCallUpdate("think", "Prompt update");
  });

  elements.hideUntilSpokenCheckbox.addEventListener("change", saveSettingsToStorage);

  elements.apiKeyInput.addEventListener("input", saveSettingsToStorage);

  elements.saveKeyBtn.addEventListener("click", () => {
    const key = elements.apiKeyInput.value.trim();
    if (key) {
      saveSettingsToStorage();
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
  // Filter out internal silence trigger prompts from user dialogue bubbles
  if (sender === "user" && text.startsWith("[System Event:")) {
    return;
  }

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
    lastAgentUtterance = pendingAgentUtterance.trim();
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

// ==========================================
// 6. Live Audio Call Handling
// ==========================================
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
  isAudioPlaying = false;
  clearSilenceWatchdog();

  try {
    // Setup AudioContext (48kHz sample rate)
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 48000 });
    if (audioCtx.state === "suspended") {
      await audioCtx.resume();
    }
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

    // Route mic through a zero-gain mute node to destination so Chrome keeps
    // onaudioprocess running WITHOUT feedback loop / speaker blast / self-interruption!
    const muteGain = audioCtx.createGain();
    muteGain.gain.value = 0;
    scriptProcessor.connect(muteGain);
    muteGain.connect(audioCtx.destination);

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
      setBadge("CONNECTING", "status-connecting");
    } else if (msg.status === "settings_sent") {
      const greeting = elements.greetingInput.value.trim();
      if (greeting) {
        lastAgentUtterance = greeting;
      }
    } else if (msg.status === "settings_applied") {
      setBadge("IN CALL", "status-active");
      const greeting = elements.greetingInput.value.trim();
      if (greeting) {
        if (!elements.hideUntilSpokenCheckbox.checked) {
          appendTranscript("agent", greeting);
        } else {
          pendingAgentUtterance = greeting;
        }
      }
    } else if (msg.status === "update_sent") {
      showMidCallNotice(`✓ ${msg.updateType} acknowledged`);
    } else if (msg.status === "deepgram_closed") {
      console.warn("[Deepgram Closed]", msg);
      if (msg.code !== 1000 || msg.reason) {
        appendTranscript("agent", `⚠️ Deepgram disconnected: ${msg.reason || `Code ${msg.code}`}`);
      }
      endCall();
    }
  } else if (msg.type === "deepgram_event") {
    const data = msg.data;
    if (data.type === "Error") {
      console.error("[Deepgram Error]", data);
      const errText = data.description || data.message || "Deepgram rejected settings";
      appendTranscript("agent", `⚠️ Deepgram Error: ${errText}`);
      alert(`Deepgram Error: ${errText}`);
      endCall();
      return;
    } else if (data.type === "SettingsApplied") {
      setBadge("IN CALL", "status-active");
    } else if (data.type === "ConversationText") {
      if (data.role === "user") {
        // User finished speaking, reveal any leftover agent utterance first
        revealPendingAgentUtterance();
        lastUserUtterance = data.content;
        clearSilenceWatchdog();
        appendTranscript("user", data.content);
        setBadge("AGENT THINKING", "status-connecting");
      } else if (data.role === "agent" || data.role === "assistant") {
        clearSilenceWatchdog();
        isAudioPlaying = true;
        if (!elements.hideUntilSpokenCheckbox.checked) {
          appendTranscript("agent", data.content);
          lastAgentUtterance = data.content;
        } else {
          // Buffer the agent utterance and reveal ONLY when playback completes
          pendingAgentUtterance += (pendingAgentUtterance ? " " : "") + data.content;
        }
        setBadge("SPEAKING", "status-speaking");
      }
    } else if (data.type === "UserStartedSpeaking") {
      // User started talking; silence broken
      clearSilenceWatchdog();
      revealPendingAgentUtterance();
      elements.speakingPill.style.display = "none";
      setBadge("LISTENING", "status-active");
    } else if (data.type === "AgentStartedSpeaking") {
      clearSilenceWatchdog();
      isAudioPlaying = true;
      elements.speakingPill.style.display = "block";
      setBadge("SPEAKING", "status-speaking");
      if (audioCtx && audioCtx.state === "suspended") {
        audioCtx.resume().catch(() => {});
      }
    } else if (data.type === "AgentAudioDone") {
      // Deepgram finished sending audio frames; wait for audio playback queue to complete
      if (audioCtx) {
        const remainingDelayMs = Math.max(0, (nextPlayTime - audioCtx.currentTime) * 1000) + 120;
        clearTimeout(agentAudioDoneTimer);
        agentAudioDoneTimer = setTimeout(() => {
          isAudioPlaying = false;
          elements.speakingPill.style.display = "none";
          revealPendingAgentUtterance();
          setBadge("IN CALL", "status-active");
          // Agent is finished speaking, start the silence watchdog!
          startSilenceWatchdog();
        }, remainingDelayMs);
      } else {
        isAudioPlaying = false;
        revealPendingAgentUtterance();
        elements.speakingPill.style.display = "none";
        startSilenceWatchdog();
      }
    } else if (data.type === "EndOfTurn") {
      setBadge("AGENT THINKING", "status-connecting");
    } else if (data.type === "SpeakUpdated") {
      showMidCallNotice("✓ Voice & speed updated live!");
    } else if (data.type === "ListenUpdated") {
      showMidCallNotice("✓ Turn thresholds updated live!");
    } else if (data.type === "ThinkUpdated") {
      showMidCallNotice("✓ Persona brain updated live!");
    }
  } else if (msg.type === "error") {
    alert(msg.error);
    endCall();
  }
}

async function playPcmChunk(chunk, sampleRate = 24000) {
  if (!audioCtx) return;

  if (audioCtx.state === "suspended") {
    try {
      await audioCtx.resume();
    } catch (e) {
      console.warn("Could not resume AudioContext:", e);
    }
  }

  let arrayBuffer;
  if (chunk instanceof Blob) {
    arrayBuffer = await chunk.arrayBuffer();
  } else if (chunk instanceof ArrayBuffer) {
    arrayBuffer = chunk;
  } else if (chunk && chunk.buffer instanceof ArrayBuffer) {
    arrayBuffer = chunk.buffer;
  } else {
    console.warn("Unexpected chunk type:", chunk);
    return;
  }

  if (!arrayBuffer || arrayBuffer.byteLength < 2) return;

  // Multiple of 2 bytes required for 16-bit PCM
  const sampleCount = Math.floor(arrayBuffer.byteLength / 2);
  const int16 = new Int16Array(arrayBuffer, 0, sampleCount);
  const float32 = new Float32Array(sampleCount);
  for (let i = 0; i < sampleCount; i++) {
    float32[i] = int16[i] / 32768.0;
  }

  const audioBuffer = audioCtx.createBuffer(1, sampleCount, sampleRate);
  audioBuffer.getChannelData(0).set(float32);

  const source = audioCtx.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioCtx.destination);

  const now = audioCtx.currentTime;
  let startTime = nextPlayTime;
  if (startTime < now || startTime > now + 1.0) {
    startTime = now + 0.02; // Small 20ms lookahead to avoid glitching
  }
  source.start(startTime);
  nextPlayTime = startTime + audioBuffer.duration;

  activeAudioSourcesCount++;
  isAudioPlaying = true;
  elements.speakingPill.style.display = "block";

  source.onended = () => {
    activeAudioSourcesCount = Math.max(0, activeAudioSourcesCount - 1);
    // When last scheduled buffer ends playback, reveal dialogue if no more audio queued
    if (activeAudioSourcesCount === 0 && (audioCtx.currentTime >= nextPlayTime - 0.08)) {
      elements.speakingPill.style.display = "none";
      revealPendingAgentUtterance();
      isAudioPlaying = false;
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
  clearSilenceWatchdog();
  isAudioPlaying = false;

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

// Fallback catalog in case /api/voices is unreachable
function getFallbackVoices() {
  return [
    { id: "flux-miles-en", name: "Miles", family: "Flux", language: "en", langName: "English", accent: "American", gender: "Male", age: "Adult", traits: "Clear, calm, professional, confident", featured: true },
    { id: "flux-conor-en", name: "Conor", family: "Flux", language: "en", langName: "English", accent: "British", gender: "Male", age: "Mature", traits: "Confident, deep, military-ready", featured: false },
    { id: "flux-kit-en", name: "Kit", family: "Flux", language: "en", langName: "English", accent: "British", gender: "Male", age: "Young Adult", traits: "Friendly, energetic, crisp", featured: true },
    { id: "flux-hannah-en", name: "Hannah", family: "Flux", language: "en", langName: "English", accent: "American", gender: "Female", age: "Young", traits: "Clear, confident, pleasant", featured: true },
    { id: "aura-2-thalia-en", name: "Thalia", family: "Aura-2", language: "en", langName: "English", accent: "American", gender: "Female", age: "Adult", traits: "Clear, confident, energetic", featured: true },
    { id: "aura-2-nestor-es", name: "Nestor", family: "Aura-2", language: "es", langName: "Spanish", accent: "Peninsular", gender: "Male", age: "Adult", traits: "Calm, professional", featured: true }
  ];
}

window.addEventListener("DOMContentLoaded", init);
