"""Servidor web de FORJIS: HUD visual + WebSocket en tiempo real.

Corre el cerebro/oídos/voz de FORJIS y empuja eventos a la pantalla.
Modo normal:  python server.py        (con micrófono)
Modo visual:  FORJIS_MOCK=1 python server.py   (sin mic, para probar la UI/voz)
"""
import os
import json
import time
import asyncio
import threading
from contextlib import asynccontextmanager

import psutil
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

import config
import state
import brain
import voice

clients = set()
main_loop = None
proc_lock = threading.Lock()
MOCK = os.environ.get("FORJIS_MOCK") == "1"
WEB_DIR = os.path.join(config.BASE_DIR, "web")


@asynccontextmanager
async def lifespan(app):
    global main_loop
    main_loop = asyncio.get_running_loop()
    threading.Thread(target=brain.warmup, daemon=True).start()  # levanta Ollama si el cerebro es local
    threading.Thread(target=telemetry_loop, daemon=True).start()
    if not MOCK:
        threading.Thread(target=audio_loop, daemon=True).start()
    else:
        set_state("idle")
    yield


app = FastAPI(lifespan=lifespan)


# ---------- difusión de eventos ----------
def emit(event: dict):
    if main_loop is None:
        return
    try:
        asyncio.run_coroutine_threadsafe(_broadcast(event), main_loop)
    except Exception:
        pass


async def _broadcast(event: dict):
    msg = json.dumps(event, ensure_ascii=False)
    dead = []
    for ws in list(clients):
        try:
            await ws.send_text(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)


def set_state(s: str):
    emit({"type": "state", "value": s})


def info_event() -> dict:
    return {
        "type": "info",
        "brain": "on" if brain.available() else "off",
        "backend": brain.get_backend_name(),     # "claude" | "local"
        "model": brain.current_model(),
        "voice": state.get("voice", "hombre"),
        "speed": state.get("speed", "normal"),
        "personality": state.get("personality", config.DEFAULT_PERSONALITY),
        "wake": config.WAKE_NAME,
        "mock": MOCK,
    }


# ---------- procesamiento de un comando ----------
def process_command(text: str, source: str = "voz"):
    with proc_lock:
        emit({"type": "heard", "text": text, "source": source})
        set_state("thinking")
        try:
            reply = brain.handle(text)
        except Exception as e:
            reply = f"Tuve un problema: {e}"
        emit({"type": "reply", "text": reply})
        set_state("speaking")
        voice.say(reply)
        set_state("idle")
        emit(info_event())  # por si cambió voz/personalidad


# ---------- bucle de audio (hilo) ----------
def audio_loop():
    from ears import Ears, split_wake_word
    set_state("loading")
    try:
        ears = Ears()
        ears.calibrate()
    except Exception as e:
        emit({"type": "reply", "text": f"No pude iniciar el micrófono: {e}"})
        set_state("off")
        return

    set_state("idle")
    greet = f"{config.WAKE_NAME} en línea."
    emit({"type": "reply", "text": greet})
    voice.say(greet)

    lvl = lambda l: emit({"type": "level", "value": round(l, 3)})

    def capture_and_process():
        voice.beep()
        set_state("listening")
        cmd = ears.listen_utterance(on_level=lvl)
        set_state("idle")
        if cmd and cmd != "__CLAP__":
            process_command(cmd, "voz")

    while True:
        try:
            set_state("idle")
            res = ears.listen_utterance(on_level=lvl, detect_clap=True)
            if res == "__CLAP__":
                emit({"type": "clap"})
                capture_and_process()
                continue
            text = res
            if not text:
                continue
            emit({"type": "partial", "text": text})
            has, cmd = split_wake_word(text)
            if not has:
                continue
            if not cmd:
                capture_and_process()
                continue
            process_command(cmd, "voz")
        except Exception as e:
            emit({"type": "reply", "text": f"Error: {e}"})
            set_state("idle")


