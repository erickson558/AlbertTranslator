// Lista de idiomas disponibles para transcripcion/traduccion
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

// --- i18n: diccionario de cadenas de interfaz por idioma ---
const UI_TRANSLATIONS = {
  es: {
    title: "Traductor de Voz en Vivo",
    subtitle: "Transcripcion por voz del navegador y traduccion automatica con idioma origen y destino.",
    uilangLabel: "Idioma de la interfaz",
    sourceLangLabel: "Idioma origen",
    targetLangLabel: "Idioma destino",
    swapBtn: "⇄ Intercambiar",
    backendLabel: "Backend de transcripcion",
    backendGoogleOption: "google (nube)",
    backendWhisperOption: "faster_whisper (local)",
    backendNoteGoogleLive: "Usando Google Speech en vivo desde el navegador (transcripcion casi en tiempo real). Para mayor precision, fija el idioma origen en lugar de auto.",
    backendNoteGoogleChunk: "Usando Google Speech por bloques (tu navegador no soporta modo en vivo).",
    backendNoteWhisper: "Usando faster_whisper local (recomendado para uso sin conexion).",
    startBtn: "Iniciar escucha",
    stopBtn: "Detener",
    clearBtn: "Limpiar",
    statusIdle: "Inactivo",
    transcriptTitle: "Transcripcion",
    translationTitle: "Traduccion",
    copyBtn: "Copiar",
    copiedBtn: "Copiado",
    transcriptPlaceholder: "La transcripcion aparecera aqui...",
    translationPlaceholder: "La traduccion aparecera aqui...",
    autoDetect: "Detectar automaticamente",
    footerHint: "Permite el microfono para capturar audio y enviarlo al servidor local para transcripcion.",
    donateBtn: "🍺 Comprame una cerveza",
    errNoServer: "No hay conexion con el servidor local. Abre AlbertTranslator e inicia el servidor. Si falla, revisa alberttranslator.log junto al .exe.",
    errNoTarget: "Selecciona un idioma destino valido.",
    errNoMic: "Tu navegador no permite capturar microfono.",
    errNoAudioCtx: "Tu navegador no soporta AudioContext para captura de voz.",
    errNoScriptProc: "Este navegador no soporta ScriptProcessor para capturar audio.",
    errNoLiveSpeech: "Tu navegador no soporta transcripcion en vivo. Cambia a faster_whisper o usa Chrome/Edge.",
    errMicLivePrefix: "No se pudo acceder al microfono para transcripcion en vivo. Detalle: ",
    errQueueDrop: "La captura va mas rapido que el procesamiento. Se descartaron bloques antiguos para mantener estabilidad.",
    errNoConnect: "No se pudo conectar con el servidor local",
    errServerDetail: "Verifica que AlbertTranslator este abierto. Revisa alberttranslator.log junto al .exe.",
    errCopyEmptyTranscript: "No hay transcripcion para copiar.",
    errCopyEmptyTranslation: "No hay traduccion para copiar.",
    errCopyFailed: "No se pudo copiar al portapapeles.",
    errSwapAuto: "No se puede intercambiar cuando el idioma origen es automatico.",
    errJsonInvalid: "La respuesta del servidor no es JSON valido.",
    errStartLiveDetail: "No se pudo iniciar la transcripcion en vivo de Google. Detalle: ",
    statusStarting: "Iniciando escucha...",
    statusStopping: "Deteniendo...",
    statusListening: "Escuchando",
    statusListeningLive: "Escuchando (Google en vivo)",
    statusFinalBrowser: "Procesando traducciones finales",
    statusFinalQueue: "Procesando bloques finales",
    statusListeningProcessing: "Escuchando + procesando",
    statusTranslatingLive: "Escuchando + traduciendo en vivo",
    statusTranslating: "Procesando traducciones",
    errSpeechNotAllowed: "Permiso de microfono bloqueado para transcripcion en vivo.",
    errSpeechNoMic: "No se detecto microfono para transcripcion en vivo.",
    errSpeechNetwork: "Error de red en Google Speech. Verifica tu conexion.",
    errSpeechGeneric: "Error en transcripcion en vivo",
  },
  en: {
    title: "Live Voice Translator",
    subtitle: "Browser voice transcription and automatic translation with source and target language.",
    uilangLabel: "Interface language",
    sourceLangLabel: "Source language",
    targetLangLabel: "Target language",
    swapBtn: "⇄ Swap",
    backendLabel: "Transcription backend",
    backendGoogleOption: "google (cloud)",
    backendWhisperOption: "faster_whisper (local)",
    backendNoteGoogleLive: "Using live Google Speech from browser (near real-time transcription). For better accuracy, fix the source language instead of auto.",
    backendNoteGoogleChunk: "Using Google Speech in blocks (your browser does not support live mode).",
    backendNoteWhisper: "Using local faster_whisper (recommended for offline use).",
    startBtn: "Start listening",
    stopBtn: "Stop",
    clearBtn: "Clear",
    statusIdle: "Idle",
    transcriptTitle: "Transcription",
    translationTitle: "Translation",
    copyBtn: "Copy",
    copiedBtn: "Copied",
    transcriptPlaceholder: "Transcription will appear here...",
    translationPlaceholder: "Translation will appear here...",
    autoDetect: "Auto-detect",
    footerHint: "Allow microphone access to capture audio and send it to the local server for transcription.",
    donateBtn: "🍺 Buy me a beer",
    errNoServer: "No connection to local server. Open AlbertTranslator and start the server. If it fails, check alberttranslator.log next to the .exe.",
    errNoTarget: "Select a valid target language.",
    errNoMic: "Your browser does not allow microphone access.",
    errNoAudioCtx: "Your browser does not support AudioContext for voice capture.",
    errNoScriptProc: "This browser does not support ScriptProcessor for audio capture.",
    errNoLiveSpeech: "Your browser does not support live transcription. Switch to faster_whisper or use Chrome/Edge.",
    errMicLivePrefix: "Could not access microphone for live transcription. Detail: ",
    errQueueDrop: "Capture is faster than processing. Old blocks were dropped to maintain stability.",
    errNoConnect: "Could not connect to local server",
    errServerDetail: "Verify AlbertTranslator is open. Check alberttranslator.log next to the .exe.",
    errCopyEmptyTranscript: "No transcription to copy.",
    errCopyEmptyTranslation: "No translation to copy.",
    errCopyFailed: "Could not copy to clipboard.",
    errSwapAuto: "Cannot swap when source language is set to auto.",
    errJsonInvalid: "Server response is not valid JSON.",
    errStartLiveDetail: "Could not start Google live transcription. Detail: ",
    statusStarting: "Starting...",
    statusStopping: "Stopping...",
    statusListening: "Listening",
    statusListeningLive: "Listening (Google live)",
    statusFinalBrowser: "Processing final translations",
    statusFinalQueue: "Processing final blocks",
    statusListeningProcessing: "Listening + processing",
    statusTranslatingLive: "Listening + translating live",
    statusTranslating: "Processing translations",
    errSpeechNotAllowed: "Microphone permission blocked for live transcription.",
    errSpeechNoMic: "No microphone detected for live transcription.",
    errSpeechNetwork: "Google Speech network error. Check your connection.",
    errSpeechGeneric: "Live transcription error",
  },
  pt: {
    title: "Tradutor de Voz ao Vivo",
    subtitle: "Transcricao de voz do navegador e traducao automatica com idioma de origem e destino.",
    uilangLabel: "Idioma da interface",
    sourceLangLabel: "Idioma de origem",
    targetLangLabel: "Idioma de destino",
    swapBtn: "⇄ Trocar",
    backendLabel: "Backend de transcricao",
    backendGoogleOption: "google (nuvem)",
    backendWhisperOption: "faster_whisper (local)",
    backendNoteGoogleLive: "Usando Google Speech ao vivo do navegador (transcricao quase em tempo real). Para maior precisao, fixe o idioma de origem em vez de auto.",
    backendNoteGoogleChunk: "Usando Google Speech em blocos (seu navegador nao suporta modo ao vivo).",
    backendNoteWhisper: "Usando faster_whisper local (recomendado para uso offline).",
    startBtn: "Iniciar escuta",
    stopBtn: "Parar",
    clearBtn: "Limpar",
    statusIdle: "Inativo",
    transcriptTitle: "Transcricao",
    translationTitle: "Traducao",
    copyBtn: "Copiar",
    copiedBtn: "Copiado",
    transcriptPlaceholder: "A transcricao aparecera aqui...",
    translationPlaceholder: "A traducao aparecera aqui...",
    autoDetect: "Detectar automaticamente",
    footerHint: "Permita o microfone para capturar audio e envia-lo ao servidor local para transcricao.",
    donateBtn: "🍺 Me pague uma cerveja",
    errNoServer: "Sem conexao com o servidor local. Abra o AlbertTranslator e inicie o servidor.",
    errNoTarget: "Selecione um idioma de destino valido.",
    errNoMic: "Seu navegador nao permite acesso ao microfone.",
    errNoAudioCtx: "Seu navegador nao suporta AudioContext para captura de voz.",
    errNoScriptProc: "Este navegador nao suporta ScriptProcessor para captura de audio.",
    errNoLiveSpeech: "Seu navegador nao suporta transcricao ao vivo. Mude para faster_whisper ou use Chrome/Edge.",
    errMicLivePrefix: "Nao foi possivel acessar o microfone para transcricao ao vivo. Detalhe: ",
    errQueueDrop: "A captura esta mais rapida que o processamento. Blocos antigos foram descartados.",
    errNoConnect: "Nao foi possivel conectar ao servidor local",
    errServerDetail: "Verifique se o AlbertTranslator esta aberto. Veja alberttranslator.log.",
    errCopyEmptyTranscript: "Nenhuma transcricao para copiar.",
    errCopyEmptyTranslation: "Nenhuma traducao para copiar.",
    errCopyFailed: "Nao foi possivel copiar para a area de transferencia.",
    errSwapAuto: "Nao e possivel trocar quando o idioma de origem e automatico.",
    errJsonInvalid: "A resposta do servidor nao e JSON valido.",
    errStartLiveDetail: "Nao foi possivel iniciar a transcricao ao vivo do Google. Detalhe: ",
    statusStarting: "Iniciando...",
    statusStopping: "Parando...",
    statusListening: "Ouvindo",
    statusListeningLive: "Ouvindo (Google ao vivo)",
    statusFinalBrowser: "Processando traducoes finais",
    statusFinalQueue: "Processando blocos finais",
    statusListeningProcessing: "Ouvindo + processando",
    statusTranslatingLive: "Ouvindo + traduzindo ao vivo",
    statusTranslating: "Processando traducoes",
    errSpeechNotAllowed: "Permissao de microfone bloqueada para transcricao ao vivo.",
    errSpeechNoMic: "Nenhum microfone detectado para transcricao ao vivo.",
    errSpeechNetwork: "Erro de rede no Google Speech. Verifique sua conexao.",
    errSpeechGeneric: "Erro na transcricao ao vivo",
  },
  fr: {
    title: "Traducteur Vocal en Direct",
    subtitle: "Transcription vocale du navigateur et traduction automatique avec langue source et cible.",
    uilangLabel: "Langue de l'interface",
    sourceLangLabel: "Langue source",
    targetLangLabel: "Langue cible",
    swapBtn: "⇄ Inverser",
    backendLabel: "Backend de transcription",
    backendGoogleOption: "google (cloud)",
    backendWhisperOption: "faster_whisper (local)",
    backendNoteGoogleLive: "Utilisation de Google Speech en direct depuis le navigateur. Pour plus de precision, fixez la langue source au lieu de auto.",
    backendNoteGoogleChunk: "Utilisation de Google Speech par blocs (votre navigateur ne supporte pas le mode direct).",
    backendNoteWhisper: "Utilisation de faster_whisper local (recommande hors ligne).",
    startBtn: "Demarrer l'ecoute",
    stopBtn: "Arreter",
    clearBtn: "Effacer",
    statusIdle: "Inactif",
    transcriptTitle: "Transcription",
    translationTitle: "Traduction",
    copyBtn: "Copier",
    copiedBtn: "Copie",
    transcriptPlaceholder: "La transcription apparaitra ici...",
    translationPlaceholder: "La traduction apparaitra ici...",
    autoDetect: "Detecter automatiquement",
    footerHint: "Autorisez le microphone pour capturer l'audio et l'envoyer au serveur local.",
    donateBtn: "🍺 Offrez-moi une biere",
    errNoServer: "Pas de connexion au serveur local. Ouvrez AlbertTranslator et demarrez le serveur.",
    errNoTarget: "Selectionnez une langue cible valide.",
    errNoMic: "Votre navigateur ne permet pas l'acces au microphone.",
    errNoAudioCtx: "Votre navigateur ne supporte pas AudioContext.",
    errNoScriptProc: "Ce navigateur ne supporte pas ScriptProcessor.",
    errNoLiveSpeech: "Votre navigateur ne supporte pas la transcription en direct. Utilisez Chrome/Edge.",
    errMicLivePrefix: "Impossible d'acceder au microphone. Detail: ",
    errQueueDrop: "La capture est plus rapide que le traitement. Des blocs anciens ont ete supprimes.",
    errNoConnect: "Impossible de se connecter au serveur local",
    errServerDetail: "Verifiez qu'AlbertTranslator est ouvert. Consultez alberttranslator.log.",
    errCopyEmptyTranscript: "Aucune transcription a copier.",
    errCopyEmptyTranslation: "Aucune traduction a copier.",
    errCopyFailed: "Impossible de copier dans le presse-papiers.",
    errSwapAuto: "Impossible d'inverser quand la langue source est automatique.",
    errJsonInvalid: "La reponse du serveur n'est pas du JSON valide.",
    errStartLiveDetail: "Impossible de demarrer la transcription en direct Google. Detail: ",
    statusStarting: "Demarrage...",
    statusStopping: "Arret...",
    statusListening: "Ecoute",
    statusListeningLive: "Ecoute (Google direct)",
    statusFinalBrowser: "Traitement des traductions finales",
    statusFinalQueue: "Traitement des blocs finaux",
    statusListeningProcessing: "Ecoute + traitement",
    statusTranslatingLive: "Ecoute + traduction en direct",
    statusTranslating: "Traitement des traductions",
    errSpeechNotAllowed: "Permission microphone bloquee.",
    errSpeechNoMic: "Aucun microphone detecte.",
    errSpeechNetwork: "Erreur reseau Google Speech. Verifiez votre connexion.",
    errSpeechGeneric: "Erreur de transcription en direct",
  },
  de: {
    title: "Live-Sprach-Ubersetzer",
    subtitle: "Browser-Sprachtranskription und automatische Ubersetzung mit Quell- und Zielsprache.",
    uilangLabel: "Sprache der Oberflache",
    sourceLangLabel: "Quellsprache",
    targetLangLabel: "Zielsprache",
    swapBtn: "⇄ Tauschen",
    backendLabel: "Transkriptions-Backend",
    backendGoogleOption: "google (Cloud)",
    backendWhisperOption: "faster_whisper (lokal)",
    backendNoteGoogleLive: "Google Speech live im Browser. Fur mehr Prazision, legen Sie die Quellsprache fest statt Auto.",
    backendNoteGoogleChunk: "Google Speech in Blocken (Ihr Browser unterstutzt den Live-Modus nicht).",
    backendNoteWhisper: "Lokales faster_whisper (empfohlen fur Offline-Nutzung).",
    startBtn: "Zuhoren starten",
    stopBtn: "Stoppen",
    clearBtn: "Loschen",
    statusIdle: "Inaktiv",
    transcriptTitle: "Transkription",
    translationTitle: "Ubersetzung",
    copyBtn: "Kopieren",
    copiedBtn: "Kopiert",
    transcriptPlaceholder: "Die Transkription erscheint hier...",
    translationPlaceholder: "Die Ubersetzung erscheint hier...",
    autoDetect: "Automatisch erkennen",
    footerHint: "Erlauben Sie das Mikrofon, um Audio aufzunehmen und an den lokalen Server zu senden.",
    donateBtn: "🍺 Kauf mir ein Bier",
    errNoServer: "Keine Verbindung zum lokalen Server. Offnen Sie AlbertTranslator und starten Sie den Server.",
    errNoTarget: "Wahlen Sie eine gultige Zielsprache.",
    errNoMic: "Ihr Browser erlaubt keinen Mikrofon-Zugriff.",
    errNoAudioCtx: "Ihr Browser unterstutzt AudioContext nicht.",
    errNoScriptProc: "Dieser Browser unterstutzt ScriptProcessor nicht.",
    errNoLiveSpeech: "Ihr Browser unterstutzt keine Live-Transkription. Verwenden Sie Chrome/Edge.",
    errMicLivePrefix: "Mikrofon-Zugriff nicht moglich. Detail: ",
    errQueueDrop: "Die Aufnahme ist schneller als die Verarbeitung. Alte Blocke wurden verworfen.",
    errNoConnect: "Verbindung zum lokalen Server fehlgeschlagen",
    errServerDetail: "Prufen Sie ob AlbertTranslator geoffnet ist. Siehe alberttranslator.log.",
    errCopyEmptyTranscript: "Keine Transkription zum Kopieren.",
    errCopyEmptyTranslation: "Keine Ubersetzung zum Kopieren.",
    errCopyFailed: "Kopieren in die Zwischenablage fehlgeschlagen.",
    errSwapAuto: "Tauschen nicht moglich bei automatischer Quellsprache.",
    errJsonInvalid: "Server-Antwort ist kein gultiges JSON.",
    errStartLiveDetail: "Google Live-Transkription konnte nicht gestartet werden. Detail: ",
    statusStarting: "Starte...",
    statusStopping: "Stoppe...",
    statusListening: "Hort zu",
    statusListeningLive: "Hort zu (Google live)",
    statusFinalBrowser: "Finale Ubersetzungen werden verarbeitet",
    statusFinalQueue: "Finale Blocke werden verarbeitet",
    statusListeningProcessing: "Hort zu + verarbeitet",
    statusTranslatingLive: "Hort zu + ubersetzt live",
    statusTranslating: "Ubersetzungen werden verarbeitet",
    errSpeechNotAllowed: "Mikrofon-Berechtigung gesperrt.",
    errSpeechNoMic: "Kein Mikrofon erkannt.",
    errSpeechNetwork: "Google Speech Netzwerkfehler. Verbindung prufen.",
    errSpeechGeneric: "Live-Transkription Fehler",
  },
};

