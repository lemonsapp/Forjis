"""Los 'ojos' de FORJIS: control del mouse con la mano vía webcam.

Usa la API moderna de MediaPipe (Tasks / HandLandmarker).

Gestos:
  - Mover cursor:    índice estirado -> el cursor sigue la punta del índice.
  - Click izquierdo: juntá pulgar + índice (pinza).
  - Click derecho:   juntá pulgar + dedo mayor.
  - Salir:           tecla 'q' en la ventana, o Ctrl+C.

Se ejecuta aparte del asistente de voz:
    .venv\\Scripts\\python.exe eyes.py
"""
import math
import os

import cv2
import numpy as np
import pyautogui
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

import config

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# Conexiones estándar de los 21 puntos de la mano (para dibujar el esqueleto).
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _make_landmarker():
    if not os.path.exists(config.HAND_MODEL):
        raise FileNotFoundError(
            f"Falta el modelo de manos en {config.HAND_MODEL}. "
            f"Corré: python download_models.py"
        )
    opts = mp_vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=config.HAND_MODEL),
        running_mode=mp_vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    return mp_vision.HandLandmarker.create_from_options(opts)


def run():
    screen_w, screen_h = pyautogui.size()
    landmarker = _make_landmarker()

    cap = cv2.VideoCapture(config.CAM_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_H)
    if not cap.isOpened():
        print("[OJOS] No pude abrir la cámara. Probá cambiar CAM_INDEX en config.py")
        return

    ploc_x, ploc_y = 0.0, 0.0
    left_down = right_down = False
    margin = config.FRAME_MARGIN
    smooth = config.CURSOR_SMOOTHING
    ts = 0

    print("[OJOS] FORJIS viendo. Índice = mover. Pinza pulgar-índice = click. 'q' para salir.")

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ts += 33  # ~30 fps; el timestamp debe ser creciente
        result = landmarker.detect_for_video(mp_img, ts)

        cv2.rectangle(frame, (margin, margin), (w - margin, h - margin),
                      (0, 200, 255), 2)

        if result.hand_landmarks:
            hand = result.hand_landmarks[0]
            lm = [(int(p.x * w), int(p.y * h)) for p in hand]

            for a, b in HAND_CONNECTIONS:
                cv2.line(frame, lm[a], lm[b], (0, 180, 0), 2)
            for p in lm:
                cv2.circle(frame, p, 4, (0, 255, 0), cv2.FILLED)

            thumb_tip, index_tip, index_pip, middle_tip = lm[4], lm[8], lm[6], lm[12]
            index_up = index_tip[1] < index_pip[1]

            if index_up:
                sx = np.interp(index_tip[0], (margin, w - margin), (0, screen_w))
                sy = np.interp(index_tip[1], (margin, h - margin), (0, screen_h))
                cx = ploc_x + (sx - ploc_x) / smooth
                cy = ploc_y + (sy - ploc_y) / smooth
                pyautogui.moveTo(cx, cy)
                ploc_x, ploc_y = cx, cy
                cv2.circle(frame, index_tip, 10, (0, 255, 0), cv2.FILLED)

            # Click izquierdo: pinza pulgar-índice
            if _dist(thumb_tip, index_tip) < config.PINCH_CLICK_DIST:
                cv2.circle(frame, index_tip, 14, (0, 0, 255), cv2.FILLED)
                if not left_down:
                    pyautogui.click()
                    left_down = True
            else:
                left_down = False

            # Click derecho: pinza pulgar-mayor
            if _dist(thumb_tip, middle_tip) < config.PINCH_RIGHT_DIST:
                cv2.circle(frame, middle_tip, 14, (255, 0, 0), cv2.FILLED)
                if not right_down:
                    pyautogui.click(button="right")
                    right_down = True
            else:
                right_down = False

        cv2.putText(frame, "FORJIS - ojos  (q = salir)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow("FORJIS - ojos", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    landmarker.close()
    cap.release()
    cv2.destroyAllWindows()
    print("[OJOS] Cámara apagada.")


if __name__ == "__main__":
    run()
