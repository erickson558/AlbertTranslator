const COMMON_LANGUAGES = [
  { name: "Espanol", code: "es" },
  { name: "Ingles", code: "en" },
  { name: "Frances", code: "fr" },
  { name: "Aleman", code: "de" },
  { name: "Italiano", code: "it" },
  { name: "Portugues", code: "pt" },
  { name: "Ruso", code: "ru" },
  { name: "Japones", code: "ja" },
  { name: "Coreano", code: "ko" },
  { name: "Chino", code: "zh" },
  { name: "Arabe", code: "ar" },
  { name: "Hindi", code: "hi" },
  { name: "Neerlandes", code: "nl" },
  { name: "Turco", code: "tr" },
  { name: "Polaco", code: "pl" },
  { name: "Ucraniano", code: "uk" },
  { name: "Sueco", code: "sv" },
  { name: "Griego", code: "el" },
  { name: "Hebreo", code: "he" },
];

const SOURCE_LANGUAGES = [{ name: "Detectar automaticamente", code: "auto" }, ...COMMON_LANGUAGES];
const TARGET_LANGUAGES = [...COMMON_LANGUAGES];

const sourceSelect = document.getElementById("source-language");
const targetSelect = document.getElementById("target-language");
const transcriptionBackendSelect = document.getElementById("transcription-backend");
const backendNote = document.getElementById("backend-note");
const copyTranscriptBtn = document.getElementById("copy-transcript");
const copyTranslationBtn = document.getElementById("copy-translation");

const startBtn = document.getElementById("start-listening");
const stopBtn = document.getElementById("stop-listening");
const clearBtn = document.getElementById("clear-output");
const swapBtn = document.getElementById("swap-languages");

const transcriptOutput = document.getElementById("transcript-output");
const translationOutput = document.getElementById("translation-output");
const statusBox = document.getElementById("status");
const errorBox = document.getElementById("error-box");

const API_BASE = resolveApiBaseUrl();
const CHUNK_MS = Number(window.APP_CONFIG?.audioChunkMs) || 2200;
const TARGET_SAMPLE_RATE = 16000;
const MAX_QUEUE_CHUNKS = 10;
const TIMER_FLUSH_MS = Math.max(600, Math.min(CHUNK_MS, 1200));
const MIN_BUFFER_MS_TO_FLUSH = 650;
const SILENCE_FLUSH_MS = 450;
const SPEECH_RMS_THRESHOLD = 0.008;
const MAX_TEXT_QUEUE_ITEMS = 40;
const BROWSER_STT_RESTART_DELAY_MS = 160;
const SpeechRecognitionCtor =
  window.SpeechRecognition || window.webkitSpeechRecognition || null;

let listening = false;
let mediaStream = null;
let audioContext = null;
let sourceNode = null;
let processorNode = null;
let muteGainNode = null;
let chunkTimer = null;
let pcmBuffers = [];
let sourceSampleRate = TARGET_SAMPLE_RATE;
let bufferedSamples = 0;
let silenceMs = 0;
let bufferHasSpeech = false;

let uploadQueue = [];
let processingQueue = false;
let queueDropWarned = false;
let backendChosenByUser = false;
let usingBrowserSpeechRecognition = false;
let browserSpeechRecognition = null;
let browserSpeechRestartTimer = null;
let browserInterimTranscript = "";
let textTranslationQueue = [];
let processingTextQueue = false;
let translationTypeTimer = null;
let translationTypeTarget = "";

buildLanguageOptions();
wireEvents();
initializeBackendControl();
void refreshBackendFromServer();

function buildLanguageOptions() {
  if (sourceSelect) {
    sourceSelect.innerHTML = "";
    SOURCE_LANGUAGES.forEach((language) => {
      const option = document.createElement("option");
      option.value = language.code;
      option.textContent = formatLanguage(language);
      sourceSelect.appendChild(option);
    });
    sourceSelect.value = "auto";
  }

  if (targetSelect) {
    targetSelect.innerHTML = "";
    TARGET_LANGUAGES.forEach((language) => {
      const option = document.createElement("option");
      option.value = language.code;
      option.textContent = formatLanguage(language);
      targetSelect.appendChild(option);
    });
    targetSelect.value = "en";
  }
}