// Idioma de la interfaz actual; se persiste en localStorage entre sesiones
let currentUiLang = localStorage.getItem("albert_ui_lang") || "es";

// Devuelve la cadena i18n para la clave dada en el idioma actual, con fallback a ES
function t(key) {
  const dict = UI_TRANSLATIONS[currentUiLang] || UI_TRANSLATIONS.es;
  return Object.prototype.hasOwnProperty.call(dict, key) ? dict[key] : (UI_TRANSLATIONS.es[key] || key);
}

// Actualiza todos los elementos del DOM con el idioma de interfaz actual
function applyUiLanguage() {
  const pageTitle = document.getElementById("page-title");
  if (pageTitle) { pageTitle.textContent = t("title"); document.title = t("title"); }

  const pageSubtitle = document.getElementById("page-subtitle");
  if (pageSubtitle) pageSubtitle.textContent = t("subtitle");

  const labelUiLang = document.getElementById("label-ui-lang");
  if (labelUiLang) labelUiLang.textContent = t("uilangLabel");

  const labelSource = document.getElementById("label-source-lang");
  if (labelSource) labelSource.textContent = t("sourceLangLabel");

  const labelTarget = document.getElementById("label-target-lang");
  if (labelTarget) labelTarget.textContent = t("targetLangLabel");

  if (swapBtn) swapBtn.textContent = t("swapBtn");

  const labelBackend = document.getElementById("label-backend");
  if (labelBackend) labelBackend.textContent = t("backendLabel");

  // Actualiza textos de las opciones del selector de backend
  if (transcriptionBackendSelect) {
    for (const opt of transcriptionBackendSelect.options) {
      if (opt.value === "google") opt.textContent = t("backendGoogleOption");
      else if (opt.value === "faster_whisper") opt.textContent = t("backendWhisperOption");
    }
  }

  // Solo actualiza botones de control cuando no hay escucha activa
  if (!listening) {
    if (startBtn) startBtn.textContent = t("startBtn");
  }
  if (stopBtn && stopBtn.disabled) stopBtn.textContent = t("stopBtn");
  if (clearBtn) clearBtn.textContent = t("clearBtn");

  const transcriptTitleEl = document.getElementById("transcript-title");
  if (transcriptTitleEl) transcriptTitleEl.textContent = t("transcriptTitle");

  const translationTitleEl = document.getElementById("translation-title");
  if (translationTitleEl) translationTitleEl.textContent = t("translationTitle");

  // Actualiza botones Copiar solo si no estan en estado "copiado"
  if (copyTranscriptBtn && !copyTranscriptBtn.classList.contains("copied")) {
    copyTranscriptBtn.textContent = t("copyBtn");
  }
  if (copyTranslationBtn && !copyTranslationBtn.classList.contains("copied")) {
    copyTranslationBtn.textContent = t("copyBtn");
  }

  if (transcriptOutput) transcriptOutput.placeholder = t("transcriptPlaceholder");
  if (translationOutput) translationOutput.placeholder = t("translationPlaceholder");

  const footerHintEl = document.getElementById("footer-hint");
  if (footerHintEl) footerHintEl.textContent = t("footerHint");

  const donateBtnEl = document.getElementById("donate-btn");
  if (donateBtnEl) donateBtnEl.textContent = t("donateBtn");

  // Actualiza la opcion "auto" del selector de idioma origen
  if (sourceSelect) {
    const autoOpt = sourceSelect.querySelector('option[value="auto"]');
    if (autoOpt) autoOpt.textContent = t("autoDetect");
  }

  // Refresca la nota del backend con el idioma actual
  updateBackendNote(currentTranscriptionBackend());

  // Refresca el estado "Inactivo" si la app esta en reposo
  if (statusBox && statusBox.classList.contains("idle")) {
    setStatus("idle", t("statusIdle"));
  }
}

