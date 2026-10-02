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


def holly_leaf_path(L=66, W=19):
    """Feuille de houx à pointes franches : bords concaves entre des épines pointues."""
    tips = [0.16, 0.37, 0.58, 0.79]
    prof = lambda t: W * math.sin(math.pi * min(max(t, 0), 1)) ** 0.75
    top, bot = [], []
    prev = 0.0
    for t in tips:
        mid = (prev + t) / 2
        top.append(f"Q{mid * L:.1f} {-prof(mid) * 0.45:.1f} {t * L:.1f} {-prof(t) * 1.12:.1f}")
        bot.append((mid, t))
        prev = t
    mid = (prev + 1) / 2
    top.append(f"Q{mid * L:.1f} {-prof(mid) * 0.5:.1f} {L} 0")
    d = "M0 0 " + " ".join(top)
    # bord inférieur : symétrique, parcouru à l'envers
    pts = [0.0] + tips + [1.0]
    for i in range(len(pts) - 1, 0, -1):
        a, b = pts[i - 1], pts[i]
        m = (a + b) / 2
        end_y = prof(a) * 1.12 if a > 0 else 0
        d += f" Q{m * L:.1f} {prof(m) * (0.5 if i == len(pts) - 1 else 0.45):.1f} {a * L:.1f} {end_y:.1f}"
    return d + " Z"


GRADIENTS = (
    '<defs>'
    '<linearGradient id="g-leaf" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#4C7A57"/><stop offset=".5" stop-color="#2C5238"/><stop offset="1" stop-color="#173022"/></linearGradient>'
    '<linearGradient id="g-leaf2" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#3A6545"/><stop offset="1" stop-color="#132719"/></linearGradient>'
    '<radialGradient id="g-berry" cx=".36" cy=".32" r=".75">'
    '<stop offset="0" stop-color="#FF6B7C"/><stop offset=".35" stop-color="#D7192F"/>'
    '<stop offset=".8" stop-color="#8E0E1F"/><stop offset="1" stop-color="#5C0713"/></radialGradient>'
    '<radialGradient id="g-shine" cx=".5" cy=".5" r=".5">'
    '<stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
    '<linearGradient id="g-gold" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#8A6A2A"/><stop offset=".3" stop-color="#F6E3A8"/><stop offset=".5" stop-color="#B8903A"/>'
    '<stop offset=".72" stop-color="#FFF1C4"/><stop offset="1" stop-color="#94712D"/></linearGradient>'
    + "".join(
        f'<radialGradient id="g-b-{n}" cx=".35" cy=".3" r=".8">'
        f'<stop offset="0" stop-color="{a}"/><stop offset=".45" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></radialGradient>'
        for n, a, b, c in [("red", "#F0697A", "#B3182C", "#4E0711"),
                           ("gold", "#FFF3CC", "#C9A04A", "#6E5020"),
                           ("green", "#7FA88A", "#2F5A3E", "#10251A")]
    )
    + '</defs>'
)


def holly():
    """Brin de houx réaliste : trois feuilles brillantes + grappe de baies (viewBox 0 0 140 70)."""
    leaf_d = holly_leaf_path()
    small_d = holly_leaf_path(38, 12)

    def leaf(d, angle, grad, L):
        return (
            f'<g transform="rotate({angle})">'
            f'<path d="{d}" fill="url(#{grad})" stroke="#10241A" stroke-width=".6" stroke-linejoin="miter"/>'
            f'<path d="M3 -1 Q{L * .5:.0f} -5 {L - 6} -1" stroke="#fff" stroke-opacity=".22" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
            f'<path d="M2 0 Q{L * .5:.0f} -1.5 {L - 2} 0" stroke="#86A57F" stroke-width="1.1" fill="none"/>'
            '</g>'
        )

    berries = ""
    for cx, cy, r in [(-8, -2, 8.2), (8, -4, 7.6), (0, 9, 8.4)]:
        berries += (
            f'<ellipse cx="{cx + 1.5}" cy="{cy + 3}" rx="{r}" ry="{r * .8:.1f}" fill="#000" opacity=".18"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#g-berry)"/>'
            f'<ellipse cx="{cx - r * .35:.1f}" cy="{cy - r * .4:.1f}" rx="{r * .38:.1f}" ry="{r * .26:.1f}" fill="url(#g-shine)"/>'
            f'<circle cx="{cx + r * .45:.1f}" cy="{cy + r * .5:.1f}" r="1.1" fill="#3A0610" opacity=".8"/>'
        )
    return (
        '<symbol id="holly" viewBox="0 0 140 70"><g transform="translate(70 40)">'
        + leaf(small_d, -82, "g-leaf2", 38)
        + leaf(leaf_d, -165, "g-leaf", 66)
        + leaf(leaf_d, -15, "g-leaf", 66)
        + f'<g class="berries">{berries}</g>'
        + "</g></symbol>"
    )