function wireEvents() {
  startBtn.addEventListener("click", startListening);
  stopBtn.addEventListener("click", stopListening);
  clearBtn.addEventListener("click", clearOutputs);
  swapBtn.addEventListener("click", swapLanguages);
  if (sourceSelect) {
    sourceSelect.addEventListener("change", () => {
      if (!listening || !usingBrowserSpeechRecognition || !browserSpeechRecognition) {
        return;
      }
      const selected = currentSourceLanguage();
      browserSpeechRecognition.lang = resolveRecognitionLanguage(selected.code);
    });
  }
  if (copyTranscriptBtn) {
    copyTranscriptBtn.addEventListener("click", () => {
      copyTextareaContent(
        transcriptOutput,
        copyTranscriptBtn,
        "No hay transcripcion para copiar."
      );
    });
  }
  if (copyTranslationBtn) {
    copyTranslationBtn.addEventListener("click", () => {
      copyTextareaContent(
        translationOutput,
        copyTranslationBtn,
        "No hay traduccion para copiar."
      );
    });
  }
  if (transcriptionBackendSelect) {
    transcriptionBackendSelect.addEventListener("change", () => {
      backendChosenByUser = true;
      updateBackendNote(currentTranscriptionBackend());
    });
  }
}

function formatLanguage(language) {
  return `${language.name} (${language.code})`;
}

function getLanguageByCode(options, code, fallbackCode) {
  const normalized = String(code || "").trim().toLowerCase();
  if (normalized) {
    const byCode = options.find((item) => item.code === normalized);
    if (byCode) {
      return byCode;
    }
  }
  return options.find((item) => item.code === fallbackCode) || options[0];
}

function normalizeBrowserHost(host) {
  const normalized = (host || "").trim().toLowerCase();
  if (!normalized || normalized === "0.0.0.0" || normalized === "::" || normalized === "*") {
    return "127.0.0.1";
  }
  return host;
}

function resolveApiBaseUrl() {
  const configured = (window.APP_CONFIG?.apiBaseUrl || "").trim();
  if (configured) {
    return configured.replace(/\/+$/, "");
  }

  if (window.location?.origin && window.location.origin !== "null") {
    return window.location.origin;
  }

  const host = normalizeBrowserHost(window.APP_CONFIG?.fallbackHost || "127.0.0.1");
  const port = Number(window.APP_CONFIG?.fallbackPort) || 8765;
  return `http://${host}:${port}`;
}

function apiUrl(path) {
  return `${API_BASE}${path}`;
}

function currentSourceLanguage() {
  return getLanguageByCode(SOURCE_LANGUAGES, sourceSelect?.value, "auto");
}

function currentTargetLanguage() {
  return getLanguageByCode(TARGET_LANGUAGES, targetSelect?.value, "en");
}

function currentTranscriptionBackend() {
  const raw = String(transcriptionBackendSelect?.value || "").trim().toLowerCase();
  return raw === "faster_whisper" ? "faster_whisper" : "google";
}

function initializeBackendControl() {
  if (!transcriptionBackendSelect) {
    return;
  }

  const configured = String(window.APP_CONFIG?.transcriptionBackend || "").trim().toLowerCase();
  transcriptionBackendSelect.value = configured === "faster_whisper" ? "faster_whisper" : "google";
  updateBackendNote(currentTranscriptionBackend());
}

async function refreshBackendFromServer() {
  try {
    const response = await fetch(apiUrl("/api/health"), { cache: "no-store" });
    if (!response.ok) {
      return;
    }
    const payload = await parseJsonResponse(response);
    const backend = String(payload?.transcription?.backend || "").trim().toLowerCase();
    if (!backendChosenByUser && transcriptionBackendSelect && (backend === "google" || backend === "faster_whisper")) {
      transcriptionBackendSelect.value = backend;
    }
    updateBackendNote(currentTranscriptionBackend());
  } catch (_error) {
    // ignorado
  }
}

function updateBackendNote(backend) {
  if (!backendNote) {
    return;
  }

  if (backend === "google") {
    if (SpeechRecognitionCtor) {
      backendNote.textContent =
        "Usando Google Speech en vivo desde el navegador (transcripcion casi en tiempo real). Para mayor precision, fija el idioma origen en lugar de auto.";
      return;
    }
    backendNote.textContent =
      "Usando Google Speech por bloques (tu navegador no soporta modo en vivo).";
    return;
  }

  backendNote.textContent = "Usando faster_whisper local (recomendado para uso sin conexion).";
}

