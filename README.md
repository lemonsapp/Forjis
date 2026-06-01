# FORJIS 🔥🦾 — Tu propio JARVIS de Iron Man

Asistente de voz para Windows con **interfaz tipo JARVIS**: le hablás, controla tu PC,
te responde con voz, aprende de vos y tiene una HUD futurista con reactor animado.

> "FORJIS, abrí Brave" · "FORJIS, subí el volumen" · "FORJIS, contame un chiste" · 👏👏

![estado](https://img.shields.io/badge/plataforma-Windows-blue) ![python](https://img.shields.io/badge/python-3.10%2B-green) ![offline](https://img.shields.io/badge/voz-offline-success)

---

## ✨ Qué hace

- 🗣️ **Hablás y te entiende** — reconocimiento de voz local (Whisper), en español.
- 🧠 **Cerebro Claude** — entiende lenguaje libre, charla y **decide acciones solo**.
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
   y te pide tu **API key de Anthropic**.
3. Abrí FORJIS con el ícono **FORJIS** del Escritorio. ¡Listo!

> ¿Se trabó algo? Mirá **`SETUP_PROMPT.md`**: tiene un prompt para pegarle a Claude y que
> te ayude a instalar y configurar lo que falte.

### Requisitos
- Windows 10/11
- Una **API key** de Anthropic → [console.anthropic.com](https://console.anthropic.com) (poné un tope de gasto, con Haiku es centavos)
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
- **Modelo del cerebro:** `CLAUDE_MODEL` (por defecto `claude-haiku-4-5`, rápido y barato).
- **Reconocimiento:** `WHISPER_MODEL` (`small` por defecto; `medium` = más preciso pero más lento).
- **Aplauso:** `CLAP_PEAK` / `CLAP_CREST` si se activa solo o no engancha.

## 🧱 Cómo está hecho
`faster-whisper` (oídos) · `Anthropic SDK` (cerebro, tool use) · `piper-tts` (voz) ·
`opencv` + `mediapipe` (ojos) · `FastAPI` + `pywebview` (HUD/app) · `pyautogui` (acciones).

Arquitectura y detalles en **`HANDOFF.md`**.

## ⚠️ Privacidad
La **voz** (reconocimiento y síntesis) es **100% local**. El **cerebro** usa la API de
Anthropic, así que el texto de tus órdenes viaja a Claude para responder. Tu API key queda
sólo en tu PC (`api_key.txt`, ignorado por git).

## 📜 Licencia
MIT — usalo, modificalo y compartilo. Si hacés algo copado, ¡mostralo! 🙌

---
Hecho con ❤️ para que cualquiera pueda tener su propio JARVIS.
