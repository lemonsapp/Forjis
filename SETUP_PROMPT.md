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
  dependencias de requirements.txt, baja los modelos (download_models.py), me pide la
  API key de Anthropic (se guarda en api_key.txt) y crea un acceso directo "FORJIS".
- Se abre como app de escritorio con el ícono FORJIS o ejecutando: .venv\Scripts\pythonw.exe app.py
- El cerebro usa la API de Anthropic (modelo claude-haiku-4-5). La clave va en api_key.txt.
- Usa el micrófono y los parlantes por DEFECTO de Windows. Se puede forzar otro dispositivo
  en config.py (INPUT_DEVICE_MATCH / OUTPUT_DEVICE_MATCH con parte del nombre del aparato).
- Se activa diciendo "FORJIS ..." o con doble aplauso.

Por favor ayudame a:
1. Confirmar que Python está instalado (versión 3.10+). Si no, instalarlo.
2. Ejecutar install.bat y resolver cualquier error que aparezca (pegame instrucciones claras).
3. Conseguir y cargar mi API key de Anthropic (decime cómo sacarla en console.anthropic.com
   y exactamente dónde ponerla).
4. Probar que el micrófono anda y elegir el correcto si me escucha mal.
5. Hacer la primera prueba: abrir FORJIS y que me responda a "FORJIS, qué hora es".

Si ves errores de audio, de modelos que no bajan, o de la API key, diagnosticá y arreglá.
Cuando todo funcione, mostrame los comandos de voz que puedo probar.
```

---

> 💡 Tip: si usás **Claude Code**, primero hacé `cd` a la carpeta de FORJIS y después pegá el prompt;
> así Claude puede ver los archivos y correr los comandos por vos.
