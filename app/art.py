"""Original SVG artwork, drawn in code (no stock images, no network).

Two kinds:
- ICONS: one line style (24 x 24, 1.8 stroke, round caps), used as CSS masks so they take the text colour in both
  modes (ui.icon / ui.icon_css).
- Illustrations: multi-colour SVGs returned as <img> data URIs, drawn with a light or dark palette. They hold no
  text (an SVG image cannot use the page fonts); labels sit in the HTML around them."""
from __future__ import annotations

import base64
from urllib.parse import quote

STRIP = ["#F7E1E1", "#E9A3A8", "#CF5B6B", "#A3153A", "#6E0B24"]

PALETTES = {
    "light": {"line": "#1B2340", "muted": "#5B6475", "soft": "#D3D8E0", "faint": "#E9EDF2", "surface": "#FFFFFF",
              "bg": "#F3F5F7", "tissue": "#E48F99", "tissue_soft": "#F2C4C9", "skin": "#F1D6C2", "skin_shade": "#E2B898",
              "nail": "#F4CDD0", "accent": "#3B5BDB", "normal": "#1F7A6D", "refer": "#B3123A", "glow": "#E9A3A8"},
    "dark": {"line": "#E6E9F0", "muted": "#9AA3B5", "soft": "#3A4360", "faint": "#232A3F", "surface": "#1B2133",
             "bg": "#121624", "tissue": "#E48F99", "tissue_soft": "#C98C94", "skin": "#B58D74", "skin_shade": "#97715B",
             "nail": "#D9A9AE", "accent": "#8FA8FF", "normal": "#4C958A", "refer": "#D17189", "glow": "#CF5B6B"},
}


def img(svg: str, alt: str = "", cls: str = "") -> str:
    data = base64.b64encode(svg.encode("utf-8")).decode()
    role = f'alt="{alt}"' if alt else 'alt="" aria-hidden="true"'
    return f'<img class="{cls}" {role} src="data:image/svg+xml;base64,{data}">'


def _svg(vb: str, body: str, defs: str = "", style: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" fill="none" stroke-linecap="round" '
            f'stroke-linejoin="round"><defs>{defs}</defs>{f"<style>{style}</style>" if style else ""}{body}</svg>')


def _strip_gradient(gid: str) -> str:
    stops = "".join(f'<stop offset="{i / 4:.2f}" stop-color="{c}"/>' for i, c in enumerate(STRIP))
    return f'<linearGradient id="{gid}" x1="0" x2="1" y1="0" y2="0">{stops}</linearGradient>'


