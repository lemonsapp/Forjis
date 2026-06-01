"""Cerebro de FORJIS — opción NUBE: Claude (Anthropic API) con tool use.

Más inteligente y rápido para decidir acciones, pero necesita API key y conexión.
Comparte herramientas/acciones/system con `brain_core` para tener paridad con el
cerebro local.
"""
from datetime import datetime

import anthropic

import config
import state
import brain_core

_client = None
_history = []  # memoria de conversación de la sesión


def _get_client():
    global _client
    if _client is None:
        key = config.get_api_key()
        if not key:
            return None
        _client = anthropic.Anthropic(api_key=key)
    return _client


def available() -> bool:
    return config.get_api_key() is not None


def _system_blocks():
    return [{
        "type": "text",
        "text": brain_core.build_system_text(local=False),
        "cache_control": {"type": "ephemeral"},
    }]


def handle(command: str) -> str:
    """Recibe el comando (sin la wake word) y devuelve la respuesta hablada."""
    command = (command or "").strip()
    if not command:
        return "¿Sí? Decime."

    client = _get_client()
    if client is None:
        return ("No tengo conectado el cerebro de Claude. Falta la clave de Anthropic. "
                "Ponela en api_key.txt o en la variable ANTHROPIC_API_KEY, o cambiá a modo local.")

    ahora = datetime.now().strftime("%A %d/%m/%Y %H:%M")
    _history.append({"role": "user", "content": f"(Contexto: ahora es {ahora}) {command}"})
    _heal_history()  # por si quedó un tool_result colgado de una vuelta anterior

    try:
        for _ in range(6):  # límite de vueltas de herramientas
            resp = client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=config.CLAUDE_MAX_TOKENS,
                system=_system_blocks(),
                tools=brain_core.TOOLS,
                messages=_history,
            )
            _history.append({"role": "assistant", "content": resp.content})

            if resp.stop_reason == "tool_use":
                results = []
                for block in resp.content:
                    if block.type == "tool_use":
                        out = brain_core.execute(block.name, block.input or {})
                        results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": out,
                        })
                _history.append({"role": "user", "content": results})
                continue
            break

        text = "".join(b.text for b in resp.content if b.type == "text").strip()
    except anthropic.AuthenticationError:
        return "La clave de Anthropic no es válida. Revisá api_key.txt."
    except anthropic.APIConnectionError:
        return "No tengo internet para pensar eso ahora."
    except Exception as e:
        return f"Tuve un problema: {e}"

    # Limitar memoria, cortando siempre en un turno de usuario válido
    if len(_history) > config.CLAUDE_HISTORY_MAX:
        del _history[: len(_history) - config.CLAUDE_HISTORY_MAX]
        _heal_history()

    return brain_core.clean(text) or "Listo."


def _heal_history():
    """El primer mensaje del historial debe ser un turno de usuario (texto).
    Así ningún `tool_result` queda sin su `tool_use` previo (evita el error 400)."""
    while _history and not (
        isinstance(_history[0], dict)
        and _history[0].get("role") == "user"
        and isinstance(_history[0].get("content"), str)
    ):
        _history.pop(0)


def reset():
    _history.clear()
