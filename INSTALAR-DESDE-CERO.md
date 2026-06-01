# 🚀 Instalar FORJIS desde CERO (para principiantes)

> Esta guía es para alguien que **nunca programó** ni abrió una terminal en su vida.
> Si seguís los pasos en orden, en ~15 minutos tenés tu propio JARVIS andando.
> También sirve de **guion para un video tutorial**.

**¿Qué es FORJIS?** Un asistente de voz para Windows estilo JARVIS de Iron Man:
le hablás, te entiende, controla tu PC y te responde con voz.

---

## ✅ Lo único que necesitás antes de empezar

- Una PC con **Windows 10 u 11**.
- **Internet** (para descargar todo la primera vez).
- **Micrófono y parlantes/auriculares**.
- Unos **15 minutos** y ganas de aprender. Nada más. 💪

No hace falta saber programar. Vas a copiar y pegar comandos, nada más.

---

## 🧠 Antes que nada: elegí el "cerebro" de FORJIS

FORJIS puede pensar de **dos formas** (lo elegís cuando corras el instalador, y lo podés
cambiar después con un botón 🧠 en la pantalla):

| | **Claude** (nube) | **Local** (gratis) |
|---|---|---|
| Inteligencia | 🥇 La más alta | 👍 Muy buena |
| Costo | Centavos por uso | **$0, gratis** |
| Internet | Necesita | **No necesita (offline)** |
| Qué hace falta | Una **API key** (Paso 4) | Que el instalador baje **Ollama** + un modelo (~4.7 GB) |
| Mejor si… | Querés lo más inteligente | Querés que sea gratis, privado y sin internet |

👉 Si elegís **Local**, podés **saltear el Paso 4** (la API key). El instalador se encarga
de todo lo demás. Si elegís **Claude**, seguí el Paso 4 para sacar tu clave.

---

## 🟦 PASO 1 — Abrir la terminal (CMD)

La "terminal" es esa pantalla negra donde se escriben comandos. Se llama **CMD**.

1. Apretá la tecla **Windows** del teclado (la del logo).
2. Escribí: **cmd**
3. Vas a ver "Símbolo del sistema". **Hacé clic derecho → "Ejecutar como administrador"**.
   (Esto evita problemas de permisos al instalar Python.)
4. Si te pregunta "¿Querés permitir que esta app haga cambios?", apretá **Sí**.

✅ Ya tenés la pantalla negra abierta. ¡No le tengas miedo, no se rompe nada!

---

## 🐍 PASO 2 — Instalar Python (el motor que hace andar todo)

Python es el lenguaje en el que está hecho FORJIS. Lo instalamos con **un solo comando**.

Copiá esta línea, pegala en el CMD (clic derecho = pegar) y apretá **Enter**:

```cmd
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
```

- Va a descargar e instalar Python solo. Esperá a que termine (vuelve a aparecer el cursor).
- Si te dice que `winget` no existe (Windows muy viejo), andá al **Plan B** del final.

### ⚠️ MUY IMPORTANTE: cerrar y reabrir el CMD
Después de instalar Python, **cerrá esa ventana negra y abrí una nueva** (Paso 1 de nuevo).
Si no, la PC todavía no "ve" a Python.

### Comprobar que quedó instalado
En la ventana **nueva**, escribí y Enter:

```cmd
python --version
```

✅ Si te muestra algo como `Python 3.12.x` → ¡perfecto, seguí!
❌ Si dice "no se reconoce..." → cerrá y reabrí el CMD una vez más. Si sigue, mirá el Plan B.

---

## 📥 PASO 3 — Descargar FORJIS

Tenés dos formas. La **A es la más fácil** (recomendada para el video).

### Opción A — Descargar el ZIP (sin saber nada, súper fácil)
1. Entrá a: **https://github.com/lemonsapp/Forjis**
2. Apretá el botón verde **`<> Code`** → **Download ZIP**.
3. Se baja un archivo `Forjis-main.zip` (mirá en tu carpeta **Descargas**).
4. **Clic derecho → Extraer todo** (¡importante extraerlo, no abrirlo desde adentro del ZIP!).
5. Te queda una carpeta `Forjis-main`. Movela al **Escritorio** para encontrarla fácil.

