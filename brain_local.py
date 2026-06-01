"""Cerebro de FORJIS — opción FREE: LLM local vía Ollama (100% offline, gratis).

Usa function-calling de Ollama con las MISMAS herramientas que el cerebro Claude
(abrir apps, volumen, buscar, gestos, voz, memoria), así el modo gratis controla
la PC igual que el de pago. Modelo por defecto: qwen2.5:7b (ver config.LLM_MODEL).

Requisitos: tener Ollama corriendo (https://ollama.com) y el modelo descargado
(`ollama pull qwen2.5:7b`). El instalador y setup_local.bat lo dejan listo.
"""
import json

import requests

import config
import brain_core

_history = []  # [{"role":"user"/"assistant","content":str}] de la sesión


def reset():
    _history.clear()


def available() -> bool:
    """¿Está Ollama vivo y con el modelo descargado?"""
    try:
        r = requests.get(config.OLLAMA_TAGS_URL, timeout=3)
        if r.status_code != 200:
            return False
        names = [m.get("name", "") for m in r.json().get("models", [])]
        base = config.LLM_MODEL.split(":")[0]
        return any(base in n for n in names)
    except Exception:
        return False


def _chat(messages):
    r = requests.post(
        config.OLLAMA_URL,
        json={
            "model": config.LLM_MODEL,
            "messages": messages,
            "tools": brain_core.tools_for_ollama(),
            "stream": False,
            "options": {
                "temperature": config.LLM_TEMPERATURE,
                "num_predict": config.LLM_NUM_PREDICT,
            },
        },
        timeout=config.LLM_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def _args(raw):
    """Los argumentos de un tool_call pueden venir como dict o como string JSON."""
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw or "{}")
        except Exception:
            return {}
    return {}


def handle(command: str) -> str:
    command = (command or "").strip()
    if not command:
        return "¿Sí? Decime."

    if not available():
        return ("No tengo el cerebro local listo. Fijate que Ollama esté corriendo y que el modelo "
                "esté descargado, o cambiá a modo Claude.")

    convo = [{"role": "system", "content": brain_core.build_system_text(local=True)}]
    convo += _history
    convo.append({"role": "user", "content": command})

    final = ""
    try:
        for _ in range(6):  # límite de vueltas de herramientas
            data = _chat(convo)
            msg = data.get("message", {}) or {}
            calls = msg.get("tool_calls") or []
            # Re-armamos el mensaje del asistente para mantener el contexto de la charla
            asst = {"role": "assistant", "content": msg.get("content", "") or ""}
            if calls:
                asst["tool_calls"] = calls
            convo.append(asst)

            if calls:
                for c in calls:
                    fn = c.get("function", {}) or {}
                    name = fn.get("name", "")
                    out = brain_core.execute(name, _args(fn.get("arguments")))
                    convo.append({"role": "tool", "name": name, "content": str(out)})
                continue

            final = msg.get("content", "") or ""
            break
    except requests.exceptions.ConnectionError:
        return "No tengo el cerebro local conectado. Fijate que Ollama esté corriendo."
    except requests.exceptions.Timeout:
        return "El cerebro local tardó demasiado. Probá con un modelo más liviano."
    except Exception as e:
        return f"Tuve un problema pensando eso: {e}"

    # Guardamos solo el turno limpio (usuario + respuesta final) para la próxima vuelta.
    _history.append({"role": "user", "content": command})
    _history.append({"role": "assistant", "content": final})
    keep = config.LLM_HISTORY_TURNS * 2
    if len(_history) > keep:
        del _history[: len(_history) - keep]

    return brain_core.clean(final) or "Listo."


if __name__ == "__main__":
    print("Ollama disponible:", available())
    print(handle("Hola, ¿quién sos y qué podés hacer?"))
