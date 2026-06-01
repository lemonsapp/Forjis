"""Estado persistente de FORJIS: personalidad y voz que recuerda entre sesiones."""
import json
import os

import config

_DEFAULTS = {
    "personality": config.DEFAULT_PERSONALITY,
    "voice": "hombre",     # "hombre" | "mujer"
    "speed": "normal",     # "lento" | "normal" | "rapido"
}


def _read():
    if os.path.exists(config.STATE_FILE):
        try:
            with open(config.STATE_FILE, encoding="utf-8") as f:
                data = json.load(f)
            return {**_DEFAULTS, **data}
        except Exception:
            pass
    return dict(_DEFAULTS)


def _write(data):
    try:
        with open(config.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[FORJIS] no pude guardar estado: {e}")


def get(key, default=None):
    return _read().get(key, default if default is not None else _DEFAULTS.get(key))


def set(key, value):
    data = _read()
    data[key] = value
    _write(data)
    return value


# ---- Memoria de largo plazo (lo que FORJIS aprende del usuario) ----
def get_memories():
    return _read().get("memories", [])


def add_memory(text):
    text = (text or "").strip()
    if not text:
        return None
    data = _read()
    mems = data.get("memories", [])
    if text not in mems:
        mems.append(text)
        data["memories"] = mems[-60:]   # tope para no crecer infinito
        _write(data)
    return text


def clear_memories():
    data = _read()
    data["memories"] = []
    _write(data)

