"""Cerebro de FORJIS — opción FREE: LLM local vía Ollama (100% offline, gratis).

Usa function-calling de Ollama con las MISMAS herramientas que el cerebro Claude
(abrir apps, volumen, buscar, gestos, voz, memoria), así el modo gratis controla
la PC igual que el de pago. Modelo por defecto: qwen2.5:7b (ver config.LLM_MODEL).

Requisitos: tener Ollama corriendo (https://ollama.com) y el modelo descargado
(`ollama pull qwen2.5:7b`). El instalador y setup_local.bat lo dejan listo.
"""
import os
import json
import time
import shutil
import subprocess

import requests

import config
import brain_core

_history = []  # [{"role":"user"/"assistant","content":str}] de la sesión


def reset():
    _history.clear()


def _ollama_exe():
    """Encuentra el ejecutable de Ollama (PATH o instalación típica en Windows)."""
    exe = shutil.which("ollama")
    if exe:
        return exe
    cand = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe")
    return cand if os.path.isfile(cand) else None


def _server_alive() -> bool:
    """¿Responde el server de Ollama (sin importar si el modelo está bajado)?"""
    try:
        return requests.get(config.OLLAMA_TAGS_URL, timeout=3).status_code == 200
    except Exception:
        return False


def ensure_server(timeout: float = 20.0) -> bool:
    """Si Ollama no está corriendo, lo levanta (`ollama serve`) y espera a que responda."""
    if _server_alive():
        return True
    exe = _ollama_exe()
    if not exe:
        return False
    try:
        flags = 0
        if os.name == "nt":
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
        subprocess.Popen([exe, "serve"], creationflags=flags,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         stdin=subprocess.DEVNULL)
    except Exception:
        return False
    end = time.time() + timeout
    while time.time() < end:
        if _server_alive():
            return True
        time.sleep(0.5)
    return False


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
        # Quizás Ollama solo estaba apagado: lo levantamos y reintentamos.
        ensure_server()
        if not available():
            if _server_alive():
                return (f"Ollama está corriendo pero no encuentro el modelo {config.LLM_MODEL}. "
                        "Bajalo con 'ollama pull " + config.LLM_MODEL + "', o cambiá a modo Claude.")
            return ("No pude arrancar el cerebro local. Fijate que Ollama esté instalado, "
                    "o cambiá a modo Claude.")

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