function setStatus(state, text) {
  statusBox.textContent = text;
  statusBox.classList.remove("idle", "listening", "processing");
  statusBox.classList.add(state);
}

function showError(message) {
  if (!message) {
    errorBox.hidden = true;
    errorBox.textContent = "";
    return;
  }

  errorBox.hidden = false;
  errorBox.textContent = message;
}

function clearOutputs() {
  resetTranslationTypewriter();
  browserInterimTranscript = "";
  transcriptOutput.value = "";
  translationOutput.value = "";
  showError("");
}

function swapLanguages() {
  const source = currentSourceLanguage();
  const target = currentTargetLanguage();

  if (source.code === "auto") {
    showError("No se puede intercambiar cuando el idioma origen es automatico.");
    return;
  }

  if (sourceSelect) {
    sourceSelect.value = target.code;
  }
  if (targetSelect) {
    targetSelect.value = source.code;
  }
  showError("");
}

async function startListening() {
  if (listening) {
    return;
  }

  showError("");

  const serverReady = await checkServerReady();
  if (!serverReady) {
    showError(
      "No hay conexion con el servidor local. Abre AlbertTranslator e inicia el servidor. Si falla, revisa alberttranslator.log junto al .exe."
    );
    return;
  }

  const source = currentSourceLanguage();
  const target = currentTargetLanguage();
  if (!target || target.code === "auto") {
    showError("Selecciona un idioma destino valido.");
    return;
  }

  if (sourceSelect) {
    sourceSelect.value = source.code;
  }
  if (targetSelect) {
    targetSelect.value = target.code;
  }

  listening = true;
  startBtn.disabled = true;
  stopBtn.disabled = false;
  setStatus("processing", "Iniciando escucha...");

  uploadQueue = [];
  processingQueue = false;
  queueDropWarned = false;
  textTranslationQueue = [];
  processingTextQueue = false;
  pcmBuffers = [];
  bufferedSamples = 0;
  silenceMs = 0;
  bufferHasSpeech = false;
  browserInterimTranscript = "";

  try {
    if (shouldUseBrowserSpeechRecognition()) {
      await ensureMicrophonePermissionForLive();
      startBrowserSpeechRecognition(source.code);
      setStatus("listening", "Escuchando (Google en vivo)");
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error("Tu navegador no permite capturar microfono.");
    }

    const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextCtor) {
      throw new Error("Tu navegador no soporta AudioContext para captura de voz.");
    }

    await initializeAudioPipeline(AudioContextCtor);
    chunkTimer = setInterval(() => {
      flushCapturedAudio(false);
    }, TIMER_FLUSH_MS);

    setStatus("listening", "Escuchando");
  } catch (error) {
    listening = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    setStatus("idle", "Inactivo");
    stopBrowserSpeechRecognition();
    await teardownAudioPipeline();
    showError(error.message || "No se pudo iniciar la captura de audio.");
  }
}

async function ensureMicrophonePermissionForLive() {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error("Tu navegador no permite capturar microfono.");
  }

  let probeStream = null;
  try {
    probeStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (error) {
    throw new Error(
      `No se pudo acceder al microfono para transcripcion en vivo. Detalle: ${error.message || error}`
    );
  } finally {
    if (probeStream) {
      probeStream.getTracks().forEach((track) => track.stop());
    }
  }
}

async function stopListening() {
  if (!listening) {
    return;
  }

  listening = false;
  startBtn.disabled = false;
  stopBtn.disabled = true;
  setStatus("processing", "Deteniendo...");

  if (usingBrowserSpeechRecognition) {
    stopBrowserSpeechRecognition();
    if (processingTextQueue || textTranslationQueue.length > 0) {
      setStatus("processing", "Procesando traducciones finales");
    } else {
      setStatus("idle", "Inactivo");
    }
    return;
  }

  if (chunkTimer) {
    clearInterval(chunkTimer);
    chunkTimer = null;
  }

  flushCapturedAudio(true);
  await teardownAudioPipeline();

  if (processingQueue || uploadQueue.length > 0) {
    setStatus("processing", "Procesando bloques finales");
  } else {
    setStatus("idle", "Inactivo");
  }
}

