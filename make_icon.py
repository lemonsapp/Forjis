"""Genera el ícono de FORJIS: una F blanca sobre fondo naranja de forja.

Crea web/favicon.png (256), web/favicon.ico (multi-tamaño) y web/favicon.svg.
Correr una sola vez (o cuando se quiera retocar el ícono):
    .venv\\Scripts\\python.exe make_icon.py
"""
import os

from PIL import Image, ImageDraw

WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

TOP = (255, 138, 43)    # naranja claro (metal al rojo vivo)
BOT = (230, 74, 0)      # naranja profundo (brasa)
WHITE = (255, 255, 255, 255)


def _f_path(s):
    """Geometría de la 'F' escalada a un lienzo de lado s (en 0..1 * s)."""
    u = s / 256.0
    stem = (96 * u, 58 * u, 128 * u, 198 * u)
    top = (96 * u, 58 * u, 182 * u, 90 * u)
    mid = (96 * u, 112 * u, 164 * u, 142 * u)
    r = max(2, int(8 * u))
    return stem, top, mid, r


def render(size: int) -> Image.Image:
    # Fondo: gradiente vertical naranja, recortado a cuadrado redondeado.
    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = Image.new("RGBA", (size, size))
    for y in range(size):
        t = y / max(1, size - 1)
        r = int(TOP[0] + (BOT[0] - TOP[0]) * t)
        g = int(TOP[1] + (BOT[1] - TOP[1]) * t)
        b = int(TOP[2] + (BOT[2] - TOP[2]) * t)
        for x in range(size):
            grad.putpixel((x, y), (r, g, b, 255))

    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    rad = int(size * 0.22)
    md.rounded_rectangle([0, 0, size - 1, size - 1], radius=rad, fill=255)
    base.paste(grad, (0, 0), mask)

    # La F blanca encima.
    d = ImageDraw.Draw(base)
    stem, top, mid, r = _f_path(size)
    for box in (stem, top, mid):
        d.rounded_rectangle(box, radius=r, fill=WHITE)
    return base


def main():
    os.makedirs(WEB, exist_ok=True)
    big = render(256)
    big.save(os.path.join(WEB, "favicon.png"))
    sizes = [16, 24, 32, 48, 64, 128, 256]
    imgs = [render(s) for s in sizes]
    imgs[0].save(os.path.join(WEB, "favicon.ico"), sizes=[(s, s) for s in sizes],
                 append_images=imgs[1:])

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">\n'
        '  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">\n'
        f'    <stop offset="0" stop-color="rgb{TOP}"/>\n'
        f'    <stop offset="1" stop-color="rgb{BOT}"/>\n'
        '  </linearGradient></defs>\n'
        '  <rect width="256" height="256" rx="56" fill="url(#g)"/>\n'
        '  <g fill="#fff">\n'
        '    <rect x="96" y="58" width="32" height="140" rx="8"/>\n'
        '    <rect x="96" y="58" width="86" height="32" rx="8"/>\n'
        '    <rect x="96" y="112" width="68" height="30" rx="8"/>\n'
        '  </g>\n'
        '</svg>\n'
    )
    with open(os.path.join(WEB, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    print("Ícono generado en", WEB)
    print(" - favicon.png, favicon.ico, favicon.svg")


if __name__ == "__main__":
    main()
