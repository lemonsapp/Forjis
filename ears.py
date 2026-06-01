"""Los 'oídos' de FORJIS: captura voz del micrófono y la transcribe.

VAD por energía (auto-calibrado) -> graba la frase -> normaliza volumen ->
Whisper (offline, con pista de contexto y filtro anti-alucinaciones) -> texto.
"""
import collections

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

import config
import audio_dev


class Ears:
    def __init__(self):
        self.device, dev_name = audio_dev.resolve("input", config.INPUT_DEVICE_MATCH)
        # Cuántos canales tiene la entrada (SSL 2 = 2). Capturamos hasta 2 y los mezclamos.
        self.channels = 1
        if self.device is not None:
            try:
                self.channels = min(2, sd.query_devices(self.device)["max_input_channels"])
            except Exception:
                self.channels = 1
            print(f"[FORJIS] Micrófono: [{self.device}] {dev_name} ({self.channels} canal/es)")
        else:
            print(f"[FORJIS] OJO: no encontré '{config.INPUT_DEVICE_MATCH}', "
                  f"uso el micrófono por defecto.")

        print(f"[FORJIS] Cargando modelo de voz (Whisper '{config.WHISPER_MODEL}')...")
        self.model = WhisperModel(
            config.WHISPER_MODEL, device="cpu", compute_type=config.WHISPER_COMPUTE,
        )
        self.sr = config.SAMPLE_RATE
        self.block = config.BLOCK_SIZE
        self.block_dur = self.block / self.sr
        self.threshold = config.SILENCE_THRESHOLD_FLOOR
        print("[FORJIS] Modelo de voz listo.")

    def _rms(self, frame: np.ndarray) -> float:
        return float(np.sqrt(np.mean(np.square(frame))) + 1e-9)

    def _stream(self):
        return sd.InputStream(samplerate=self.sr, channels=self.channels,
                              dtype="float32", blocksize=self.block, device=self.device)

    def _to_mono(self, data: np.ndarray) -> np.ndarray:
        """Suma los canales -> captura el mic esté en input 1 o 2 del SSL 2."""
        if data.ndim == 2 and data.shape[1] > 1:
            return data.sum(axis=1)
        return data[:, 0]

    def calibrate(self):
        n = int(config.CALIB_SECONDS / self.block_dur)
        levels = []
        with self._stream() as stream:
            for _ in range(n):
                data, _ = stream.read(self.block)
                levels.append(self._rms(self._to_mono(data)))
        noise = float(np.median(levels)) if levels else 0.0
        self.threshold = max(config.SILENCE_THRESHOLD_FLOOR, noise * config.CALIB_FACTOR)
        print(f"[FORJIS] Ruido de fondo: {noise:.4f}  ->  umbral: {self.threshold:.4f}")

    def listen_utterance(self, on_level=None, detect_clap=False):
        """Bloquea hasta capturar UNA frase. Devuelve texto transcrito o None.
        on_level(float 0..1): callback opcional con el nivel del micrófono por bloque.
        detect_clap: si True, devuelve '__CLAP__' al detectar un doble aplauso."""
        pad = collections.deque(maxlen=config.PRE_SPEECH_PAD_BLOCKS)
        buffer = []
        triggered = False
        silence_acc = 0.0
        total = 0.0
        elapsed = 0.0
        last_clap_t = None

        with self._stream() as stream:
            while True:
                data, _ = stream.read(self.block)
                frame = self._to_mono(data).copy()
                level = self._rms(frame)
                elapsed += self.block_dur

                if on_level is not None:
                    norm = min(1.0, level / max(self.threshold * 6.0, 1e-6))
                    try:
                        on_level(norm)
                    except Exception:
                        pass

                if not triggered:
                    pad.append(frame)
                    # Detección de aplauso (transitorio impulsivo) antes del VAD de voz
                    if detect_clap and config.CLAP_ENABLED:
                        peak = float(np.max(np.abs(frame)))
                        crest = peak / max(level, 1e-6)
                        if peak > config.CLAP_PEAK and crest > config.CLAP_CREST:
                            if (last_clap_t is not None and
                                    config.CLAP_GAP_MIN <= (elapsed - last_clap_t) <= config.CLAP_GAP_MAX):
                                return "__CLAP__"
                            last_clap_t = elapsed
                            continue  # no dejar que el aplauso dispare el VAD de voz
                    if level > self.threshold:
                        triggered = True
                        buffer = list(pad)
                        buffer.append(frame)
                        silence_acc = 0.0
                        total = len(buffer) * self.block_dur
                else:
                    buffer.append(frame)
                    total += self.block_dur
                    if level < self.threshold:
                        silence_acc += self.block_dur
                        if silence_acc >= config.SILENCE_DURATION:
                            break
                    else:
                        silence_acc = 0.0
                    if total >= config.MAX_UTTERANCE:
                        break

        if total < config.MIN_UTTERANCE:
            return None

        audio = np.concatenate(buffer).astype(np.float32)
        audio = self._normalize(audio)
        return self._transcribe(audio)

    def _normalize(self, audio: np.ndarray) -> np.ndarray:
        """Amplifica la frase a un pico fijo (ayuda si hablás bajo)."""
        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        if peak > 1e-4:
            audio = audio * (config.NORMALIZE_PEAK / peak)
        return np.clip(audio, -1.0, 1.0)

    def _transcribe(self, audio: np.ndarray):
        segments, _ = self.model.transcribe(
            audio,
            language=config.LANGUAGE,
            beam_size=config.WHISPER_BEAM,
            temperature=0.0,
            initial_prompt=config.WHISPER_INITIAL_PROMPT,
            condition_on_previous_text=False,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=300),
            no_speech_threshold=0.6,
            log_prob_threshold=-1.0,
        )
        parts = [s.text for s in segments if s.no_speech_prob < 0.6]
        text = "".join(parts).strip()
        if not text or self._is_hallucination(text):
            return None
        return text

    def _is_hallucination(self, text: str) -> bool:
        low = text.lower().strip(" .,!¡¿?")
        if len(low) < 3:
            return True
        for h in config.HALLUCINATIONS:
            if h in low:
                return True
        return False


def split_wake_word(text: str):
    """Si el texto contiene la wake word, devuelve (True, comando_restante).
    Si no, (False, None). Acepta variantes de cómo Whisper oye 'forjis'."""
    low = text.lower()
    for w in config.WAKE_WORDS:
        idx = low.find(w)
        if idx != -1:
            rest = text[idx + len(w):]
            rest = rest.lstrip(" ,.:;¡!¿?").strip()
            return True, rest
    return False, None
