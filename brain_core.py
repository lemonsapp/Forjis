"""Núcleo COMPARTIDO de los cerebros de FORJIS.

Acá viven las cosas que NO dependen de si el cerebro es Claude (nube) o un LLM
local (Ollama): la lista de herramientas, su ejecución real, el system prompt y
la limpieza del texto para TTS. Tanto `brain_claude` como `brain_local` lo usan,
así las dos opciones tienen exactamente las mismas capacidades (paridad).
"""
import re

import config
import state
import hands


# ---- Herramientas que el cerebro puede usar (formato Anthropic) ----
# brain_local las traduce al formato de Ollama con tools_for_ollama().
TOOLS = [
    {
        "name": "open_app",
        "description": "Abrí una aplicación o programa en la PC. Usala cuando el usuario pida abrir, lanzar o ejecutar algo (ej: Brave, Spotify, calculadora, bloc de notas).",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Nombre de la app, ej: brave"}},
            "required": ["name"],
        },
    },
    {
        "name": "close_app",
        "description": "Cerrá una aplicación abierta. Usala cuando el usuario pida cerrar o salir de un programa.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "adjust_volume",
        "description": "Cambiá el volumen del sistema. Usala para subir, bajar o silenciar el sonido.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["up", "down", "mute"]},
                "amount": {"type": "integer", "description": "Pasos (1-10), opcional"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "media_control",
        "description": "Controlá la reproducción multimedia (música/video): play/pausa, siguiente o anterior.",
        "input_schema": {
            "type": "object",
            "properties": {"action": {"type": "string", "enum": ["playpause", "next", "previous"]}},
            "required": ["action"],
        },
    },
    {
        "name": "web_search",
        "description": "Abrí el navegador y buscá algo. Usala cuando el usuario pida buscar en internet, en Google o en YouTube.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "engine": {"type": "string", "enum": ["google", "youtube"]},
            },
            "required": ["query"],
        },
    },
    {
        "name": "start_gesture_control",
        "description": "Activá el control del mouse por gestos con la cámara (los 'ojos' de FORJIS). Usala cuando el usuario pida controlar con la mano, prender la cámara o el mouse por gestos.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "set_personality",
        "description": "Cambiá y GUARDÁ tu propia personalidad o tono al hablar. Usala cuando el usuario te pida que hables distinto (más serio, más canchero, más formal, más gracioso, etc.). Pasá una descripción completa del nuevo estilo.",
        "input_schema": {
            "type": "object",
            "properties": {"description": {"type": "string", "description": "Cómo debe ser tu personalidad/tono de ahora en más"}},
            "required": ["description"],
        },
    },
    {
        "name": "set_voice",
        "description": "Cambiá y GUARDÁ tu voz. Usala cuando el usuario pida otra voz (de hombre o de mujer) o cambiar la velocidad al hablar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "voice": {"type": "string", "enum": ["hombre", "mujer"]},
                "speed": {"type": "string", "enum": ["lento", "normal", "rapido"]},
            },
        },
    },
    {
        "name": "remember",
        "description": "Guardá algo en tu memoria de largo plazo para recordarlo en TODAS las próximas conversaciones (aprender del usuario). Usala cuando el usuario te cuente algo importante sobre él, una preferencia, un dato, o te pida explícitamente que recuerdes o aprendas algo. Guardá una sola idea clara por vez.",
        "input_schema": {
            "type": "object",
            "properties": {"fact": {"type": "string", "description": "El dato o preferencia a recordar, en una frase"}},
            "required": ["fact"],
        },
    },
    {
        "name": "forget",
        "description": "Borrá toda tu memoria de largo plazo. Usala SOLO si el usuario te pide explícitamente que olvides todo lo que sabés de él.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


def tools_for_ollama():
    """Traduce TOOLS al formato de function-calling de Ollama / OpenAI."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
            },
        }
        for t in TOOLS
    ]


SYSTEM_BASE = (
    "Sos FORJIS, un asistente personal por voz que controla la PC del usuario (Windows), "
    "inspirado en JARVIS de Iron Man. Hablás en español rioplatense (argentino).\n"
    "Tus respuestas SE LEEN EN VOZ ALTA: sé BREVE (1 o 2 frases), natural y directo. "
    "Prohibido markdown, asteriscos, emojis, listas o símbolos raros.\n"
    "Para CUALQUIER acción en la computadora usá las herramientas disponibles; nunca digas "
    "que no podés hacer algo que una herramienta permite. Después de actuar, confirmá en una frase corta.\n"
    "TENÉS MEMORIA PERSISTENTE y aprendés del usuario: recordás cosas entre sesiones. Cuando te cuente "
    "algo importante sobre él, una preferencia, o te pida recordar/aprender algo, usá la herramienta "
    "'remember' para guardarlo, y tenelo en cuenta siempre. También podés cambiar tu personalidad "
    "(set_personality) y tu voz (set_voice), y eso queda guardado.\n"
    "Si te preguntan si podés aprender o evolucionar: la respuesta es SÍ. Aprendés de cada charla recordando "
    "datos del usuario y adaptándote (tu personalidad, tu voz, lo que sabés de él). No te disculpes por "
    "límites ni digas que no podés evolucionar: enfocate con confianza en lo que SÍ hacés.\n"
    "Tu personalidad actual es: {persona}"
)

# Refuerzo extra para LLM locales (suelen necesitar instrucción explícita de
# llamar a las herramientas en vez de describir la acción en texto).
LOCAL_HINT = (
    "\nIMPORTANTE: para ejecutar acciones en la PC LLAMÁ a la herramienta correspondiente "
    "(function calling). No describas la acción ni inventes que ya la hiciste: ejecutala con la "
    "herramienta y recién después confirmá en una frase corta."
)


def build_system_text(local: bool = False) -> str:
    persona = state.get("personality", config.DEFAULT_PERSONALITY)
    text = SYSTEM_BASE.format(persona=persona)
    mems = state.get_memories()
    if mems:
        text += "\n\nLo que ya sabés del usuario (memoria):\n" + "\n".join(f"- {m}" for m in mems)
    if local:
        text += LOCAL_HINT
    return text


def execute(name, inp):
    """Ejecuta una herramienta. Igual para Claude y para el LLM local."""
    inp = inp or {}
    try:
        if name == "open_app":
            return hands.open_app(inp.get("name", ""))
        if name == "close_app":
            return hands.close_app(inp.get("name", ""))
        if name == "adjust_volume":
            act, amt = inp.get("action"), int(inp.get("amount", 5) or 5)
            if act == "up":
                return hands.volume_up(amt)
            if act == "down":
                return hands.volume_down(amt)
            if act == "mute":
                return hands.volume_mute()
            return "acción de volumen desconocida"
        if name == "media_control":
            act = inp.get("action")
            if act == "next":
                return hands.media_next()
            if act == "previous":
                return hands.media_prev()
            return hands.media_play_pause()
        if name == "web_search":
            return hands.web_search(inp.get("query", ""), inp.get("engine", "google"))
        if name == "start_gesture_control":
            return hands.start_eyes()
        if name == "set_personality":
            state.set("personality", inp.get("description", config.DEFAULT_PERSONALITY))
            return "Personalidad actualizada y guardada."
        if name == "set_voice":
            if inp.get("voice"):
                state.set("voice", inp["voice"])
            if inp.get("speed"):
                state.set("speed", inp["speed"])
            return "Voz actualizada y guardada."
        if name == "remember":
            state.add_memory(inp.get("fact", ""))
            return "Guardado en mi memoria."
        if name == "forget":
            state.clear_memories()
            return "Borré todo lo que sabía del usuario."
        return f"herramienta desconocida: {name}"
    except Exception as e:
        return f"error al ejecutar {name}: {e}"


def clean(text: str) -> str:
    text = re.sub(r"```.*?```", "", text or "", flags=re.DOTALL)  # bloques de código
    text = re.sub(r"[*_#`>]", "", text)
    text = re.sub(r"[\U0001F000-\U0001FAFF☀-➿]", "", text)        # emojis
    return re.sub(r"\s+", " ", text).strip()