# ------------------------------------------------------------------ icons (mask, one style)
ICONS = {
    "eye": '<path d="M2.5 12s3.5-6.5 9.5-6.5 9.5 6.5 9.5 6.5-3.5 6.5-9.5 6.5S2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>'
           '<path d="M6.5 16.6c1.6 1.2 3.4 1.9 5.5 1.9s3.9-.7 5.5-1.9" stroke-dasharray="1.6 2"/>',
    "palm": '<path d="M7 21v-4.5c-1.4-1-2.6-2.7-3-4.6-.2-1 .8-1.6 1.6-.9L7 12.5V5.5a1.3 1.3 0 0 1 2.6 0V11V3.8a1.3 1.3 0 0 1 '
            '2.6 0V11V4.6a1.3 1.3 0 0 1 2.6 0V11.5V6.8a1.3 1.3 0 0 1 2.6 0V14c0 3-1.5 5-3.4 6.2V21"/>',
    "nail": '<rect x="7" y="2.5" width="10" height="19" rx="5"/><rect x="9.2" y="4.6" width="5.6" height="6.8" rx="2.6"/>',
    "camera": '<path d="M4 7.5h3l1.6-2.5h6.8L17 7.5h3a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 20 19.5H4A1.5 1.5 0 0 1 2.5 18V9A1.5 1.5 0 0 1 4 7.5z"/>'
              '<circle cx="12" cy="13" r="3.6"/>',
    "upload": '<path d="M12 15.5V4m0 0L7.5 8.5M12 4l4.5 4.5"/><path d="M4 14.5v3A2.5 2.5 0 0 0 6.5 20h11a2.5 2.5 0 0 0 2.5-2.5v-3"/>',
    "people": '<circle cx="9" cy="8" r="3"/><path d="M3.5 19.5c.6-3.2 2.8-5 5.5-5s4.9 1.8 5.5 5"/><circle cx="16.5" cy="9" r="2.4"/>'
              '<path d="M15.5 14.6c2.5-.3 4.4 1.3 5 4.4"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.3l2.7 2.7L16.2 9.4"/>',
    "light": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6'
             'M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/>',
    "glare": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M18.5 16.5l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7z"/>',
    "sharp": '<path d="M4 8V5.5A1.5 1.5 0 0 1 5.5 4H8M16 4h2.5A1.5 1.5 0 0 1 20 5.5V8M20 16v2.5a1.5 1.5 0 0 1-1.5 1.5H16M8 20H5.5A1.5 1.5 0 0 1 4 18.5V16"/>'
             '<circle cx="12" cy="12" r="3.5"/>',
    "makeup": '<path d="M14.5 3.5l6 6-8.5 8.5H6v-6z"/><path d="M6 18l-2.5 2.5"/><path d="M11 7l6 6"/>',
    "noflash": '<path d="M13 2.5L6 13.5h5.5L10 21.5l7-11h-5.5z"/><path d="M3.5 3.5l17 17"/>',
    "nopolish": '<rect x="8" y="9" width="8" height="12" rx="2.5"/><path d="M10 9V6.5h4V9M11 6.5V3h2v3.5"/><path d="M3.5 3.5l17 17"/>',
    "hand": '<path d="M8 13V6.5a1.4 1.4 0 0 1 2.8 0V12V4.6a1.4 1.4 0 0 1 2.8 0V12V5.8a1.4 1.4 0 0 1 2.8 0V13a7 7 0 0 1-7 7c-2.6 0-4.3-1.4-5.4-3.4L2.5 12.8'
            'c-.5-.9.6-1.8 1.4-1.1L6.5 14"/>',
    "still": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/><path d="M3 9v6M21 9v6"/>',
    "home": '<path d="M3.5 11L12 4l8.5 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5.5h4V20"/>',
    "screen": '<path d="M4 8V5.5A1.5 1.5 0 0 1 5.5 4H8M16 4h2.5A1.5 1.5 0 0 1 20 5.5V8M20 16v2.5a1.5 1.5 0 0 1-1.5 1.5H16M8 20H5.5A1.5 1.5 0 0 1 4 18.5V16"/>'
              '<path d="M5.5 12s2.6-4 6.5-4 6.5 4 6.5 4-2.6 4-6.5 4-6.5-4-6.5-4z"/><circle cx="12" cy="12" r="1.6"/>',
    "results": '<path d="M4 20V4"/><path d="M4 20h16"/><rect x="7" y="12" width="3" height="5" rx=".8"/><rect x="12" y="8" width="3" height="9" rx=".8"/>'
               '<rect x="17" y="5" width="3" height="12" rx=".8"/>',
    "insights": '<path d="M9 18.5h6M10 21.5h4"/><path d="M12 2.5a6.5 6.5 0 0 0-3.8 11.8c.5.4.8 1 .8 1.7v.5h6V16c0-.7.3-1.3.8-1.7A6.5 6.5 0 0 0 12 2.5z"/>',
    "about": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.5"/><path d="M12 7.6v.2"/>',
    "drop": '<path d="M12 3s6.5 7.2 6.5 11.5a6.5 6.5 0 0 1-13 0C5.5 10.2 12 3 12 3z"/>',
    "halfsun": '<path d="M12 4v16"/><path d="M12 7a5 5 0 0 0 0 10"/><path d="M12 7a5 5 0 0 1 0 10" stroke-dasharray="1.5 2"/>'
               '<path d="M4 12h1.5M18.5 12H20M6.3 6.3l1 1M16.7 16.7l1 1"/>',
    "blood": '<path d="M9 3.5s5 5.6 5 8.9a5 5 0 0 1-10 0C4 9.1 9 3.5 9 3.5z"/><path d="M15 14h5.5M15 18h5.5M17.5 10h3"/>',
    "pie": '<circle cx="12" cy="12" r="8.5"/><path d="M12 12V3.5"/><path d="M12 12l6.5 5.5"/>',
    "palette": '<path d="M12 3.5a8.5 8.5 0 1 0 0 17c1.3 0 1.8-.9 1.5-1.9-.4-1.2.3-2.6 1.9-2.6H17a3.5 3.5 0 0 0 3.5-3.5c0-5-3.8-9-8.5-9z"/>'
               '<circle cx="7.8" cy="11" r="1.1"/><circle cx="10.5" cy="7.3" r="1.1"/><circle cx="15" cy="7.8" r="1.1"/>',
    "alert": '<path d="M12 3.5l9.5 16.5h-19z"/><path d="M12 10v4.5"/><path d="M12 17.3v.2"/>',
    "arrow": '<path d="M4 12h15M14 7l5 5-5 5"/>',
}