### Opción B — Clonarlo desde CMD (más "pro", opcional)
Si querés hacerlo todo por terminal, primero instalá Git:
```cmd
winget install -e --id Git.Git
```
Cerrá y reabrí el CMD, después:
```cmd
cd %USERPROFILE%\Desktop
git clone https://github.com/lemonsapp/Forjis.git
```
Te queda la carpeta `Forjis` en el Escritorio.

---

## 🔑 PASO 4 — Conseguir tu "código" de Claude (API key)

> 🆓 **¿Elegiste el cerebro LOCAL (gratis)?** Saltá este paso entero y andá al **Paso 5**.
> El instalador baja Ollama y el modelo solo; no necesitás ninguna clave.

Si elegís el cerebro **Claude**, usa la inteligencia de Claude (la IA de Anthropic).
Para eso necesitás una **API key**: es como una contraseña personal que conecta TU FORJIS con la IA.

> 💡 Cada persona usa **su propia** key. La mía no se comparte (así nadie gasta el saldo de otro).

1. Entrá a: **https://console.anthropic.com**
2. Creá tu cuenta (con tu mail, es gratis registrarse).
3. En el menú, andá a **API Keys** → **Create Key**. Ponele un nombre (ej: "FORJIS").
4. Te muestra una clave larga que empieza con `sk-ant-...`.
   **COPIALA Y GUARDALA YA** (no se vuelve a mostrar). Pegala en un bloc de notas por ahora.
5. **Ponele un tope de gasto** (recomendado): en **Limits / Billing**, cargá un poco de crédito
   y poné un límite mensual chico. Con el modelo Haiku, usarlo cuesta **centavos**.

> ⚠️ La API key es de pago (consumo propio de cada uno). Anthropic suele dar un créditito
> inicial para probar. Tratala como una contraseña: **no la compartas ni la subas a ningún lado.**

---

## ⚙️ PASO 5 — Instalar FORJIS (el instalador hace casi todo solo)

Ahora lo más fácil de todo:

1. Entrá a la carpeta de FORJIS (la que descargaste en el Paso 3).
2. Buscá el archivo **`install.bat`** y hacele **doble clic**.

El instalador hace **todo automáticamente**, en orden:
- ✅ Verifica Python (y lo instala si falta).
- ✅ Crea un "entorno aislado" para no ensuciar tu PC.
- ✅ Instala todas las piezas (reconocimiento de voz, voz, visión, etc.).
- ✅ Descarga los modelos de voz.
- 🧠 **Te pregunta qué cerebro querés:**
  - Escribís **`1`** (Claude) → te pide tu **API key** (pegá la del Paso 4 y Enter).
  - Escribís **`2`** (Local, gratis) → instala **Ollama** y baja el modelo `qwen2.5:7b`
    (~4.7 GB, una sola vez). Esto tarda un rato según tu internet.
- ✅ Crea el ícono **FORJIS** en tu Escritorio.

Cuando termine te pregunta si lo querés abrir. Decí que **sí** (`s`).

> 🔁 **¿Te arrepentiste o querés probar el otro cerebro?** Una vez abierto FORJIS, tocá el
> botón **🧠** abajo en la pantalla para cambiar Claude ↔ Local cuando quieras. Y si elegiste
> Claude pero después querés el modo gratis, doble clic en **`setup_local.bat`**.

> ⏳ La **primera vez** que FORJIS escucha, descarga el modelo que entiende tu voz (Whisper).
> Por eso el primer arranque tarda un poquito más y necesita internet esa vez. Después, vuela.

---

## 🎉 PASO 6 — ¡Usar FORJIS!

Abrilo con el ícono **FORJIS** del Escritorio. Probá decir (o aplaudí dos veces 👏👏 y hablá):