def telemetry_loop():
    try:
        psutil.cpu_percent()  # primer llamado (calibra)
    except Exception:
        pass
    start = time.time()
    while True:
        time.sleep(config.TELEMETRY_INTERVAL)
        try:
            emit({
                "type": "telemetry",
                "cpu": round(psutil.cpu_percent(), 1),
                "ram": round(psutil.virtual_memory().percent, 1),
                "up": int(time.time() - start),
            })
        except Exception:
            pass


def demo():
    """Pequeña demo para ver la HUD viva (sin mic ni API)."""
    seq = [
        ("listening", "Te escucho...", 1.2),
        ("thinking", None, 1.0),
        ("speaking", "Hola jefe, soy FORJIS. La interfaz está funcionando.", 0),
    ]
    for st, txt, wait in seq:
        set_state(st)
        if txt and st == "speaking":
            emit({"type": "reply", "text": txt})
            voice.say(txt)
        elif txt:
            emit({"type": "heard", "text": txt, "source": "demo"})
        if wait:
            import time
            time.sleep(wait)
    set_state("idle")


# ---------- rutas ----------
@app.get("/")
def index():
    return FileResponse(os.path.join(WEB_DIR, "index.html"))


@app.get("/favicon.ico")
def favicon_ico():
    return FileResponse(os.path.join(WEB_DIR, "favicon.ico"))


@app.get("/favicon.svg")
def favicon_svg():
    return FileResponse(os.path.join(WEB_DIR, "favicon.svg"))


@app.get("/favicon.png")
def favicon_png():
    return FileResponse(os.path.join(WEB_DIR, "favicon.png"))


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    await websocket.send_text(json.dumps(info_event(), ensure_ascii=False))
    await websocket.send_text(json.dumps({"type": "state", "value": "idle"}))
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except Exception:
                continue
            await _handle_client(msg)
    except WebSocketDisconnect:
        clients.discard(websocket)
    except Exception:
        clients.discard(websocket)


async def _handle_client(msg: dict):
    t = msg.get("type")
    if t == "command":
        text = (msg.get("text") or "").strip()
        if text:
            threading.Thread(target=process_command, args=(text, "texto"), daemon=True).start()
    elif t == "set_voice":
        if msg.get("voice"):
            state.set("voice", msg["voice"])
        if msg.get("speed"):
            state.set("speed", msg["speed"])
        emit(info_event())
        threading.Thread(target=voice.say, args=("Voz actualizada.",), daemon=True).start()
    elif t == "set_personality":
        state.set("personality", (msg.get("text") or config.DEFAULT_PERSONALITY))
        emit(info_event())
    elif t == "set_brain":
        applied = brain.set_backend(msg.get("backend"))
        emit(info_event())
        if applied:
            label = "cerebro local, gratis y offline" if applied == "local" else "cerebro Claude"
            ready = brain.available()
            txt = f"Listo, cambié al {label}." if ready else (
                "Cambié al cerebro local, pero todavía no lo encuentro. Asegurate de que Ollama esté corriendo."
                if applied == "local" else
                "Cambié al cerebro Claude, pero falta la API key.")
            threading.Thread(target=voice.say, args=(txt,), daemon=True).start()
    elif t == "demo":
        threading.Thread(target=demo, daemon=True).start()


if __name__ == "__main__":
    print("=" * 50)
    print(f"  FORJIS HUD  ->  http://localhost:8000")
    print(f"  Modo: {'VISUAL (sin mic)' if MOCK else 'COMPLETO (con mic)'}")
    print("=" * 50)
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
    except OSError as e:
        print("\n[FORJIS] No pude usar el puerto 8000 — ya hay otro FORJIS abierto.")
        print("         Cerrá la otra ventana de FORJIS y volvé a intentar.")
        print(f"         (detalle: {e})")
        input("\nEnter para salir...")