// Arrays de idiomas con opcion "auto" para origen
const SOURCE_LANGUAGES = [{ name: "autoDetect", code: "auto" }, ...COMMON_LANGUAGES];
const TARGET_LANGUAGES = [...COMMON_LANGUAGES];

// Referencias al DOM
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
const BROWSER_STT_RESTART_DELAY_MS = 160;
const TRANSCRIPT_TRANSLATION_DEBOUNCE_MS = 260;
const SpeechRecognitionCtor =
  window.SpeechRecognition || window.webkitSpeechRecognition || null;

// Estado global de la app
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
let translationTypeTimer = null;
let translationTypeTarget = "";
let translationSyncTimer = null;
let activeTranscriptTranslationController = null;
let lastRequestedTranscript = "";

// Inicializacion al cargar la pagina
buildLanguageOptions();
wireEvents();
wireUiLanguageSelect();
initializeBackendControl();
applyUiLanguage();
void refreshBackendFromServer();

// Construye las listas de idiomas origen y destino en los selectores del DOM
function buildLanguageOptions() {
  if (sourceSelect) {
    sourceSelect.innerHTML = "";
    // Opcion de deteccion automatica (texto actualizado por i18n)
    const autoOpt = document.createElement("option");
    autoOpt.value = "auto";
    autoOpt.textContent = t("autoDetect");
    sourceSelect.appendChild(autoOpt);
    COMMON_LANGUAGES.forEach((language) => {
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

// Enlaza todos los eventos de la UI con sus manejadores
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
        t("errCopyEmptyTranscript")
      );
    });
  }
  if (copyTranslationBtn) {
    copyTranslationBtn.addEventListener("click", () => {
      copyTextareaContent(
        translationOutput,
        copyTranslationBtn,
        t("errCopyEmptyTranslation")
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

// Enlaza el selector de idioma de la interfaz con localStorage y applyUiLanguage
function wireUiLanguageSelect() {
  const uiLangSelect = document.getElementById("ui-language");
  if (!uiLangSelect) return;
  // Restaura la preferencia guardada
  uiLangSelect.value = currentUiLang;
  uiLangSelect.addEventListener("change", () => {
    currentUiLang = uiLangSelect.value;
    localStorage.setItem("albert_ui_lang", currentUiLang);
    applyUiLanguage();
  });
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
    // ignorado - el servidor puede no estar disponible aun
  }
}

// Actualiza la nota informativa del backend usando las cadenas i18n actuales
function updateBackendNote(backend) {
  if (!backendNote) {
    return;
  }

  if (backend === "google") {
    if (SpeechRecognitionCtor) {
      backendNote.textContent = t("backendNoteGoogleLive");
      return;
    }
    backendNote.textContent = t("backendNoteGoogleChunk");
    return;
  }

  backendNote.textContent = t("backendNoteWhisper");
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
  cancelPendingTranscriptTranslationSync();
  browserInterimTranscript = "";
  transcriptOutput.value = "";
  translationOutput.value = "";
  showError("");
}

function swapLanguages() {
  const source = currentSourceLanguage();
  const target = currentTargetLanguage();

  if (source.code === "auto") {
    showError(t("errSwapAuto"));
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
    showError(t("errNoServer"));
    return;
  }

  const source = currentSourceLanguage();
  const target = currentTargetLanguage();
  if (!target || target.code === "auto") {
    showError(t("errNoTarget"));
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
  setStatus("processing", t("statusStarting"));

  uploadQueue = [];
  processingQueue = false;
  queueDropWarned = false;
  cancelPendingTranscriptTranslationSync();
  pcmBuffers = [];
  bufferedSamples = 0;
  silenceMs = 0;
  bufferHasSpeech = false;
  browserInterimTranscript = "";

  try {
    if (shouldUseBrowserSpeechRecognition()) {
      await ensureMicrophonePermissionForLive();
      startBrowserSpeechRecognition(source.code);
      setStatus("listening", t("statusListeningLive"));
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error(t("errNoMic"));
    }

    const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextCtor) {
      throw new Error(t("errNoAudioCtx"));
    }

    await initializeAudioPipeline(AudioContextCtor);
    chunkTimer = setInterval(() => {
      flushCapturedAudio(false);
    }, TIMER_FLUSH_MS);

    setStatus("listening", t("statusListening"));
  } catch (error) {
    listening = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    setStatus("idle", t("statusIdle"));
    stopBrowserSpeechRecognition();
    await teardownAudioPipeline();
    showError(error.message || t("errNoMic"));
  }
}

async function ensureMicrophonePermissionForLive() {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error(t("errNoMic"));
  }

  let probeStream = null;
  try {
    probeStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (error) {
    throw new Error(t("errMicLivePrefix") + (error.message || error));
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
  setStatus("processing", t("statusStopping"));

  if (usingBrowserSpeechRecognition) {
    stopBrowserSpeechRecognition();
    if (isTranscriptTranslationPending()) {
      setStatus("processing", t("statusFinalBrowser"));
    } else {
      setStatus("idle", t("statusIdle"));
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
    setStatus("processing", t("statusFinalQueue"));
  } else {
    setStatus("idle", t("statusIdle"));
  }
}

function shouldUseBrowserSpeechRecognition() {
  return currentTranscriptionBackend() === "google" && Boolean(SpeechRecognitionCtor);
}

function startBrowserSpeechRecognition(sourceLanguageCode) {
  if (!SpeechRecognitionCtor) {
    throw new Error(t("errNoLiveSpeech"));
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
    throw new Error(t("errStartLiveDetail") + (error.message || error));
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
        scheduleTranscriptTranslationSync();
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

  // Reinicia el reconocimiento automaticamente tras un breve retardo
  browserSpeechRestartTimer = setTimeout(() => {
    if (!listening || !usingBrowserSpeechRecognition || !browserSpeechRecognition) {
      return;
    }

    try {
      browserSpeechRecognition.start();
    } catch (_error) {
      // Si ya esta arrancando/reiniciando, el siguiente onend reintentara
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

// Mapea codigos de error de SpeechRecognition a mensajes i18n
function mapSpeechRecognitionError(code) {
  if (code === "not-allowed" || code === "service-not-allowed") {
    return t("errSpeechNotAllowed");
  }
  if (code === "audio-capture") {
    return t("errSpeechNoMic");
  }
  if (code === "network") {
    return t("errSpeechNetwork");
  }
  return `${t("errSpeechGeneric")} (${code}).`;
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

function isTranscriptTranslationPending() {
  return Boolean(translationSyncTimer || activeTranscriptTranslationController);
}

function cancelPendingTranscriptTranslationSync() {
  if (translationSyncTimer) {
    clearTimeout(translationSyncTimer);
    translationSyncTimer = null;
  }

  if (activeTranscriptTranslationController) {
    activeTranscriptTranslationController.abort();
    activeTranscriptTranslationController = null;
  }

  lastRequestedTranscript = "";
}

function scheduleTranscriptTranslationSync() {
  if (translationSyncTimer) {
    clearTimeout(translationSyncTimer);
  }

  translationSyncTimer = setTimeout(() => {
    translationSyncTimer = null;
    void syncTranslationFromTranscriptOutput();
  }, TRANSCRIPT_TRANSLATION_DEBOUNCE_MS);
}

async function syncTranslationFromTranscriptOutput() {
  const transcript = cleanTranscript(transcriptOutput.value || "");
  if (!transcript) {
    resetTranslationTypewriter();
    translationOutput.value = "";
    cancelPendingTranscriptTranslationSync();
    return;
  }

  if (transcript === lastRequestedTranscript) {
    return;
  }

  if (activeTranscriptTranslationController) {
    activeTranscriptTranslationController.abort();
  }

  lastRequestedTranscript = transcript;
  const controller = new AbortController();
  activeTranscriptTranslationController = controller;

  const source = currentSourceLanguage();
  const target = currentTargetLanguage();

  if (sourceSelect) {
    sourceSelect.value = source.code;
  }
  if (targetSelect) {
    targetSelect.value = target.code;
  }

  setStatus(
    "processing",
    listening ? t("statusTranslatingLive") : t("statusTranslating")
  );

  let response;
  try {
    response = await fetch(apiUrl("/api/translate-text"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      body: JSON.stringify({
        transcript,
        source_language: source.code,
        target_language: target.code,
        detected_language: "",
      }),
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      return;
    }
    throw new Error(
      `${t("errNoConnect")} (${API_BASE}).`
    );
  }

  try {
    const payload = await parseJsonResponse(response);
    if (!response.ok) {
      throw new Error(payload.error || `Error del servidor (${response.status}).`);
    }

    if (activeTranscriptTranslationController !== controller) {
      return;
    }

    const translation = cleanTranscript(payload.translation || "");
    animateTranslationTo(translation);
    showError("");
  } catch (error) {
    if (error?.name !== "AbortError") {
      showError(error.message || t("errNoConnect"));
    }
  } finally {
    if (activeTranscriptTranslationController === controller) {
      activeTranscriptTranslationController = null;
    }

    if (listening) {
      setStatus(
        "listening",
        usingBrowserSpeechRecognition ? t("statusListeningLive") : t("statusListening")
      );
    } else {
      setStatus("idle", t("statusIdle"));
    }
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
    throw new Error(t("errNoScriptProc"));
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

  // Descarta el bloque mas antiguo si la cola esta llena para evitar desfase
  if (uploadQueue.length >= MAX_QUEUE_CHUNKS) {
    uploadQueue.shift();
    if (!queueDropWarned) {
      queueDropWarned = true;
      showError(t("errQueueDrop"));
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
  setStatus("processing", listening ? t("statusListeningProcessing") : t("statusFinalQueue"));

  const chunk = uploadQueue.shift();

  try {
    await sendChunk(chunk);
    queueDropWarned = false;
    showError("");
  } catch (error) {
    showError(error.message || t("errNoConnect"));
  } finally {
    processingQueue = false;
    if (uploadQueue.length > 0) {
      processQueue();
    } else if (listening) {
      setStatus("listening", t("statusListening"));
    } else {
      setStatus("idle", t("statusIdle"));
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
      `${t("errNoConnect")} (${API_BASE}). ${t("errServerDetail")}`
    );
  }

  const payload = await parseJsonResponse(response);
  if (!response.ok) {
    throw new Error(payload.error || `Error del servidor (${response.status}).`);
  }

  const transcript = cleanTranscript(payload.transcript || "");
  const effectiveBackend = String(payload.transcription_backend || "").trim().toLowerCase();
  if (effectiveBackend === "google" || effectiveBackend === "faster_whisper") {
    updateBackendNote(effectiveBackend);
  }

  if (transcript) {
    appendLine(transcriptOutput, transcript);
    scheduleTranscriptTranslationSync();
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

// Reduce la tasa de muestreo del audio para ajustarlo a TARGET_SAMPLE_RATE
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

// Codifica muestras Float32 como un blob WAV PCM 16-bit mono
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

// Calcula RMS (nivel de volumen) de un frame de audio para deteccion de voz
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

// Anima la aparicion de la traduccion caracter a caracter (efecto maquina de escribir)
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
    return { error: t("errJsonInvalid") };
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
    showError(t("errCopyFailed"));
  }
}

async function writeToClipboard(text) {
  if (navigator.clipboard?.writeText && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  // Fallback para contextos no seguros (HTTP local)
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

// Muestra confirmacion visual en el boton Copiar y restaura el texto original
function flashCopiedButton(button) {
  if (!button) {
    return;
  }
  const original = button.textContent;
  button.textContent = t("copiedBtn");
  button.classList.add("copied");
  setTimeout(() => {
    button.textContent = original;
    button.classList.remove("copied");
  }, 1200);
}