function shouldUseBrowserSpeechRecognition() {
  return currentTranscriptionBackend() === "google" && Boolean(SpeechRecognitionCtor);
}

function startBrowserSpeechRecognition(sourceLanguageCode) {
  if (!SpeechRecognitionCtor) {
    throw new Error(
      "Tu navegador no soporta transcripcion en vivo. Cambia a faster_whisper o usa Chrome/Edge."
    );
  }

  if (browserSpeechRestartTimer) {
    clearTimeout(browserSpeechRestartTimer);
    browserSpeechRestartTimer = null;
  }

  if (browserSpeechRecognition) {
    try {
      browserSpeechRecognition.stop();
    } catch (_error) {
      // ignorado
    }
  }

  usingBrowserSpeechRecognition = true;
  browserSpeechRecognition = new SpeechRecognitionCtor();
  browserSpeechRecognition.continuous = true;
  browserSpeechRecognition.interimResults = true;
  browserSpeechRecognition.maxAlternatives = 1;
  browserSpeechRecognition.lang = resolveRecognitionLanguage(sourceLanguageCode);
  browserSpeechRecognition.onresult = handleBrowserSpeechResult;
  browserSpeechRecognition.onerror = handleBrowserSpeechError;
  browserSpeechRecognition.onend = handleBrowserSpeechEnd;

  try {
    browserSpeechRecognition.start();
  } catch (error) {
    usingBrowserSpeechRecognition = false;
    browserSpeechRecognition = null;
    throw new Error(
      `No se pudo iniciar la transcripcion en vivo de Google. Detalle: ${error.message || error}`
    );
  }
}

function stopBrowserSpeechRecognition() {
  usingBrowserSpeechRecognition = false;

  if (browserSpeechRestartTimer) {
    clearTimeout(browserSpeechRestartTimer);
    browserSpeechRestartTimer = null;
  }

  clearTrailingInterimLine();

  if (!browserSpeechRecognition) {
    return;
  }

  const recognition = browserSpeechRecognition;
  browserSpeechRecognition = null;
  recognition.onresult = null;
  recognition.onerror = null;
  recognition.onend = null;

  try {
    recognition.stop();
  } catch (_error) {
    // ignorado
  }
}

function handleBrowserSpeechResult(event) {
  if (!listening || !usingBrowserSpeechRecognition) {
    return;
  }

  let interimText = "";

  for (let index = event.resultIndex; index < event.results.length; index += 1) {
    const result = event.results[index];
    const bestResult = result?.[0];
    const text = cleanTranscript(bestResult?.transcript || "");
    if (!text) {
      continue;
    }

    if (result.isFinal) {
      setTranscriptInterimPreview("");
      if (lastTextareaLine(transcriptOutput) !== text) {
        appendLine(transcriptOutput, text);
        enqueueTextForTranslation(text);
      }
    } else {
      interimText += (interimText ? " " : "") + text;
    }
  }

  setTranscriptInterimPreview(interimText);
}

function handleBrowserSpeechError(event) {
  const code = String(event?.error || "").trim().toLowerCase();

  if (!listening || !usingBrowserSpeechRecognition) {
    return;
  }

  if (!code || code === "aborted" || code === "no-speech") {
    return;
  }

  showError(mapSpeechRecognitionError(code));

  if (code === "not-allowed" || code === "service-not-allowed" || code === "audio-capture") {
    void stopListening();
  }
}

function handleBrowserSpeechEnd() {
  if (!listening || !usingBrowserSpeechRecognition || !browserSpeechRecognition) {
    return;
  }

  if (browserSpeechRestartTimer) {
    clearTimeout(browserSpeechRestartTimer);
  }

  browserSpeechRestartTimer = setTimeout(() => {
    if (!listening || !usingBrowserSpeechRecognition || !browserSpeechRecognition) {
      return;
    }

    try {
      browserSpeechRecognition.start();
    } catch (_error) {
      // Si ya esta arrancando/reiniciando, dejamos que el siguiente onend reintente.
    }
  }, BROWSER_STT_RESTART_DELAY_MS);
}

