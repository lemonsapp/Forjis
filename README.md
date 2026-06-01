# FORJIS 🔥🦾 — Tu propio JARVIS de Iron Man

Asistente de voz para Windows con **interfaz tipo JARVIS**: le hablás, controla tu PC,
te responde con voz, aprende de vos y tiene una HUD futurista con reactor animado.

> "FORJIS, abrí Brave" · "FORJIS, subí el volumen" · "FORJIS, contame un chiste" · 👏👏

![estado](https://img.shields.io/badge/plataforma-Windows-blue) ![python](https://img.shields.io/badge/python-3.10%2B-green) ![offline](https://img.shields.io/badge/voz-offline-success)

---

## ✨ Qué hace

- 🗣️ **Hablás y te entiende** — reconocimiento de voz local (Whisper), en español.
- 🧠 **Cerebro a elección** — **Claude** (nube, más inteligente) o **100% local y gratis**
  con [Ollama](https://ollama.com) (offline, sin costo). Lo elegís en el instalador y lo
  cambiás cuando quieras con un botón en la HUD. **Las dos opciones controlan la PC igual.**
- 🦾 **Controla la PC** — abre/cierra apps, volumen, multimedia, búsquedas en Google/YouTube.
- 🔊 **Te habla** — voz neural (Piper), de hombre o mujer, ajustable. 100% offline.
- 👁️ **Control por gestos** — mové el mouse con la mano usando la webcam.
- 🧩 **Aprende y recuerda** — guarda tus datos/preferencias entre sesiones.
- 🎨 **HUD JARVIS** — reactor reactivo, telemetría (CPU/RAM), reloj, secuencia de arranque.
- 👏 **Doble aplauso** para activarlo · 🔌 **arranca solo** al prender la PC.
- 🖥️ **App de escritorio** — ventana propia, sin navegador a la vista.

## 🚀 Instalación (1 clic)

> 🆕 **¿Nunca programaste?** Seguí la **[guía de cero para principiantes →
> `INSTALAR-DESDE-CERO.md`](INSTALAR-DESDE-CERO.md)** (instala Python, la API key y todo, paso a paso).

1. **Descargá** este repo (botón verde **Code → Download ZIP**) y descomprimilo.
2. Doble clic en **`install.bat`**. Hace todo solo: instala lo necesario, baja los modelos
   y te pregunta qué **cerebro** querés:
   - **[1] Claude** (nube) → te pide tu **API key de Anthropic**.
   - **[2] Local** (gratis) → instala **Ollama** y baja el modelo `qwen2.5:7b` (~4.7 GB).
3. Abrí FORJIS con el ícono **FORJIS** del Escritorio. ¡Listo!

> ¿Ya instalaste y querés pasar a modo gratis después? Doble clic en **`setup_local.bat`**
> (instala Ollama + el modelo y deja FORJIS en local). Para volver a Claude, usá el botón 🧠 de la HUD.

> ¿Se trabó algo? Mirá **`SETUP_PROMPT.md`**: tiene un prompt para pegarle a Claude y que
> te ayude a instalar y configurar lo que falte.

### Requisitos
- Windows 10/11
- **Para el cerebro Claude:** una **API key** de Anthropic → [console.anthropic.com](https://console.anthropic.com)
  (poné un tope de gasto; con Haiku son centavos) e internet.
- **Para el cerebro local (gratis):** [Ollama](https://ollama.com) (lo instala el instalador) y
  ~5 GB de disco. Anda en CPU, pero con **GPU** (4 GB+ de VRAM) vuela.
- Micrófono y parlantes
- (Opcional) webcam para los gestos

## 🎮 Cómo se usa

Decí **"FORJIS"** seguido de tu orden, o **aplaudí dos veces** 👏👏:

| Decís… | Hace… |
|---|---|
| "FORJIS, abrí Brave" | Abre la app |
| "FORJIS, subí el volumen" | Sube el volumen |
| "FORJIS, buscá gatos en YouTube" | Busca en YouTube |
| "FORJIS, hablame más serio y con voz de mujer" | Cambia personalidad + voz (y lo recuerda) |
| "FORJIS, recordá que soy productor musical" | Lo guarda para siempre |
| "FORJIS, activá el mouse" | Control por gestos con la webcam |

## ⚙️ Personalización (`config.py`)
- **Micrófono/parlante:** `INPUT_DEVICE_MATCH` / `OUTPUT_DEVICE_MATCH` — dejá `""` para el
  dispositivo por defecto de Windows, o poné parte del nombre de tu aparato (ej. `"SSL 2"`).
- **Cerebro:** se elige al instalar y se cambia con el botón 🧠 de la HUD (queda guardado).
  Defaults en `config.py`: `DEFAULT_BRAIN` (`claude`/`local`), `CLAUDE_MODEL`
  (`claude-haiku-4-5`) y `LLM_MODEL` (`qwen2.5:7b` para el modo local).
- **Reconocimiento:** `WHISPER_MODEL` (`small` por defecto; `medium` = más preciso pero más lento).
- **Aplauso:** `CLAP_PEAK` / `CLAP_CREST` si se activa solo o no engancha.

## 🧱 Cómo está hecho
`faster-whisper` (oídos) · cerebro intercambiable: **`Anthropic SDK`** (Claude) u **`Ollama`**
(LLM local), ambos con tool use · `piper-tts` (voz) · `opencv` + `mediapipe` (ojos) ·
`FastAPI` + `pywebview` (HUD/app) · `pyautogui` (acciones).

El cerebro es un dispatcher (`brain.py`) sobre `brain_claude.py` y `brain_local.py`, que
comparten herramientas y system prompt en `brain_core.py` (por eso las dos opciones hacen
lo mismo). Arquitectura y detalles en **`HANDOFF.md`**.

## ⚠️ Privacidad
La **voz** (reconocimiento y síntesis) es **100% local**. El **cerebro** depende de la opción:
- **Local (Ollama):** todo queda en tu PC, **nada sale a internet**. Privacidad total.
- **Claude:** el texto de tus órdenes viaja a Anthropic para responder. Tu API key queda
  sólo en tu PC (`api_key.txt`, ignorado por git).

## 📜 Licencia
MIT — usalo, modificalo y compartilo. Si hacés algo copado, ¡mostralo! 🙌

---
Hecho con ❤️ para que cualquiera pueda tener su propio JARVIS.
