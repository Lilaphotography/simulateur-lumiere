"""Assemble le guide mini-séances de Noël en un seul fichier HTML autonome.

- génère les ornements SVG (branche de sapin, brin de houx) et les injecte à la place de <!--SVG_SYMBOLS-->
- remplace chaque src="images/xxx.jpg" par l'image encodée en base64

Usage : python3 build.py  ->  guide-mini-noel.html
"""
import base64
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).parent
random.seed(7)

GREENS = ["#2F4A3A", "#3B5B47", "#26402F", "#4F6E57", "#1F3528", "#5C7A62"]


def fir_branch():
    """Branche de sapin horizontale, base à gauche (0,60), pointe vers la droite."""
    out = []

    def needles_along(x0, y0, x1, y1, cx, cy, count, length, spread):
        for i in range(count):
            t = 0.04 + 0.96 * i / count
            # point sur la courbe quadratique
            x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
            y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
            dx = 2 * (1 - t) * (cx - x0) + 2 * t * (x1 - cx)
            dy = 2 * (1 - t) * (cy - y0) + 2 * t * (y1 - cy)
            ang = math.atan2(dy, dx)
            ln = length * (1 - 0.55 * t) * random.uniform(0.85, 1.1)
            for side in (-1, 1):
                a = ang + side * math.radians(spread + random.uniform(-8, 8))
                ex, ey = x + math.cos(a) * ln, y + math.sin(a) * ln
                out.append(
                    f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
                    f'stroke="{random.choice(GREENS)}"/>'
                )

    # tige principale
    out.append('<path d="M0 60 Q150 48 300 56" stroke="#5A4632" stroke-width="2.2" fill="none"/>')
    # rameaux secondaires
    twigs = [(40, 58, 95, 28, 70, 38), (80, 55, 140, 86, 115, 76), (125, 52, 185, 24, 160, 32),
             (170, 52, 228, 82, 205, 72), (215, 53, 262, 32, 245, 38)]
    for x0, y0, x1, y1, cx, cy in twigs:
        out.append(f'<path d="M{x0} {y0} Q{cx} {cy} {x1} {y1}" stroke="#5A4632" stroke-width="1.2" fill="none"/>')
        needles_along(x0, y0, x1, y1, cx, cy, 18, 14, 50)
    needles_along(0, 60, 300, 56, 150, 48, 56, 21, 48)
    return (
        '<symbol id="fir" viewBox="-10 0 330 115">'
        '<g stroke-width="1.3" stroke-linecap="round">' + "".join(out) + "</g></symbol>"
    )


HOLLY_LEAF = (
    "M0 0 C6 -6 10 -12 16 -10 C18 -15 24 -17 28 -13 C32 -18 38 -18 42 -13 "
    "C46 -16 52 -14 54 -9 C58 -9 62 -5 64 0 C62 5 58 9 54 9 C52 14 46 16 42 13 "
    "C38 18 32 18 28 13 C24 17 18 15 16 10 C10 12 6 6 0 0 Z"
)


def holly():
    """Brin de houx : deux feuilles + trois baies rouges (les baies ont leur propre classe pour l'animation)."""
    leaf = (
        f'<path d="{HOLLY_LEAF}" fill="#2F4A3A"/>'
        '<path d="M2 0 L60 0" stroke="#4E6B56" stroke-width="1" fill="none"/>'
    )
    return (
        '<symbol id="holly" viewBox="-70 -40 140 70">'
        f'<g transform="rotate(-160) translate(6 0)">{leaf}</g>'
        f'<g transform="rotate(-20) translate(6 0)">{leaf}</g>'
        '<g class="berries">'
        '<circle cx="-7" cy="-4" r="7.5" fill="#9E1B2A"/>'
        '<circle cx="7" cy="-5" r="7" fill="#B3263A"/>'
        '<circle cx="0" cy="7" r="7.5" fill="#8E1F2A"/>'
        '<circle cx="-9" cy="-7" r="2" fill="#fff" opacity=".55"/>'
        '<circle cx="5" cy="-8" r="1.8" fill="#fff" opacity=".55"/>'
        '<circle cx="-2" cy="4" r="2" fill="#fff" opacity=".5"/>'
        "</g></symbol>"
    )


def main():
    html = (ROOT / "template.html").read_text(encoding="utf-8")
    html = html.replace("<!--SVG_SYMBOLS-->",
                        '<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
                        + fir_branch() + holly() + "</svg>")

    def inline(m):
        path = ROOT / m.group(1)
        if not path.exists():  # ex. images/stella.jpg cité dans un commentaire avant d'être ajouté
            return m.group(0)
        data = path.read_bytes()
        return 'src="data:image/jpeg;base64,' + base64.b64encode(data).decode() + '"'

    html = re.sub(r'src="(images/[^"]+\.jpg)"', inline, html)
    out = ROOT / "guide-mini-noel.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out.name} : {out.stat().st_size / 1024:.0f} Ko")


if __name__ == "__main__":
    main()