function resolveRecognitionLanguage(sourceLanguageCode) {
  const aliases = {
    ar: "ar-SA",
    de: "de-DE",
    el: "el-GR",
    en: "en-US",
    es: "es-ES",
    fr: "fr-FR",
    he: "he-IL",
    hi: "hi-IN",
    it: "it-IT",
    ja: "ja-JP",
    ko: "ko-KR",
    nl: "nl-NL",
    pl: "pl-PL",
    pt: "pt-PT",
    ru: "ru-RU",
    sv: "sv-SE",
    tr: "tr-TR",
    uk: "uk-UA",
    zh: "zh-CN",
  };

  const sourceCode = String(sourceLanguageCode || "").trim().toLowerCase();
  if (sourceCode && sourceCode !== "auto") {
    return aliases[sourceCode] || `${sourceCode}-${sourceCode.toUpperCase()}`;
  }

  const hint = bestBrowserLanguageHint();
  return aliases[hint] || `${hint}-${hint.toUpperCase()}`;
}

function bestBrowserLanguageHint() {
  const allowed = new Set(COMMON_LANGUAGES.map((lang) => lang.code));
  const rawLanguages = Array.isArray(navigator.languages)
    ? navigator.languages
    : [navigator.language];

  for (const raw of rawLanguages) {
    const code = String(raw || "")
      .trim()
      .toLowerCase()
      .split("-")[0];
    if (allowed.has(code)) {
      return code;
    }
  }

  const fallback = browserLanguageHint();
  if (allowed.has(fallback)) {
    return fallback;
  }

  return "es";
}

function mapSpeechRecognitionError(code) {
  if (code === "not-allowed" || code === "service-not-allowed") {
    return "Permiso de microfono bloqueado para transcripcion en vivo.";
  }
  if (code === "audio-capture") {
    return "No se detecto microfono para transcripcion en vivo.";
  }
  if (code === "network") {
    return "Error de red en Google Speech. Verifica tu conexion.";
  }
  return `Error en transcripcion en vivo (${code}).`;
}

function setTranscriptInterimPreview(text) {
  const normalized = cleanTranscript(text);
  if (normalized === browserInterimTranscript) {
    return;
  }

  clearTrailingInterimLine();
  if (!normalized) {
    return;
  }

  browserInterimTranscript = normalized;
  appendLine(transcriptOutput, `... ${browserInterimTranscript}`);
}

function clearTrailingInterimLine() {
  if (!browserInterimTranscript) {
    return;
  }

  const current = String(transcriptOutput.value || "");
  const interimLine = `... ${browserInterimTranscript}`;
  if (current === interimLine) {
    transcriptOutput.value = "";
  } else if (current.endsWith(`\n${interimLine}`)) {
    transcriptOutput.value = current.slice(0, -(`\n${interimLine}`).length);
  }

  browserInterimTranscript = "";
}

function enqueueTextForTranslation(text) {
  const normalized = cleanTranscript(text);
  if (!normalized) {
    return;
  }

  if (textTranslationQueue.length >= MAX_TEXT_QUEUE_ITEMS) {
    textTranslationQueue.shift();
  }

  textTranslationQueue.push(normalized);
  processTextTranslationQueue();
}

async function processTextTranslationQueue() {
  if (processingTextQueue || textTranslationQueue.length === 0) {
    return;
  }

  processingTextQueue = true;
  setStatus("processing", listening ? "Escuchando + traduciendo en vivo" : "Procesando traducciones");

  while (textTranslationQueue.length > 0) {
    const segment = textTranslationQueue.shift();
    try {
      await translateTextSegment(segment);
      showError("");
    } catch (error) {
      showError(error.message || "No se pudo traducir el texto en vivo.");
    }
  }

  processingTextQueue = false;
  if (listening) {
    setStatus("listening", usingBrowserSpeechRecognition ? "Escuchando (Google en vivo)" : "Escuchando");
  } else {
    setStatus("idle", "Inactivo");
  }
}

async function translateTextSegment(text) {
  const source = currentSourceLanguage();
  const target = currentTargetLanguage();

  if (sourceSelect) {
    sourceSelect.value = source.code;
  }
  if (targetSelect) {
    targetSelect.value = target.code;
  }

  let response;
  try {
    response = await fetch(apiUrl("/api/translate-text"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        transcript: text,
        source_language: source.code,
        target_language: target.code,
        detected_language: "",
      }),
    });
  } catch (_error) {
    throw new Error(
      `No se pudo conectar con el servidor local (${API_BASE}) para traducir en vivo.`
    );
  }

  const payload = await parseJsonResponse(response);
  if (!response.ok) {
    throw new Error(payload.error || `Error del servidor (${response.status}).`);
  }

  const translation = cleanTranscript(payload.translation || "");
  if (translation) {
    appendTranslationLine(translation);
  }
}

