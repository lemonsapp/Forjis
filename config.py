"""Configuración central de FORJIS."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# ---- Identidad ----
WAKE_NAME = "FORJIS"
# Variantes que Whisper puede transcribir cuando decís "forjis"
WAKE_WORDS = [
    "forjis", "forjes", "forji", "forhis", "forgis", "forjós", "foryis",
    "forys", "porgis", "for gis", "forge is", "forjás", "forjia", "forxis",
    "forhís", "forjís", "fortis", "forchis",
]

# ---- Reconocimiento de voz (Whisper) ----
WHISPER_MODEL = "small"     # tiny / base / small / medium  (small = mucho mejor en español)
WHISPER_COMPUTE = "int8"    # int8 = rápido en CPU
WHISPER_BEAM = 5            # más precisión (5) vs más velocidad (1)
LANGUAGE = "es"
# Pista de contexto: sesga a Whisper hacia la wake word y los comandos típicos.
WHISPER_INITIAL_PROMPT = (
    "Asistente de voz FORJIS. Órdenes habituales: FORJIS abrí Brave, "
    "FORJIS subí el volumen, FORJIS bajá el volumen, FORJIS buscá en YouTube, "
    "FORJIS qué hora es, FORJIS cerrá la ventana, FORJIS apagáte."
)

# ---- Audio: dispositivos ----
# Se buscan por nombre en MME/WASAPI (no por índice fijo). Poné "" para usar el default.
INPUT_DEVICE_MATCH = ""    # "" = micrófono por defecto de Windows. O poné parte del nombre (ej. "SSL 2")
OUTPUT_DEVICE_MATCH = ""   # "" = parlantes por defecto de Windows. O poné parte del nombre (ej. "SSL 2")

# ---- Audio: captura ----
SAMPLE_RATE = 16000
BLOCK_SIZE = 1600          # 0.1s por bloque
SILENCE_DURATION = 0.9     # segundos de silencio para cortar la frase
MAX_UTTERANCE = 12         # segundos máximos por frase
MIN_UTTERANCE = 0.4        # frases más cortas se descartan (ruido)

# ---- Audio: VAD por energía (auto-calibrado) ----
SILENCE_THRESHOLD_FLOOR = 0.008  # umbral mínimo absoluto
CALIB_SECONDS = 1.2              # cuánto ruido de fondo medir al arrancar
CALIB_FACTOR = 3.0               # umbral = ruido_de_fondo * factor
PRE_SPEECH_PAD_BLOCKS = 6        # ~0.6s antes del disparo (no cortar la 'F' de FORJIS)
NORMALIZE_PEAK = 0.95            # amplificar la frase a este pico antes de transcribir

# ---- Activación por aplauso ----
CLAP_ENABLED = True
CLAP_PEAK = 0.35        # amplitud pico mínima para un aplauso
CLAP_CREST = 4.0        # pico/rms (impulsividad) para distinguirlo de la voz
CLAP_GAP_MIN = 0.12     # seg mínimo entre los dos aplausos
CLAP_GAP_MAX = 0.90     # seg máximo entre los dos aplausos (doble aplauso)

# ---- Telemetría de la HUD ----
TELEMETRY_INTERVAL = 1.5

# ---- Anti-alucinaciones de Whisper ----
# Frases fantasma típicas que Whisper inventa con silencio/ruido (se descartan).
HALLUCINATIONS = [
    "subtítulos realizados por", "subtítulos por", "amara.org",
    "gracias por ver", "gracias por ver el video", "¡gracias!", "gracias.",
    "subscribe", "suscríbete", "www.", ".com", "♪", "[música]", "música",
    "subtitulado por", "subtítulos", "él línio", "purquis",
]

# ---- Voz de FORJIS (Piper) ----
PIPER_VOICE = os.path.join(MODELS_DIR, "es_ES-davefx-medium.onnx")  # compat
PIPER_VOICES = {
    "hombre": os.path.join(MODELS_DIR, "es_ES-davefx-medium.onnx"),
    "mujer":  os.path.join(MODELS_DIR, "es_ES-sharvard-medium.onnx"),
}
SPEED_SCALE = {"lento": 1.30, "normal": 1.0, "rapido": 0.85}
TMP_WAV = os.path.join(BASE_DIR, "_forjis_say.wav")

# ====================================================================
#  CEREBRO: dos opciones intercambiables (ver brain.py)
#    "claude" -> nube, Anthropic API (más inteligente, necesita API key)
#    "local"  -> Ollama offline (100% gratis y sin conexión)
#  Se elige en el instalador y se puede conmutar en la HUD; queda guardado
#  en forjis_state.json. Override puntual con la variable FORJIS_BRAIN.
# ====================================================================
DEFAULT_BRAIN = "claude"            # cerebro por defecto si no hay nada elegido

# ---- Cerebro Claude (Anthropic API) ----
CLAUDE_MODEL = "claude-haiku-4-5"   # rápido y sigue instrucciones (ideal por voz)
CLAUDE_MAX_TOKENS = 320
CLAUDE_HISTORY_MAX = 24             # cuántos mensajes recordar en la sesión

# Estado persistente (personalidad + voz que FORJIS recuerda)
STATE_FILE = os.path.join(BASE_DIR, "forjis_state.json")
DEFAULT_PERSONALITY = (
    "Elegante, tranquilo y con un toque de humor fino, al estilo JARVIS. "
    "Tratás al usuario de vos y a veces le decís jefe."
)


def get_api_key():
    """API key de Anthropic: variable de entorno o archivo api_key.txt."""
    k = os.environ.get("ANTHROPIC_API_KEY")
    if k:
        return k.strip()
    p = os.path.join(BASE_DIR, "api_key.txt")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return f.read().strip()
    return None

# ---- Cerebro LLM local (Ollama) ----
# El system prompt y las herramientas las arma brain_core (paridad con Claude).
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_URL = OLLAMA_HOST + "/api/chat"
OLLAMA_TAGS_URL = OLLAMA_HOST + "/api/tags"
LLM_MODEL = "qwen2.5:7b"     # entra en 6 GB de VRAM (RTX 2060), bueno en español y con tool-calling
LLM_TEMPERATURE = 0.6
LLM_NUM_PREDICT = 320        # máximo de tokens por respuesta
LLM_HISTORY_TURNS = 6        # cuántos turnos de conversación recordar
LLM_TIMEOUT = 90             # segundos (el primer turno carga el modelo en VRAM)

# ---- Ojos: cámara + gestos (Fase 3) ----
HAND_MODEL = os.path.join(MODELS_DIR, "hand_landmarker.task")
CAM_INDEX = 0           # índice de la webcam (0 = la primera)
CAM_W = 640
CAM_H = 480
FRAME_MARGIN = 100      # borde de la cámara que NO se usa (para llegar a las esquinas)
CURSOR_SMOOTHING = 5    # más alto = más suave/lento; más bajo = más directo
PINCH_CLICK_DIST = 40   # px entre pulgar e índice para considerar "click"
PINCH_RIGHT_DIST = 45   # px entre pulgar y mayor para "click derecho"

# ---- Apps conocidas (nombre dicho -> ejecutable o comando) ----
def _find_brave():
    cands = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    return "brave.exe"  # fallback: Windows lo resuelve si está instalado


_BRAVE = _find_brave()

KNOWN_APPS = {
    "brave": _BRAVE,
    "navegador": _BRAVE,
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "firefox": "firefox.exe",
    "bloc de notas": "notepad.exe",
    "notepad": "notepad.exe",
    "calculadora": "calc.exe",
    "explorador": "explorer.exe",
    "archivos": "explorer.exe",
    "configuracion": "ms-settings:",
    "configuración": "ms-settings:",
    "spotify": "spotify:",
    "terminal": "wt.exe",
    "cmd": "cmd.exe",
    "paint": "mspaint.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
}
