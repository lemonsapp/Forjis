"""Resolución de dispositivos de audio (evita los ~2000 fantasmas de WDM-KS).

Busca el dispositivo por nombre solo en MME / WASAPI, prefiriendo MME.
"""
import sounddevice as sd

PREFERRED_APIS = ("MME", "Windows WASAPI")


def _candidates(kind: str, name_match: str):
    """kind = 'input' o 'output'. Devuelve [(prioridad, idx)]."""
    has = sd.query_hostapis()
    nm = name_match.lower()
    found = []
    for i, d in enumerate(sd.query_devices()):
        api = has[d["hostapi"]]["name"]
        if api not in PREFERRED_APIS:
            continue
        if d[f"max_{kind}_channels"] <= 0:
            continue
        if nm and nm not in d["name"].lower():
            continue
        prio = PREFERRED_APIS.index(api)  # 0 = MME primero
        found.append((prio, i, d["name"]))
    found.sort()
    return found


def resolve(kind: str, name_match: str):
    """Devuelve (idx, nombre) del primer match, o (None, None).
    Si name_match está vacío -> (None, None) = usar el dispositivo por defecto del sistema."""
    if not name_match:
        return None, None
    c = _candidates(kind, name_match)
    if c:
        return c[0][1], c[0][2]
    return None, None