async function initializeAudioPipeline(AudioContextCtor) {
  mediaStream = await navigator.mediaDevices.getUserMedia({
    audio: {
      channelCount: 1,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
  });

  audioContext = new AudioContextCtor();
  if (audioContext.state === "suspended") {
    await audioContext.resume();
  }

  sourceSampleRate = Number(audioContext.sampleRate) || TARGET_SAMPLE_RATE;
  sourceNode = audioContext.createMediaStreamSource(mediaStream);

  if (typeof audioContext.createScriptProcessor !== "function") {
    throw new Error("Este navegador no soporta ScriptProcessor para capturar audio.");
  }

  processorNode = audioContext.createScriptProcessor(2048, 1, 1);
  processorNode.onaudioprocess = onAudioProcess;

  muteGainNode = audioContext.createGain();
  muteGainNode.gain.value = 0;

  sourceNode.connect(processorNode);
  processorNode.connect(muteGainNode);
  muteGainNode.connect(audioContext.destination);
}

function onAudioProcess(event) {
  if (!listening) {
    return;
  }

  const input = event.inputBuffer.getChannelData(0);
  if (!input || input.length === 0) {
    return;
  }

  const frame = new Float32Array(input);
  pcmBuffers.push(frame);
  bufferedSamples += frame.length;

  const frameMs = (frame.length / sourceSampleRate) * 1000;
  const rms = calculateRms(frame);
  if (rms >= SPEECH_RMS_THRESHOLD) {
    bufferHasSpeech = true;
    silenceMs = 0;
  } else {
    silenceMs += frameMs;
  }

  const bufferedMs = (bufferedSamples / sourceSampleRate) * 1000;
  if (
    bufferHasSpeech &&
    bufferedMs >= MIN_BUFFER_MS_TO_FLUSH &&
    silenceMs >= SILENCE_FLUSH_MS
  ) {
    flushCapturedAudio(false);
  }
}

async function teardownAudioPipeline() {
  if (processorNode) {
    try {
      processorNode.disconnect();
    } catch (_error) {
      // ignorado
    }
    processorNode.onaudioprocess = null;
    processorNode = null;
  }

  if (sourceNode) {
    try {
      sourceNode.disconnect();
    } catch (_error) {
      // ignorado
    }
    sourceNode = null;
  }

  if (muteGainNode) {
    try {
      muteGainNode.disconnect();
    } catch (_error) {
      // ignorado
    }
    muteGainNode = null;
  }

  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }

  if (audioContext) {
    try {
      await audioContext.close();
    } catch (_error) {
      // ignorado
    }
    audioContext = null;
  }
}

function flushCapturedAudio(forceProcessQueue) {
  if (pcmBuffers.length === 0) {
    return;
  }

  const merged = mergeFloat32Buffers(pcmBuffers);
  pcmBuffers = [];
  bufferedSamples = 0;
  silenceMs = 0;
  bufferHasSpeech = false;

  if (!merged || merged.length === 0) {
    return;
  }

  const sampled = downsampleFloat32(merged, sourceSampleRate, TARGET_SAMPLE_RATE);
  if (!sampled || sampled.length === 0) {
    return;
  }

  const wavBlob = encodeWavBlob(sampled, TARGET_SAMPLE_RATE);
  enqueueAudioChunk(wavBlob);

  if (forceProcessQueue) {
    processQueue();
  }
}

function enqueueAudioChunk(blob) {
  if (!blob || blob.size === 0) {
    return;
  }

  if (uploadQueue.length >= MAX_QUEUE_CHUNKS) {
    uploadQueue.shift();
    if (!queueDropWarned) {
      queueDropWarned = true;
      showError(
        "La captura va mas rapido que el procesamiento. Se descartaron bloques antiguos para mantener estabilidad."
      );
    }
  }

  uploadQueue.push(blob);
  processQueue();
}