def icon_svg(name: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


def icon_css() -> str:
    return "".join(f'.nh-i-{n}{{--icon:url("data:image/svg+xml,{quote(icon_svg(n))}")}}' for n in ICONS)


# ------------------------------------------------------------------ parts reused by several illustrations
def _eye(p: dict, x: float, y: float, s: float = 1.0, finger: bool = True) -> str:
    """Almond eye with the lower lid gently pulled down to show the pink inner rim, and the finger that pulls it."""
    g = (f'<g transform="translate({x} {y}) scale({s})" stroke="{p["line"]}" stroke-width="{3 / s:.2f}">'
         f'<path d="M-92 0 Q0 -66 92 0" />'
         f'<path d="M-82 8 Q0 78 82 8 Q0 44 -82 8 Z" fill="{p["tissue"]}" stroke="none"/>'
         f'<path d="M-82 8 Q0 44 82 8" stroke="{p["tissue_soft"]}" stroke-width="{2 / s:.2f}"/>'
         f'<path d="M-92 0 Q0 40 92 0" fill="{p["surface"]}"/>'
         f'<circle cx="0" cy="-4" r="25" fill="{p["faint"]}"/><circle cx="0" cy="-4" r="11" fill="{p["line"]}"/>'
         f'<circle cx="7" cy="-11" r="4" fill="{p["surface"]}" stroke="none"/>'
         f'<path d="M-82 8 Q0 78 82 8"/>'
         f'<path d="M-60 -34l-8 -14M-30 -46l-4 -15M4 -50v-15M36 -46l5 -14M64 -33l9 -12"/>')
    if finger:
        g += (f'<path d="M-22 104 L-22 60 Q0 34 22 60 L22 104" fill="{p["skin"]}"/>'
              f'<path d="M-11 50 Q0 44 11 50" stroke="{p["skin_shade"]}"/>')
    return g + "</g>"


def _palm(p: dict, x: float, y: float, s: float = 1.0) -> str:
    sw = 3 / s
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{p["line"]}" stroke-width="{sw:.2f}">'
            f'<path d="M-46 120 L-52 30 Q-54 14 -40 14 L42 14 Q56 14 54 30 L48 120 Z" fill="{p["skin"]}"/>'
            f'<rect x="-48" y="-62" width="20" height="82" rx="10" fill="{p["skin"]}"/>'
            f'<rect x="-24" y="-78" width="20" height="98" rx="10" fill="{p["skin"]}"/>'
            f'<rect x="0" y="-74" width="20" height="94" rx="10" fill="{p["skin"]}"/>'
            f'<rect x="24" y="-56" width="20" height="76" rx="10" fill="{p["skin"]}"/>'
            f'<path d="M-50 52 Q-80 40 -94 14 Q-100 2 -88 0 Q-74 0 -52 30" fill="{p["skin"]}"/>'
            f'<ellipse cx="0" cy="62" rx="30" ry="22" fill="{p["tissue_soft"]}" stroke="none"/>'
            f'<path d="M-36 44 Q-4 60 34 40M-30 78 Q0 88 30 74" stroke="{p["skin_shade"]}" stroke-width="{2 / s:.2f}"/>'
            f'<path d="M-46 14 L-52 30" /></g>')