- *"FORJIS, ¿qué hora es?"*
- *"FORJIS, abrí Brave"*
- *"FORJIS, subí el volumen"*
- *"FORJIS, buscá gatos en YouTube"*
- *"FORJIS, contame un chiste"*

¿No te escucha el micrófono? Podés **escribir** la orden en la cajita de la pantalla mientras tanto.

---

# 🧑‍💻 (Avanzado / educativo) Instalación 100% manual por CMD

Si querés entender qué hace el `install.bat` por dentro — o si el doble clic falla — podés
hacer lo mismo a mano. Abrí el CMD y andá a la carpeta de FORJIS:

```cmd
cd %USERPROFILE%\Desktop\Forjis-main
```
*(cambiá `Forjis-main` por el nombre real de tu carpeta. Si usaste git, es `Forjis`.)*

Después, uno por uno:

```cmd
:: 1) Crear el entorno aislado
python -m venv .venv

:: 2) Activarlo (vas a ver "(.venv)" al principio de la línea)
.venv\Scripts\activate

:: 3) Instalar todas las dependencias
pip install -r requirements.txt

:: 4) Descargar los modelos de voz
python download_models.py

:: 5a) CEREBRO CLAUDE: crear el archivo con tu API key (reemplazá sk-ant-TU-CLAVE)
echo sk-ant-TU-CLAVE> api_key.txt
python -c "import state; state.set('brain','claude')"

:: 5b) ...o CEREBRO LOCAL (gratis): instalar Ollama + bajar el modelo
::     winget install -e --id Ollama.Ollama
::     ollama pull qwen2.5:7b
::     python -c "import state; state.set('brain','local')"
::     (o simplemente: doble clic en setup_local.bat)

:: 6) Abrir FORJIS
python app.py
```

Eso es exactamente lo que automatiza el instalador. 🙂

---

# 🆘 Si algo no funciona (problemas comunes)

| Síntoma | Solución |
|---|---|
| `python no se reconoce` | Cerrá y reabrí el CMD. Si sigue, reinstalá Python tildando **"Add to PATH"** (Plan B). |
| `winget no se reconoce` | Tu Windows no lo tiene. Usá el **Plan B** (instalar Python a mano). |
| El instalador se cierra solo o tira error | Hacé clic derecho en `install.bat` → **Ejecutar como administrador**. |
| Abrí el ZIP pero no anda | Tenés que **Extraer todo** primero, no correrlo desde adentro del ZIP. |
| FORJIS no me escucha | Revisá que tu micro sea el predeterminado en Windows. Mientras tanto, escribí la orden. |
| "El cerebro está OFF" (modo Claude) | Falta o está mal la API key. Abrí `api_key.txt` y pegá tu clave `sk-ant-...` (sin espacios). |
| "El cerebro está OFF" (modo Local) | Ollama no está corriendo o falta el modelo. Doble clic en `setup_local.bat`, o en CMD: `ollama pull qwen2.5:7b`. Fijate el ícono de Ollama en la bandeja. |
| El modo local va muy lento | Es normal sin GPU. Probá un modelo más liviano (`ollama pull qwen2.5:3b` y cambiá `LLM_MODEL` en `config.py`), o usá el cerebro Claude. |

### 🅱️ Plan B — Instalar Python sin winget (a mano)
1. Entrá a **https://www.python.org/downloads/** y descargá Python 3.12.
2. Abrí el instalador y, **antes de "Install Now"**, tildá la casilla
   **✅ "Add python.exe to PATH"** (abajo de todo). ¡Es clave!
3. Instalá, reiniciá el CMD y volvé al Paso 2 para comprobar con `python --version`.

### 🤖 Truco: que Claude te ayude
En la carpeta hay un archivo **`SETUP_PROMPT.md`**. Copiá su contenido, pegáselo a Claude
(o a FORJIS) y contale qué error te apareció: te guía paso a paso para resolverlo.

---

Hecho con ❤️ para que **cualquiera** pueda tener su propio JARVIS. Si lo lográs, ¡compartilo! 🔥🦾