async function processQueue() {
  if (processingQueue || uploadQueue.length === 0) {
    return;
  }

  processingQueue = true;
  setStatus("processing", listening ? "Escuchando + procesando" : "Procesando bloques finales");

  const chunk = uploadQueue.shift();

  try {
    await sendChunk(chunk);
    queueDropWarned = false;
    showError("");
  } catch (error) {
    showError(error.message || "No se pudo procesar el audio.");
  } finally {
    processingQueue = false;
    if (uploadQueue.length > 0) {
      processQueue();
    } else if (listening) {
      setStatus("listening", "Escuchando");
    } else {
      setStatus("idle", "Inactivo");
    }
  }
}

async function sendChunk(chunk) {
  const source = currentSourceLanguage();
  const target = currentTargetLanguage();

  if (sourceSelect) {
    sourceSelect.value = source.code;
  }
  if (targetSelect) {
    targetSelect.value = target.code;
  }

  const formData = new FormData();
  formData.append("audio", chunk, "chunk.wav");
  formData.append("source_language", source.code);
  formData.append("target_language", target.code);
  formData.append("language_hint", browserLanguageHint());
  formData.append("transcription_backend", currentTranscriptionBackend());

  let response;
  try {
    response = await fetch(apiUrl("/api/transcribe-translate"), {
      method: "POST",
      body: formData,
    });
  } catch (_error) {
    throw new Error(
      `No se pudo conectar con el servidor local (${API_BASE}). Verifica que AlbertTranslator este abierto. Revisa alberttranslator.log junto al .exe.`
    );
  }

  const payload = await parseJsonResponse(response);
  if (!response.ok) {
    throw new Error(payload.error || `Error del servidor (${response.status}).`);
  }

  const transcript = cleanTranscript(payload.transcript || "");
  const translation = cleanTranscript(payload.translation || "");
  const effectiveBackend = String(payload.transcription_backend || "").trim().toLowerCase();
  if (effectiveBackend === "google" || effectiveBackend === "faster_whisper") {
    updateBackendNote(effectiveBackend);
  }

  if (transcript) {
    appendLine(transcriptOutput, transcript);
  }

  if (translation) {
    appendTranslationLine(translation);
  }
}

function mergeFloat32Buffers(buffers) {
  let totalLength = 0;
  buffers.forEach((buffer) => {
    totalLength += buffer.length;
  });

  const merged = new Float32Array(totalLength);
  let offset = 0;
  buffers.forEach((buffer) => {
    merged.set(buffer, offset);
    offset += buffer.length;
  });

  return merged;
}

function downsampleFloat32(buffer, inputRate, outputRate) {
  if (!buffer || buffer.length === 0) {
    return new Float32Array(0);
  }

  if (!inputRate || inputRate <= 0 || inputRate === outputRate) {
    return buffer;
  }

  const ratio = inputRate / outputRate;
  const newLength = Math.max(1, Math.round(buffer.length / ratio));
  const result = new Float32Array(newLength);

  let offsetResult = 0;
  let offsetBuffer = 0;
  while (offsetResult < newLength) {
    const nextOffsetBuffer = Math.min(buffer.length, Math.round((offsetResult + 1) * ratio));
    let sum = 0;
    let count = 0;

    for (let idx = offsetBuffer; idx < nextOffsetBuffer; idx += 1) {
      sum += buffer[idx];
      count += 1;
    }

    result[offsetResult] = count > 0 ? sum / count : 0;
    offsetResult += 1;
    offsetBuffer = nextOffsetBuffer;
  }

  return result;
}

function encodeWavBlob(samples, sampleRate) {
  const bytesPerSample = 2;
  const blockAlign = bytesPerSample;
  const buffer = new ArrayBuffer(44 + samples.length * bytesPerSample);
  const view = new DataView(buffer);

  writeWavString(view, 0, "RIFF");
  view.setUint32(4, 36 + samples.length * bytesPerSample, true);
  writeWavString(view, 8, "WAVE");
  writeWavString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, 16, true);
  writeWavString(view, 36, "data");
  view.setUint32(40, samples.length * bytesPerSample, true);

  let offset = 44;
  for (let i = 0; i < samples.length; i += 1) {
    const clipped = Math.max(-1, Math.min(1, samples[i]));
    const pcm = clipped < 0 ? clipped * 0x8000 : clipped * 0x7fff;
    view.setInt16(offset, pcm, true);
    offset += 2;
  }

  return new Blob([buffer], { type: "audio/wav" });
}