def _nails(p: dict, x: float, y: float, s: float = 1.0) -> str:
    sw = 3 / s
    out = f'<g transform="translate({x} {y}) scale({s})" stroke="{p["line"]}" stroke-width="{sw:.2f}">'
    for dx, top, h in ((-56, -40, 170), (-16, -62, 192), (24, -54, 184), (64, -30, 160)):
        out += (f'<rect x="{dx - 16}" y="{top}" width="32" height="{h}" rx="16" fill="{p["skin"]}"/>'
                f'<rect x="{dx - 10}" y="{top + 8}" width="20" height="30" rx="9" fill="{p["nail"]}"/>'
                f'<path d="M{dx - 8} {top + 30} Q{dx} {top + 36} {dx + 8} {top + 30}" stroke="{p["tissue"]}" '
                f'stroke-width="{2 / s:.2f}"/>')
    return out + "</g>"


def _sun(p: dict, x: float, y: float, r: float = 10) -> str:
    rays = "".join(f'<path d="M{x} {y - r - 5}v-6" transform="rotate({a} {x} {y})"/>' for a in range(0, 360, 45))
    return f'<g stroke="{p["muted"]}" stroke-width="2.5"><circle cx="{x}" cy="{y}" r="{r}"/>{rays}</g>'


# ------------------------------------------------------------------ illustrations
def hero(mode: str) -> str:
    """Eye, palm and fingernails joined by the Hb colour strip, which glows once on load."""
    p = PALETTES[mode]
    dots = "".join(f'<circle cx="{cx}" cy="{cy}" r="5" fill="{p["line"]}"/>'
                   for cx, cy in ((210, 296), (550, 296), (890, 296)))
    links = (f'<g stroke="{p["muted"]}" stroke-width="2.5" stroke-dasharray="3 8">'
             f'<path d="M210 266 Q210 280 210 290"/><path d="M550 236 Q550 266 550 290"/>'
             f'<path d="M890 236 Q890 266 890 290"/></g>')
    defs = (_strip_gradient("hs") +
            '<filter id="blur" x="-10%" y="-200%" width="120%" height="500%"><feGaussianBlur stdDeviation="14"/></filter>'
            '<linearGradient id="sheen" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
            '</linearGradient><clipPath id="sc"><rect x="120" y="306" width="860" height="34" rx="17"/></clipPath>')
    style = ('.glow{opacity:.35;animation:glow 2.6s ease-out .3s both}'
             '.sheen{transform:translateX(-300px);animation:sheen 2.2s ease-in-out .5s both}'
             '@keyframes glow{0%{opacity:0}45%{opacity:.85}100%{opacity:.35}}'
             '@keyframes sheen{from{transform:translateX(-300px)}to{transform:translateX(1100px)}}'
             '@media (prefers-reduced-motion: reduce){.glow,.sheen{animation:none}.sheen{opacity:0}}')
    body = (_eye(p, 210, 150, 1.05) + _palm(p, 550, 120, 0.95) + _nails(p, 890, 112, 0.85) + links +
            f'<rect class="glow" x="120" y="304" width="860" height="38" rx="19" fill="{p["glow"]}" filter="url(#blur)"/>'
            f'<rect x="120" y="306" width="860" height="34" rx="17" fill="url(#hs)"/>'
            f'<g clip-path="url(#sc)"><rect class="sheen" x="0" y="300" width="260" height="48" fill="url(#sheen)"/></g>'
            f'<rect x="120" y="306" width="860" height="34" rx="17" stroke="{p["line"]}" stroke-opacity=".25" stroke-width="2"/>'
            + dots)
    return _svg("0 0 1100 360", body, defs, style)


