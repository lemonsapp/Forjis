# 🤖 Prompt para Claude — Ayudante de instalación de FORJIS

¿Algo no te funcionó? Abrí **Claude Code** (o claude.ai) en la carpeta de FORJIS y
**copiá y pegá este prompt**. Claude te va a guiar paso a paso y arreglar lo que falle.

---

```
Hola Claude. Descargué FORJIS, un asistente de voz tipo JARVIS para Windows hecho en Python,
y quiero que me ayudes a instalarlo y dejarlo funcionando. Soy nuevo en esto, así que explicame
simple y andá paso a paso, pidiéndome los errores exactos cuando algo falle.

Contexto del proyecto:
- Es una carpeta con archivos .py, un install.bat, app.py y una carpeta web/.
- install.bat hace todo: instala Python si falta, crea un entorno .venv, instala las
  dependencias de requirements.txt, baja los modelos (download_models.py), me PREGUNTA qué
  cerebro quiero y crea un acceso directo "FORJIS".
- El cerebro es intercambiable (lo elijo al instalar y lo cambio con el botón 🧠 de la HUD):
    * "claude": nube, Anthropic API (modelo claude-haiku-4-5). La clave va en api_key.txt.
    * "local": Ollama offline y gratis (modelo qwen2.5:7b). Necesita tener Ollama instalado
      y corriendo, y el modelo descargado (ollama pull qwen2.5:7b). setup_local.bat hace eso.
  La opción elegida se guarda en forjis_state.json (clave "brain"). Las dos controlan la PC igual.
- Se abre como app de escritorio con el ícono FORJIS o ejecutando: .venv\Scripts\pythonw.exe app.py
- Usa el micrófono y los parlantes por DEFECTO de Windows. Se puede forzar otro dispositivo
  en config.py (INPUT_DEVICE_MATCH / OUTPUT_DEVICE_MATCH con parte del nombre del aparato).
- Se activa diciendo "FORJIS ..." o con doble aplauso.

Por favor ayudame a:
1. Confirmar que Python está instalado (versión 3.10+). Si no, instalarlo.
2. Ejecutar install.bat y resolver cualquier error que aparezca (pegame instrucciones claras).
3. Elegir el cerebro:
   - Si quiero CLAUDE: cómo sacar la API key en console.anthropic.com y dónde ponerla (api_key.txt).
   - Si quiero LOCAL (gratis): instalar Ollama (winget install -e --id Ollama.Ollama),
     correr "ollama pull qwen2.5:7b" y dejar brain=local (o correr setup_local.bat).
4. Probar que el micrófono anda y elegir el correcto si me escucha mal.
5. Hacer la primera prueba: abrir FORJIS y que me responda a "FORJIS, qué hora es".

Si ves errores de audio, de modelos que no bajan, de la API key o de Ollama, diagnosticá y arreglá.
Cuando todo funcione, mostrame los comandos de voz que puedo probar.
```

---

> 💡 Tip: si usás **Claude Code**, primero hacé `cd` a la carpeta de FORJIS y después pegá el prompt;
> así Claude puede ver los archivos y correr los comandos por vos.
