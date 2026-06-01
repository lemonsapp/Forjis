"""Cerebro de FORJIS — DISPATCHER de dos opciones intercambiables:

  - "claude"  -> brain_claude  (nube, Anthropic API; más inteligente, necesita key)
  - "local"   -> brain_local   (Ollama offline; 100% gratis, sin conexión)

El resto del sistema (server.py, forjis.py, app.py) sigue usando `brain.handle()`,
`brain.available()` y `brain.reset()` sin enterarse de cuál está activo.

¿Cuál se usa? En este orden:
  1. variable de entorno FORJIS_BRAIN ("claude" | "local")  ← override por launcher
  2. lo guardado en forjis_state.json (lo que elijas en la HUD o el instalador)
  3. config.DEFAULT_BRAIN
"""
import os

import config
import state
import brain_claude
import brain_local

_BACKENDS = {"claude": brain_claude, "local": brain_local}


def get_backend_name() -> str:
    env = os.environ.get("FORJIS_BRAIN", "").strip().lower()
    if env in _BACKENDS:
        return env
    saved = state.get("brain", None)
    if saved in _BACKENDS:
        return saved
    return config.DEFAULT_BRAIN if config.DEFAULT_BRAIN in _BACKENDS else "claude"


def _backend():
    return _BACKENDS.get(get_backend_name(), brain_claude)


def set_backend(name: str):
    """Cambia el cerebro y lo deja guardado. Devuelve el nombre aplicado o None."""
    name = (name or "").strip().lower()
    if name not in _BACKENDS:
        return None
    state.set("brain", name)
    reset()  # que no se mezcle el historial de un cerebro con el del otro
    return name


def current_model() -> str:
    return config.LLM_MODEL if get_backend_name() == "local" else config.CLAUDE_MODEL


def backend_label() -> str:
    name = get_backend_name()
    if name == "local":
        return f"Local · {config.LLM_MODEL}"
    return f"Claude · {config.CLAUDE_MODEL}"


def handle(command: str) -> str:
    return _backend().handle(command)


def available() -> bool:
    return _backend().available()


def reset():
    brain_claude.reset()
    brain_local.reset()