def step(name: str, mode: str) -> str:
    p = PALETTES[mode]
    sw = 'stroke-width="3"'
    if name == "photo":
        body = (f'<rect x="70" y="14" width="80" height="140" rx="14" fill="{p["surface"]}" stroke="{p["line"]}" {sw}/>'
                f'<rect x="80" y="34" width="60" height="96" rx="6" fill="{p["faint"]}"/>'
                + _eye(p, 110, 78, 0.27, finger=False) +
                f'<circle cx="110" cy="24" r="3" fill="{p["line"]}"/><path d="M102 142h16" stroke="{p["line"]}" {sw}/>'
                + _sun(p, 186, 34, 9))
    elif name == "check":
        body = (f'<rect x="40" y="22" width="100" height="84" rx="10" fill="{p["faint"]}" stroke="{p["soft"]}" {sw}/>'
                + _eye(p, 90, 62, 0.33, finger=False) +
                f'<circle cx="130" cy="98" r="30" fill="{p["surface"]}" fill-opacity=".55" stroke="{p["line"]}" {sw}/>'
                f'<path d="M151 119l24 24" stroke="{p["line"]}" stroke-width="7"/>'
                + "".join(f'<circle cx="{cx}" cy="140" r="11" fill="{p["normal"]}"/><path d="M{cx - 5} 140l3.5 3.5 6.5-7" '
                          f'stroke="#fff" stroke-width="3"/>' for cx in (34, 62, 90)))
    else:
        body = (f'<rect x="28" y="20" width="164" height="124" rx="12" fill="{p["surface"]}" stroke="{p["line"]}" {sw}/>'
                f'<path d="M28 20v124" stroke="{p["refer"]}" stroke-width="10"/>'
                f'<circle cx="150" cy="64" r="24" stroke="{p["faint"]}" stroke-width="9"/>'
                f'<path d="M150 40 A24 24 0 1 1 129 76" stroke="{p["refer"]}" stroke-width="9"/>'
                f'<rect x="48" y="44" width="58" height="12" rx="6" fill="{p["refer"]}"/>'
                f'<rect x="48" y="64" width="42" height="8" rx="4" fill="{p["soft"]}"/>'
                f'<rect x="46" y="108" width="128" height="14" rx="7" fill="url(#ss)"/>'
                f'<path d="M104 102v26" stroke="{p["line"]}" stroke-width="3"/>')
    return _svg("0 0 220 170", body, _strip_gradient("ss"))


def guide(site: str, mode: str) -> str:
    p = PALETTES[mode]
    if site == "eye":
        body = _eye(p, 150, 92, 0.95)
    elif site == "palm":
        body = _palm(p, 150, 92, 0.78)
        body += f'<path d="M108 108h-10v12M192 108h10v12M108 168h-10v-12M192 168h10v-12" stroke="{p["accent"]}" stroke-width="3"/>'
    else:
        body = _nails(p, 150, 66, 0.72)
        body += f'<path d="M92 30h-10v12M208 30h10v12M92 90h-10v-12M208 90h10v-12" stroke="{p["accent"]}" stroke-width="3"/>'
    return _svg("0 0 300 200", f'<rect x="0" y="0" width="300" height="200" rx="18" fill="{p["faint"]}"/>' + body)


