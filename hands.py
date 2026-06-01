"""Las 'manos' de FORJIS: ejecuta acciones reales en la PC."""
import os
import sys
import subprocess
import webbrowser
import urllib.parse
from datetime import datetime

import pyautogui

import config


def open_app(name: str) -> str:
    """Abre una app conocida o intenta lanzarla por nombre."""
    name = name.strip().lower()
    target = config.KNOWN_APPS.get(name)

    if target:
        try:
            if target.endswith(":") or target.startswith("ms-"):
                # protocolo (spotify:, ms-settings:, etc.)
                os.startfile(target)
            elif os.path.isabs(target):
                if os.path.exists(target):
                    subprocess.Popen([target])
                else:
                    # la ruta fija no existe en esta PC -> probar por nombre (App Paths)
                    subprocess.Popen(f'start "" "{os.path.basename(target)}"', shell=True)
            else:
                subprocess.Popen(target, shell=True)
            return f"Abriendo {name}."
        except Exception as e:
            return f"No pude abrir {name}: {e}"

    # Fallback: intentar lanzarlo por nombre vía el shell de Windows
    try:
        subprocess.Popen(f'start "" "{name}"', shell=True)
        return f"Intentando abrir {name}."
    except Exception:
        return f"No conozco la aplicación {name}."


def close_app(name: str) -> str:
    name = name.strip().lower()
    exe_map = {
        "brave": "brave.exe", "navegador": "brave.exe",
        "bloc de notas": "notepad.exe", "notepad": "notepad.exe",
        "calculadora": "Calculator.exe", "spotify": "spotify.exe",
    }
    exe = exe_map.get(name, name if name.endswith(".exe") else name + ".exe")
    try:
        subprocess.run(["taskkill", "/IM", exe, "/F"],
                       capture_output=True, check=False)
        return f"Cerrando {name}."
    except Exception as e:
        return f"No pude cerrar {name}: {e}"


def volume_up(steps: int = 5) -> str:
    for _ in range(steps):
        pyautogui.press("volumeup")
    return "Subiendo el volumen."


def volume_down(steps: int = 5) -> str:
    for _ in range(steps):
        pyautogui.press("volumedown")
    return "Bajando el volumen."


def volume_mute() -> str:
    pyautogui.press("volumemute")
    return "Silencio."


def media_play_pause() -> str:
    pyautogui.press("playpause")
    return "Listo."


def media_next() -> str:
    pyautogui.press("nexttrack")
    return "Siguiente."


def media_prev() -> str:
    pyautogui.press("prevtrack")
    return "Anterior."


def web_search(query: str, engine: str = "google") -> str:
    q = urllib.parse.quote(query)
    urls = {
        "google": f"https://www.google.com/search?q={q}",
        "youtube": f"https://www.youtube.com/results?search_query={q}",
    }
    webbrowser.open(urls.get(engine, urls["google"]))
    return f"Buscando {query} en {engine}."


def start_eyes() -> str:
    """Lanza el control del mouse por gestos (eyes.py) en un proceso aparte."""
    try:
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eyes.py")
        subprocess.Popen([sys.executable, script])
        return "Activando el control por gestos. Mirá la cámara y mové el índice."
    except Exception as e:
        return f"No pude activar los ojos: {e}"


def tell_time() -> str:
    now = datetime.now()
    return f"Son las {now.hour} y {now.minute:02d}."


def tell_date() -> str:
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    now = datetime.now()
    return f"Hoy es {dias[now.weekday()]} {now.day} de {meses[now.month - 1]}."