def baubles():
    """Boules de Noël (viewBox 0 0 60 70) : rouge, or, vert."""
    out = ""
    for n in ("red", "gold", "green"):
        out += (
            f'<symbol id="bauble-{n}" viewBox="0 0 60 70">'
            '<path d="M26 2 Q30 -3 34 2" stroke="url(#g-gold)" stroke-width="2" fill="none"/>'
            '<rect x="23" y="2" width="14" height="9" rx="2" fill="url(#g-gold)"/>'
            f'<circle cx="30" cy="38" r="26" fill="url(#g-b-{n})"/>'
            '<path d="M6 34 Q30 44 54 34" stroke="url(#g-gold)" stroke-width="1.4" fill="none" opacity=".8"/>'
            '<path d="M6.5 42 Q30 52 53.5 42" stroke="url(#g-gold)" stroke-width="1" fill="none" opacity=".6"/>'
            '<ellipse cx="20" cy="26" rx="7" ry="4.5" fill="url(#g-shine)" transform="rotate(-30 20 26)"/>'
            '</symbol>'
        )
    return out


def bow():
    """Noeud de ruban satin doré (viewBox 0 0 160 110), centré en (80,40)."""
    g = "url(#g-gold)"
    return (
        '<symbol id="bow" viewBox="0 0 160 110">'
        # pans du ruban
        f'<path d="M74 44 L52 104 L62 98 L68 108 L82 48 Z" fill="{g}" stroke="#6E501C" stroke-width=".6"/>'
        f'<path d="M86 44 L108 104 L98 98 L92 108 L78 48 Z" fill="{g}" stroke="#6E501C" stroke-width=".6"/>'
        # boucles
        f'<path d="M78 40 C60 8 18 4 12 26 C6 46 46 54 78 44 Z" fill="{g}" stroke="#6E501C" stroke-width=".7"/>'
        f'<path d="M82 40 C100 8 142 4 148 26 C154 46 114 54 82 44 Z" fill="{g}" stroke="#6E501C" stroke-width=".7"/>'
        # ombres internes des boucles
        '<path d="M74 40 C58 22 34 18 26 28 C40 26 58 32 74 42 Z" fill="#6E501C" opacity=".35"/>'
        '<path d="M86 40 C102 22 126 18 134 28 C120 26 102 32 86 42 Z" fill="#6E501C" opacity=".35"/>'
        # reflets satin
        '<path d="M20 22 C34 12 54 16 66 28" stroke="#fff" stroke-opacity=".55" stroke-width="2" fill="none" stroke-linecap="round"/>'
        '<path d="M140 22 C126 12 106 16 94 28" stroke="#fff" stroke-opacity=".55" stroke-width="2" fill="none" stroke-linecap="round"/>'
        # noeud central
        f'<rect x="70" y="32" width="20" height="18" rx="5" fill="{g}" stroke="#6E501C" stroke-width=".7"/>'
        '<path d="M73 36 Q80 33 87 36" stroke="#fff" stroke-opacity=".6" stroke-width="1.4" fill="none"/>'
        '</symbol>'
    )


def main():
    html = (ROOT / "template.html").read_text(encoding="utf-8")
    html = html.replace("<!--SVG_SYMBOLS-->",
                        '<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
                        + GRADIENTS + fir_branch() + holly() + baubles() + bow() + "</svg>")

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


def apercus():
    """Aperçus à ouvrir tels quels : le guide dans un cadre de téléphone, et sur un écran d'ordinateur."""
    import html as h
    guide = h.escape((ROOT / "guide-mini-noel.html").read_text(encoding="utf-8"), quote=True)
    mobile = (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Aperçu mobile</title>'
        '<style>html,body{margin:0;height:100%}body{background:#2A2420;display:flex;align-items:center;justify-content:center;font-family:system-ui,sans-serif}'
        '.phone{width:390px;height:844px;max-height:calc(100vh - 40px);border-radius:48px;background:#111;padding:14px;box-shadow:0 30px 80px rgba(0,0,0,.5)}'
        '.phone iframe{width:100%;height:100%;border:0;border-radius:36px;background:#fff;display:block}'
        '@media(max-width:440px){body{display:block}.phone{width:100%;height:100vh;max-height:none;border-radius:0;padding:0}.phone iframe{border-radius:0}}'
        '</style></head><body><div class="phone"><iframe title="Guide mini-séances de Noël, version mobile" srcdoc="'
        + guide + '"></iframe></div></body></html>'
    )
    desktop = (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Aperçu ordinateur</title>'
        '<style>html,body{margin:0}body{background:#2A2420}.wrap{position:relative;width:100%;overflow:hidden}'
        '.screen{position:absolute;top:0;left:0;width:1440px;transform-origin:0 0;background:#fff}iframe{border:0;width:1440px;display:block}</style></head><body>'
        '<div class="wrap" id="wrap"><div class="screen" id="screen"><iframe id="f" title="Guide mini-séances de Noël, version ordinateur" srcdoc="'
        + guide + '"></iframe></div></div><script>'
        "var wr=document.getElementById('wrap'),sc=document.getElementById('screen'),f=document.getElementById('f');"
        "function fit(){var w=wr.clientWidth||innerWidth,h=Math.max(innerHeight,560),k=Math.min(1,w/1440);"
        "wr.style.height=h+'px';sc.style.transform='scale('+k+')';sc.style.left=Math.max(0,(w-1440*k)/2)+'px';f.style.height=Math.round(h/k)+'px'}"
        "addEventListener('resize',fit);fit();</script></body></html>"
    )
    (ROOT / "apercu-mobile.html").write_text(mobile, encoding="utf-8")
    (ROOT / "apercu-ordinateur.html").write_text(desktop, encoding="utf-8")
    print("aperçus : apercu-mobile.html, apercu-ordinateur.html")


if __name__ == "__main__":
    apercus()