def header(name: str, mode: str) -> str:
    """Small header illustration per Insights tab and for About (no text)."""
    p = PALETTES[mode]
    bg = f'<rect width="240" height="120" rx="16" fill="{p["faint"]}"/>'
    if name == "data":
        hs = [18, 30, 46, 62, 54, 40, 70, 84, 60, 34]
        bars = "".join(f'<rect x="{26 + i * 19}" y="{100 - h}" width="13" height="{h}" rx="3" '
                       f'fill="{p["refer"] if i < 5 else p["normal"]}" fill-opacity=".85"/>' for i, h in enumerate(hs))
        body = bars + f'<path d="M119 18v86" stroke="{p["line"]}" stroke-width="2.5" stroke-dasharray="4 5"/>'
    elif name == "sites":
        body = (_eye(p, 50, 56, 0.28, finger=False) + _palm(p, 120, 50, 0.3) + _nails(p, 192, 42, 0.26) +
                "".join(f'<rect x="{x - 16}" y="{106 - h}" width="32" height="{h}" rx="4" fill="{p["soft"]}"/>'
                        for x, h in ((50, 16), (120, 22), (192, 12))))
    elif name == "clusters":
        import random
        rnd = random.Random(7)
        body = ""
        for cx, cy, col in ((60, 46, STRIP[1]), (120, 78, STRIP[2]), (178, 44, STRIP[3]), (110, 30, STRIP[0])):
            for _ in range(11):
                body += (f'<circle cx="{cx + rnd.gauss(0, 11):.1f}" cy="{cy + rnd.gauss(0, 9):.1f}" r="4.5" fill="{col}" '
                         f'stroke="{p["line"]}" stroke-opacity=".3"/>')
            body += f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="{p["line"]}" stroke-width="2.5"/>'
    elif name == "search":
        nodes = {(120, 18): None, (64, 54): (120, 18), (176, 54): (120, 18), (36, 92): (64, 54), (92, 92): (64, 54),
                 (148, 92): (176, 54), (204, 92): (176, 54)}
        best = {(120, 18), (176, 54), (148, 92)}
        body = ""
        for n, parent in nodes.items():
            if parent:
                on = n in best and parent in best
                body += (f'<path d="M{parent[0]} {parent[1]}L{n[0]} {n[1]}" stroke="{p["accent"] if on else p["soft"]}" '
                         f'stroke-width="{4 if on else 2.5}"/>')
        for n in nodes:
            body += (f'<circle cx="{n[0]}" cy="{n[1]}" r="{9 if n in best else 7}" fill="{p["surface"]}" '
                     f'stroke="{p["accent"] if n in best else p["muted"]}" stroke-width="3"/>')
    else:   # about
        body = (_eye(p, 82, 54, 0.42, finger=False) +
                f'<rect x="140" y="40" width="80" height="16" rx="8" fill="url(#hs2)"/>'
                f'<rect x="140" y="68" width="56" height="8" rx="4" fill="{p["soft"]}"/>'
                f'<rect x="140" y="84" width="70" height="8" rx="4" fill="{p["soft"]}"/>')
    return _svg("0 0 240 120", bg + body, _strip_gradient("hs2"))


def pipeline_node(name: str, mode: str) -> str:
    """One square icon per pipeline stage: photo, mask, features, model, threshold, result."""
    p = PALETTES[mode]
    frame = f'<rect x="4" y="4" width="112" height="112" rx="22" fill="{p["faint"]}" stroke="{p["soft"]}" stroke-width="2"/>'
    if name == "photo":
        body = (f'<rect x="26" y="30" width="68" height="60" rx="8" fill="{p["surface"]}" stroke="{p["line"]}" stroke-width="3"/>'
                + _eye(p, 60, 58, 0.26, finger=False))
    elif name == "mask":
        body = (f'<path d="M24 58 Q60 92 96 58 Q60 76 24 58 Z" fill="{p["tissue"]}"/>'
                f'<path d="M22 58 Q60 98 98 58" stroke="{p["accent"]}" stroke-width="3" stroke-dasharray="5 5"/>'
                f'<path d="M22 50 Q60 22 98 50" stroke="{p["muted"]}" stroke-width="3"/>')
    elif name == "features":
        body = "".join(f'<rect x="{24 + i * 20}" y="{86 - h}" width="13" height="{h}" rx="3" fill="{c}"/>'
                       for i, (h, c) in enumerate(((30, STRIP[1]), (48, STRIP[2]), (24, p["muted"]), (40, STRIP[3]))))
        body += f'<path d="M20 90h80" stroke="{p["line"]}" stroke-width="3"/>'
    elif name == "model":
        body = ""
        for cx in (34, 60, 86):
            body += (f'<path d="M{cx} 40v14M{cx} 54l-9 12M{cx} 54l9 12" stroke="{p["line"]}" stroke-width="3"/>'
                     f'<circle cx="{cx}" cy="38" r="5" fill="{p["line"]}"/><circle cx="{cx - 9}" cy="70" r="4" fill="{p["muted"]}"/>'
                     f'<circle cx="{cx + 9}" cy="70" r="4" fill="{p["muted"]}"/>')
        body += f'<path d="M30 88h60" stroke="{p["accent"]}" stroke-width="4"/><path d="M60 80v16" stroke="{p["accent"]}" stroke-width="4"/>'
    elif name == "threshold":
        body = (f'<path d="M24 76 A36 36 0 0 1 96 76" stroke="{p["soft"]}" stroke-width="10"/>'
                f'<path d="M24 76 A36 36 0 0 1 74 43" stroke="{p["refer"]}" stroke-width="10"/>'
                f'<path d="M60 76 L80 50" stroke="{p["line"]}" stroke-width="4"/><circle cx="60" cy="76" r="6" fill="{p["line"]}"/>')
    else:
        body = (f'<rect x="20" y="34" width="80" height="22" rx="11" fill="{p["refer"]}"/>'
                f'<rect x="20" y="66" width="80" height="22" rx="11" fill="{p["normal"]}"/>')
    return _svg("0 0 120 120", frame + body)


