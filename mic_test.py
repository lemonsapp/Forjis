# -*- coding: utf-8 -*-
"""Test de micrófono de FORJIS: muestra qué mic usa y cuánta señal entra."""
import sys
import time

import numpy as np
import sounddevice as sd

import config
import audio_dev

print("=" * 60)
print("  TEST DE MICROFONO - FORJIS")
print("=" * 60)

dev, name = audio_dev.resolve("input", config.INPUT_DEVICE_MATCH)
if dev is None:
    print(f"FORJIS usara: MICROFONO POR DEFECTO de Windows")
else:
    print(f"FORJIS usara: [{dev}] {name}")
print(f"(config.INPUT_DEVICE_MATCH = {config.INPUT_DEVICE_MATCH!r})")

print("\n--- Microfonos disponibles (MME) ---")
has = sd.query_hostapis()
for i, d in enumerate(sd.query_devices()):
    if has[d["hostapi"]]["name"] == "MME" and d["max_input_channels"] > 0:
        print(f"  [{i}] {d['name']}")

sr = 16000
block = 1600
try:
    ch = 1 if dev is None else min(2, sd.query_devices(dev)["max_input_channels"])
except Exception:
    ch = 1

print("\n>>> Escuchando 8 segundos. HABLA normal y despues APLAUDI fuerte 👏👏 <<<\n")
maxpeak = 0.0
maxrms = 0.0
try:
    with sd.InputStream(samplerate=sr, channels=ch, dtype="float32",
                        blocksize=block, device=dev) as st:
        t0 = time.time()
        while time.time() - t0 < 8:
            data, _ = st.read(block)
            mono = data.sum(axis=1) if (data.ndim == 2 and data.shape[1] > 1) else data[:, 0]
            rms = float(np.sqrt(np.mean(mono ** 2)))
            peak = float(np.max(np.abs(mono)))
            maxpeak = max(maxpeak, peak)
            maxrms = max(maxrms, rms)
            bar = "#" * int(min(1.0, rms * 20) * 45)
            print(f"\r nivel |{bar:<45}| rms={rms:.3f} peak={peak:.3f}", end="")
except Exception as e:
    print("\n\n[ERROR] No pude abrir el microfono:", e)
    print("=> En config.py proba poner:  INPUT_DEVICE_MATCH = \"\"")
    print("   (usa el microfono por defecto de Windows), o el nombre de otro mic de la lista.")
    input("\nEnter para salir...")
    sys.exit()

print(f"\n\nRESULTADO:  pico maximo = {maxpeak:.3f}   |   rms maximo = {maxrms:.3f}")
print(f"Referencia: umbral de voz ~{config.SILENCE_THRESHOLD_FLOOR}, aplauso necesita pico > {config.CLAP_PEAK}")

if maxpeak < 0.05:
    print("\n[!!] CASI NO ENTRO SENAL. Ese microfono no te esta escuchando.")
    print("     SOLUCIONES:")
    print("     1) En config.py cambia:  INPUT_DEVICE_MATCH = \"\"   (mic por defecto de Windows)")
    print("     2) O pone parte del nombre de tu mic real (de la lista de arriba).")
    print("     3) O subi la ganancia/volumen del microfono en Windows.")
elif maxpeak < config.CLAP_PEAK:
    print("\n[i] Te escucha pero la senal es baja para el aplauso.")
    print(f"    En config.py baja:  CLAP_PEAK = {round(maxpeak * 0.6, 2)}")
    print("    (y subi un poco la ganancia del mic si podes).")
else:
    print("\n[OK] Hay senal de sobra. La voz y el aplauso deberian andar.")
    print("     Si igual no engancha el aplauso, en config.py proba CLAP_CREST = 3.0")

print("\nCopiame este resultado y te digo exactamente que tocar.")
input("\nEnter para salir...")
