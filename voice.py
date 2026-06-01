"""La 'voz' de FORJIS: texto -> habla (Piper, offline).
La voz y la velocidad se leen del estado persistente (cambiables por voz).
Reproduce por el dispositivo de salida elegido (SSL 2).
"""
import os
import wave
import winsound

import numpy as np
import sounddevice as sd
from piper import PiperVoice
try:
    from piper import SynthesisConfig
except Exception:
    SynthesisConfig = None

import config
import state
import audio_dev

_loaded = {}            # cache de voces cargadas por path
_out_device = None
_out_resolved = False


def _get_voice():
    name = state.get("voice", "hombre")
    path = config.PIPER_VOICES.get(name, config.PIPER_VOICES["hombre"])
    if not os.path.exists(path):
        path = config.PIPER_VOICES["hombre"]
    if path not in _loaded:
        print(f"[FORJIS] Cargando voz ({name})...")
        _loaded[path] = PiperVoice.load(path)
    return _loaded[path]


def _get_output():
    global _out_device, _out_resolved
    if not _out_resolved:
        _out_device, nm = audio_dev.resolve("output", config.OUTPUT_DEVICE_MATCH)
        if _out_device is not None:
            print(f"[FORJIS] Salida de audio: [{_out_device}] {nm}")
        _out_resolved = True
    return _out_device


def say(text: str):
    if not text:
        return
    print(f"FORJIS> {text}")
    try:
        voice = _get_voice()
        cfg = None
        if SynthesisConfig is not None:
            scale = config.SPEED_SCALE.get(state.get("speed", "normal"), 1.0)
            cfg = SynthesisConfig(length_scale=scale)
        with wave.open(config.TMP_WAV, "wb") as wf:
            if cfg is not None:
                voice.synthesize_wav(text, wf, syn_config=cfg)
            else:
                voice.synthesize_wav(text, wf)
        _play(config.TMP_WAV)
    except Exception as e:
        print(f"[FORJIS] (no pude hablar: {e})")


def _play(path: str):
    out = _get_output()
    try:
        with wave.open(path, "rb") as wf:
            rate, ch = wf.getframerate(), wf.getnchannels()
            frames = wf.readframes(wf.getnframes())
        data = np.frombuffer(frames, dtype=np.int16)
        if ch > 1:
            data = data.reshape(-1, ch)
        sd.play(data, samplerate=rate, device=out)
        sd.wait()
    except Exception as e:
        print(f"[FORJIS] (salida SSL falló, uso default: {e})")
        winsound.PlaySound(path, winsound.SND_FILENAME)


def beep():
    try:
        winsound.Beep(880, 120)
    except Exception:
        pass


if __name__ == "__main__":
    say("Hola, soy FORJIS. Probando la voz.")
