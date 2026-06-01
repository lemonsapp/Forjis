"""Descarga la voz de Piper (offline) para FORJIS."""
import os
import sys
import urllib.request

import config

BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/"
FEM = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/"
HAND = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
        "hand_landmarker/float16/1/hand_landmarker.task")
FILES = [
    ("es_ES-davefx-medium.onnx", BASE + "es_ES-davefx-medium.onnx?download=true"),
    ("es_ES-davefx-medium.onnx.json", BASE + "es_ES-davefx-medium.onnx.json?download=true"),
    ("es_ES-sharvard-medium.onnx", FEM + "es_ES-sharvard-medium.onnx?download=true"),
    ("es_ES-sharvard-medium.onnx.json", FEM + "es_ES-sharvard-medium.onnx.json?download=true"),
    ("hand_landmarker.task", HAND),  # Fase 3: detección de manos (MediaPipe Tasks)
]


def _progress(block_num, block_size, total_size):
    if total_size > 0:
        done = block_num * block_size
        pct = min(100, done * 100 // total_size)
        mb = done / (1024 * 1024)
        sys.stdout.write(f"\r   {pct:3d}%  ({mb:.1f} MB)")
        sys.stdout.flush()


def main():
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    for name, url in FILES:
        dest = os.path.join(config.MODELS_DIR, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            print(f"[ok] {name} ya existe")
            continue
        print(f"[..] Descargando {name}")
        urllib.request.urlretrieve(url, dest, _progress)
        print(f"\n[ok] {name} descargado")
    print("\nListo. Modelos de voz instalados.")


if __name__ == "__main__":
    main()
