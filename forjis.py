"""FORJIS - Asistente personal por voz, 100% offline.

Bucle principal:
  1. Escucha el micrófono y transcribe cada frase (Whisper).
  2. Si detecta la palabra clave 'FORJIS', toma el resto como comando.
  3. El cerebro interpreta el comando y las manos lo ejecutan.
  4. FORJIS responde hablando (Piper).
"""
import time

import config
import voice
from ears import Ears, split_wake_word
import brain


def main():
    print("=" * 50)
    print(f"   {config.WAKE_NAME} - iniciando...")
    print("=" * 50)

    ears = Ears()

    # Estado del cerebro (Claude)
    if brain.available():
        print(f"[FORJIS] Cerebro: Claude ON ({config.CLAUDE_MODEL})")
    else:
        print("[FORJIS] Cerebro: OFF — falta la API key (api_key.txt o ANTHROPIC_API_KEY)")

    print("[FORJIS] Calibrando ruido de fondo... (quedate en silencio 1 segundo)")
    ears.calibrate()
    voice.say(f"{config.WAKE_NAME} en línea. Decí mi nombre para activarme.")

    print(f"\n[FORJIS] Escuchando... (decí '{config.WAKE_NAME} ...' para darme una orden)")
    print("[FORJIS] Ctrl+C para salir.\n")

    while True:
        try:
            text = ears.listen_utterance()
            if not text:
                continue

            print(f"  (oí): {text}")
            has_wake, command = split_wake_word(text)
            if not has_wake:
                continue

            # Caso 1: dijo solo "FORJIS" -> pedir la orden
            if not command:
                voice.beep()
                voice.say("¿Sí?")
                command_text = ears.listen_utterance()
                if not command_text:
                    voice.say("No te escuché.")
                    continue
                print(f"  (orden): {command_text}")
                command = command_text

            # Caso 2: dijo "FORJIS abrí brave" -> command ya tiene la orden
            response = brain.handle(command)

            if response == "__SLEEP__":
                voice.say("Hasta luego.")
                break

            voice.say(response)

        except KeyboardInterrupt:
            print("\n[FORJIS] Apagando.")
            break
        except Exception as e:
            print(f"[FORJIS] Error: {e}")
            time.sleep(0.5)


if __name__ == "__main__":
    main()