def swatch_chip(rgb: tuple[int, int, int], mode: str) -> str:
    p = PALETTES[mode]
    r, g, b = rgb
    return _svg("0 0 80 80", f'<rect x="3" y="3" width="74" height="74" rx="18" fill="rgb({r},{g},{b})" '
                             f'stroke="{p["line"]}" stroke-opacity=".25" stroke-width="2"/>'
                             f'<path d="M14 18 Q22 10 34 12" stroke="#fff" stroke-opacity=".45" stroke-width="5"/>')


# ------------------------------------------------------------------ "Why Netra-Hb" and "What we found"
def _person(p: dict, x: float, y: float, s: float = 1.0, fill: str | None = None) -> str:
    f = fill or p["soft"]
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{p["line"]}" stroke-width="{3 / s:.2f}">'
            f'<circle cx="0" cy="-34" r="13" fill="{p["skin"]}"/>'
            f'<path d="M-22 22 Q-22 -16 0 -16 Q22 -16 22 22 Z" fill="{f}"/></g>')


def why(name: str, mode: str) -> str:
    p = PALETTES[mode]
    bg = f'<rect width="240" height="150" rx="18" fill="{p["faint"]}"/>'
    if name == "worker":      # a health worker with a phone, visiting village homes
        houses = "".join(f'<path d="M{x} 96 l18 -16 l18 16 v26 h-36 z" fill="{p["surface"]}" stroke="{p["muted"]}" stroke-width="2.5"/>'
                         f'<rect x="{x + 13}" y="108" width="10" height="14" fill="{p["soft"]}"/>' for x in (130, 176))
        body = (houses + f'<path d="M20 124h200" stroke="{p["muted"]}" stroke-width="2.5"/>' + _person(p, 76, 100, 1.1, p["normal"]) +
                f'<rect x="96" y="70" width="16" height="26" rx="3" fill="{p["surface"]}" stroke="{p["line"]}" stroke-width="2.5"/>'
                '')
    elif name == "consistent":  # two examiners, two different answers; the app, one answer every time
        body = (_person(p, 46, 104, 0.9) + _person(p, 104, 104, 0.9) +
                f'<rect x="20" y="22" width="44" height="26" rx="10" fill="{p["surface"]}" stroke="{p["muted"]}" stroke-width="2.5"/>'
                f'<rect x="28" y="31" width="28" height="8" rx="4" fill="{STRIP[1]}"/>'
                f'<rect x="80" y="22" width="44" height="26" rx="10" fill="{p["surface"]}" stroke="{p["muted"]}" stroke-width="2.5"/>'
                f'<rect x="88" y="31" width="28" height="8" rx="4" fill="{STRIP[3]}"/>'
                f'<path d="M140 76h12" stroke="{p["muted"]}" stroke-width="3"/>'
                f'<rect x="160" y="40" width="58" height="84" rx="10" fill="{p["surface"]}" stroke="{p["line"]}" stroke-width="3"/>'
                + "".join(f'<rect x="170" y="{52 + i * 22}" width="38" height="12" rx="6" fill="{STRIP[2]}"/>' for i in range(3)))
    else:                       # scarce finger-prick strips: decide who gets one
        strips = "".join(f'<rect x="{40 + i * 22}" y="44" width="12" height="60" rx="4" fill="{p["surface"]}" '
                         f'stroke="{p["muted"]}" stroke-width="2.5" stroke-dasharray="{"4 4" if i > 1 else "0"}"/>'
                         f'<rect x="{42 + i * 22}" y="84" width="8" height="14" rx="2" fill="{p["soft"] if i > 1 else STRIP[2]}"/>'
                         for i in range(4))
        body = (f'<rect x="30" y="34" width="96" height="80" rx="10" stroke="{p["line"]}" stroke-width="3"/>' + strips +
                f'<path d="M178 44 s20 22 20 38 a20 20 0 0 1 -40 0 c0 -16 20 -38 20 -38z" fill="{STRIP[3]}"/>'
                f'<path d="M150 122h56" stroke="{p["normal"]}" stroke-width="5"/>')
    return _svg("0 0 240 150", bg + body)