function writeWavString(view, offset, text) {
  for (let i = 0; i < text.length; i += 1) {
    view.setUint8(offset + i, text.charCodeAt(i));
  }
}

function calculateRms(buffer) {
  if (!buffer || buffer.length === 0) {
    return 0;
  }

  let sum = 0;
  for (let i = 0; i < buffer.length; i += 1) {
    const sample = buffer[i];
    sum += sample * sample;
  }
  return Math.sqrt(sum / buffer.length);
}

function browserLanguageHint() {
  const raw = String(navigator.language || "").trim().toLowerCase();
  if (!raw) {
    return "es";
  }

  const code = raw.split("-")[0].trim();
  return code || "es";
}

function cleanTranscript(raw) {
  return String(raw || "").replace(/\s+/g, " ").trim();
}

function resetTranslationTypewriter() {
  if (translationTypeTimer) {
    clearTimeout(translationTypeTimer);
    translationTypeTimer = null;
  }
  translationTypeTarget = String(translationOutput?.value || "");
}

function appendTranslationLine(text) {
  if (!text) {
    return;
  }

  const current = String(translationTypeTarget || translationOutput.value || "");
  const combined = current ? `${current}\n${text}` : text;
  animateTranslationTo(combined);
}

function animateTranslationTo(targetText) {
  translationTypeTarget = String(targetText || "");

  if (translationTypeTimer) {
    return;
  }

  const step = () => {
    const current = String(translationOutput.value || "");
    const target = String(translationTypeTarget || "");

    if (current === target) {
      translationTypeTimer = null;
      return;
    }

    if (!target.startsWith(current)) {
      translationOutput.value = target;
      translationOutput.scrollTop = translationOutput.scrollHeight;
      translationTypeTimer = null;
      return;
    }

    const nextChar = target.charAt(current.length);
    translationOutput.value = target.slice(0, current.length + 1);
    translationOutput.scrollTop = translationOutput.scrollHeight;

    let delayMs = 14;
    if (nextChar === " ") {
      delayMs = 8;
    } else if (/[,.!?;:]/.test(nextChar)) {
      delayMs = 34;
    } else if (nextChar === "\n") {
      delayMs = 20;
    }

    translationTypeTimer = setTimeout(step, delayMs);
  };

  step();
}

function appendLine(textarea, text) {
  if (!text) {
    return;
  }

  textarea.value += (textarea.value ? "\n" : "") + text;
  textarea.scrollTop = textarea.scrollHeight;
}

function lastTextareaLine(textarea) {
  const lines = String(textarea?.value || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  if (lines.length === 0) {
    return "";
  }
  return lines[lines.length - 1];
}

async function parseJsonResponse(response) {
  const text = await response.text();
  if (!text) {
    return {};
  }

  try {
    return JSON.parse(text);
  } catch (_error) {
    return { error: "La respuesta del servidor no es JSON valido." };
  }
}

async function checkServerReady() {
  try {
    const response = await fetch(apiUrl("/api/health"), { cache: "no-store" });
    return response.ok;
  } catch (_error) {
    return false;
  }
}

async function copyTextareaContent(textarea, button, emptyMessage) {
  const text = String(textarea?.value || "").trim();
  if (!text) {
    showError(emptyMessage);
    return;
  }

  try {
    await writeToClipboard(text);
    flashCopiedButton(button);
    showError("");
  } catch (_error) {
    showError("No se pudo copiar al portapapeles.");
  }
}

async function writeToClipboard(text) {
  if (navigator.clipboard?.writeText && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const helper = document.createElement("textarea");
  helper.value = text;
  helper.setAttribute("readonly", "");
  helper.style.position = "fixed";
  helper.style.top = "-9999px";
  document.body.appendChild(helper);
  helper.select();
  const copied = document.execCommand("copy");
  document.body.removeChild(helper);
  if (!copied) {
    throw new Error("copy failed");
  }
}

function flashCopiedButton(button) {
  if (!button) {
    return;
  }
  const original = button.textContent;
  button.textContent = "Copiado";
  button.classList.add("copied");
  setTimeout(() => {
    button.textContent = original;
    button.classList.remove("copied");
  }, 1200);
}
