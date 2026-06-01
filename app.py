"""FORJIS como APP DE ESCRITORIO (ventana nativa, sin navegador).

Levanta el servidor por dentro y muestra la HUD en una ventana propia del sistema
(WebView2 de Windows). Para el usuario es una app, no un link a localhost.

Correr:  pythonw app.py   (sin consola)  ó  python app.py
"""
import time
import asyncio
import threading
import urllib.request

import uvicorn
import webview

import server as srv


class Api:
    """Funciones que la HUD puede llamar desde JS (window.pywebview.api.*)."""
    def close(self):
        for w in list(webview.windows):
            try:
                w.destroy()
            except Exception:
                pass

    def minimize(self):
        try:
            webview.windows[0].minimize()
        except Exception:
            pass

    def toggle_fullscreen(self):
        try:
            webview.windows[0].toggle_fullscreen()
        except Exception:
            pass


def _serve():
    config = uvicorn.Config(srv.app, host="127.0.0.1", port=8000, log_level="warning")
    s = uvicorn.Server(config)
    s.install_signal_handlers = lambda: None   # necesario fuera del hilo principal
    asyncio.run(s.serve())


def _wait_up(timeout=20.0):
    end = time.time() + timeout
    while time.time() < end:
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1)
            return True
        except Exception:
            time.sleep(0.25)
    return False


def main():
    threading.Thread(target=_serve, daemon=True).start()
    _wait_up()
    webview.create_window(
        "FORJIS",
        "http://127.0.0.1:8000",
        fullscreen=True,
        background_color="#02040a",
        js_api=Api(),
    )
    webview.start()


if __name__ == "__main__":
    main()