def finding(name: str, mode: str, values: tuple[float, ...] = ()) -> str:
    """Small data-shaped illustrations for the findings panel. Bar heights come from the real numbers passed in."""
    p = PALETTES[mode]
    bg = f'<rect width="240" height="130" rx="18" fill="{p["faint"]}"/>'
    if name == "sites":           # values: eye, palm, nail ROC-AUC at equal size
        body = ""
        for i, (v, part) in enumerate(zip(values, ("eye", "palm", "nail"))):
            h = max((v - 0.5) * 300, 4)
            x = 44 + i * 64
            body += f'<rect x="{x}" y="{112 - h}" width="40" height="{h}" rx="6" fill="{[p["line"], p["muted"], p["soft"]][i]}"/>'
        body += f'<path d="M30 112h180" stroke="{p["muted"]}" stroke-width="2.5"/>'
    elif name == "honest":        # values: before, after (two pairs)
        body = ""
        for j, (a, b) in enumerate(zip(values[::2], values[1::2])):
            x = 36 + j * 104
            for k, (v, col) in enumerate(((a, p["soft"]), (b, p["line"]))):
                h = max(v * 150, 4)
                body += f'<rect x="{x + k * 34}" y="{112 - h}" width="28" height="{h}" rx="5" fill="{col}"/>'
            body += f'<path d="M{x + 14} {108 - a * 150} L{x + 48} {104 - b * 150}" stroke="{p["muted"]}" stroke-width="2.5" stroke-dasharray="4 4"/>'
        body += f'<path d="M24 112h192" stroke="{p["muted"]}" stroke-width="2.5"/>'
    elif name == "safeguards":    # an eye with kajal, a filter, a shield
        body = (_eye(p, 78, 62, 0.42, finger=False) +
                f'<path d="M44 74 Q78 92 112 74" stroke="{p["line"]}" stroke-width="6"/>'
                f'<path d="M168 30 l32 12 v24 c0 22 -14 36 -32 42 c-18 -6 -32 -20 -32 -42 v-24 z" fill="{p["surface"]}" '
                f'stroke="{p["normal"]}" stroke-width="4"/><path d="M155 68l9 9 17 -18" stroke="{p["normal"]}" stroke-width="4"/>')
    else:                         # search: values = BFS evaluations, local beam evaluations to optimum
        import math
        total, beam = values if values else (10, 10)
        w = 180 * min(math.log10(max(beam, 1)) / math.log10(max(total, 10)), 1)   # log scale: both runs stay visible
        ticks = "".join(f'<path d="M{30 + 180 * k / math.log10(max(total, 10)):.1f} 102v8" stroke="{p["muted"]}" stroke-width="2"/>'
                        for k in range(1, int(math.log10(max(total, 10))) + 1))
        body = (f'<rect x="30" y="30" width="180" height="18" rx="9" fill="{p["soft"]}"/>'
                f'<rect x="30" y="64" width="{w:.1f}" height="18" rx="9" fill="{p["accent"]}"/>'
                f'<circle cx="{30 + w:.1f}" cy="73" r="7" fill="{p["surface"]}" stroke="{p["accent"]}" stroke-width="3"/>'
                f'<path d="M30 106h180" stroke="{p["muted"]}" stroke-width="2"/>' + ticks)
    return _svg("0 0 240 130", bg + body)
