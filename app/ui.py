from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import art
from strings import STRINGS

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
RESULTS_DIR = ROOT / "outputs" / "results"

PORCELAIN, INK, SLATE, PALLOR, HAEM, CLEAR = "#F3F5F7", "#1B2340", "#5B6475", "#F2C4C9", "#B3123A", "#1F7A6D"
STRIP_STOPS = art.STRIP
HB_MIN, HB_MAX = 6.0, 15.0
# Text versions of haem/clear are lightened in dark mode: the base hues fail AA on the dark surface
LIGHT = {"bg": PORCELAIN, "surface": "#FFFFFF", "text": INK, "muted": SLATE, "line": "#D3D8E0", "grid": "#E1E5EB",
         "refer": HAEM, "normal": CLEAR, "series": [INK, SLATE, "#7E8799", "#A3ABBA"], "cell": "#E4E8EE"}
DARK = {"bg": "#121624", "surface": "#1B2133", "text": "#E6E9F0", "muted": "#9AA3B5", "line": "#2E3650", "grid": "#262D44",
        "refer": "#D17189", "normal": "#4C958A", "series": ["#E6E9F0", "#B4BCCB", "#8E97A9", "#6F7890"], "cell": "#2A3248"}

_FACE = '@font-face {{ font-family: "{f}"; src: url("/app/static/fonts/{file}") format("truetype"); font-weight: {w}; font-display: swap; }}'
FONT_FACES = "\n".join(_FACE.format(f=f, file=file, w=w) for f, file, w in (
    ("Atkinson Hyperlegible", "AtkinsonHyperlegible-Regular.ttf", 400),
    ("Atkinson Hyperlegible", "AtkinsonHyperlegible-Bold.ttf", 700),
    ("Bricolage Grotesque", "BricolageGrotesque-VF.ttf", "200 800"),
    ("Noto Sans Kannada", "NotoSansKannada-VF.ttf", "100 900"),
    ("Noto Sans Devanagari", "NotoSansDevanagari-VF.ttf", "100 900")))
DISPLAY_FONT = "Bricolage Grotesque, Noto Sans Kannada, Noto Sans Devanagari, sans-serif"
BODY_FONT = "Atkinson Hyperlegible, Noto Sans Kannada, Noto Sans Devanagari, sans-serif"

LANGS = {"en": "English", "kn": "ಕನ್ನಡ", "hi": "हिंदी"}

# (script, nav label key, URL path, icon), in nav order
PAGES = [
    ("Home.py", "nav_home", "", "home"),
    ("pages/1_Screen.py", "nav_screen", "Screen", "screen"),
    ("pages/2_Results.py", "nav_results", "Results", "results"),
    ("pages/3_Insights.py", "nav_insights", "Insights", "insights"),
    ("pages/4_About.py", "nav_about", "About", "about"),
]

# WHO anaemia cut-offs, g/dL; keys are STRINGS keys
AGE_BANDS = {"age_6_59m": 11.0, "age_5_11": 11.5, "age_12_14": 12.0, "age_15_woman": 12.0, "age_15_man": 13.0}
TRAINED_BAND = "age_6_59m"
LIMITS = ("limit_skin", "limit_makeup", "limit_adult", "limit_light", "limit_children")


def lang() -> str:
    return st.session_state.get("lang") or "en"


def is_dark() -> bool:
    return bool(st.session_state.get("dark", False))


def mode() -> str:
    return "dark" if is_dark() else "light"


def tokens() -> dict:
    return DARK if is_dark() else LIGHT


def t(key: str, **fmt: Any) -> str:
    entry = STRINGS.get(key, {})
    text = entry.get(lang()) or entry.get("en") or key
    return text.format(**fmt) if fmt else text


def inject_css() -> None:
    css = (APP_DIR / "style.css").read_text(encoding="utf-8")
    if is_dark():
        css = css.replace(".nh-dark {", ":root {")
    st.html(f"<style>{css}{art.icon_css()}</style>")


def setup_page(title_key: str, script: str) -> None:
    """script is this page's entry in PAGES, e.g. "pages/1_Screen.py"; it marks the current nav item."""
    st.session_state.setdefault("dark", False)   # light by default: the exhibition hall is bright
    st.session_state.setdefault("lang", "en")
    st.set_page_config(page_title=f"{t(title_key)} | Netra-Hb", page_icon=str(APP_DIR / "static" / "favicon.png"),
                       layout="wide", initial_sidebar_state="collapsed")
    inject_css()
    pio.templates.default = "netra_dark" if is_dark() else "netra"
    header()
    nav(script)


def header() -> None:
    with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="distribute", key="nh_header"):
        st.html('<p class="nh-brand"><span class="nh-brand-mark" aria-hidden="true"></span>Netra-Hb</p>')
        with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="right", width="content",
                          gap="medium", key="nh_controls"):
            st.segmented_control(t("language"), list(LANGS), format_func=LANGS.get, key="lang", required=True,
                                 label_visibility="collapsed", persist_state="session")
            st.toggle(t("dark"), key="dark", persist_state="session")


def nav(current: str) -> None:
    path = next(p for s, _, p, _ in PAGES if s == current)
    sels = [f'a[href="{path}"]', f'a[href$="/{path}"]'] if path else ['a[href=""]', 'a[href="/"]']
    sel = ", ".join(f'.stApp .st-key-nh_nav [data-testid="stPageLink"] {s}' for s in sels)
    rules = "".join(f'.stApp .st-key-nh_nav [data-testid="stElementContainer"]:nth-child({i + 1}) a::before'
                    f'{{--icon:url("data:image/svg+xml,{art.quote(art.icon_svg(icon))}")}}'
                    for i, (_, _, _, icon) in enumerate(PAGES))
    st.html(f'<style>{sel} {{ color: var(--text); box-shadow: inset 0 -3px 0 var(--text); font-weight: 700; }}{rules}</style>')
    with st.container(horizontal=True, wrap=False, gap="small", key="nh_nav"):
        for script, key, _, _ in PAGES:
            st.page_link(script, label=t(key))


def footer() -> None:
    st.html(f'<footer class="nh-footer">{html.escape(t("footer"))}</footer>')


def icon(name: str, cls: str = "") -> str:
    return f'<span class="nh-icon nh-i-{name} {cls}" aria-hidden="true"></span>'


def page_title(title: str, lede: str | None = None, art_html: str = "") -> None:
    body = f'<h1 class="nh-page-title">{html.escape(title)}</h1>'
    if lede:
        body += f'<p class="nh-section-lede">{html.escape(lede)}</p>'
    if art_html:
        body = f'<div class="nh-page-head"><div>{body}</div><div class="nh-page-art">{art_html}</div></div>'
    st.html(body)


def section(title: str, lede: str | None = None, art_html: str = "") -> None:
    body = f'<h2 class="nh-section-title">{html.escape(title)}</h2>'
    if lede:
        body += f'<p class="nh-section-lede">{html.escape(lede)}</p>'
    if art_html:
        body = f'<div class="nh-sec-head"><div>{body}</div><div class="nh-sec-art">{art_html}</div></div>'
    st.html(body)


def spacer(small: bool = False) -> None:
    st.html(f'<div class="{"nh-spacer-sm" if small else "nh-spacer"}"></div>')


def note(text: str, warn: bool = False) -> None:
    st.html(f'<p class="nh-note{" nh-note-warn" if warn else ""}">{html.escape(text)}</p>')


def read_result(name: str) -> dict | None:
    path = RESULTS_DIR / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def read_csv(name: str) -> pd.DataFrame | None:
    path = ROOT / "outputs" / name
    return pd.read_csv(path) if path.exists() else None


def missing(name: str, script: str) -> None:
    st.html(f'<p class="nh-missing">{t("missing", path=f"<code>outputs/{html.escape(name)}</code>", cmd=f"<code>python -m scripts.{html.escape(script)}</code>")}</p>')


def _hb_frac(hb: float) -> float:
    return min(max((hb - HB_MIN) / (HB_MAX - HB_MIN), 0.0), 1.0)


_STRIP_HTML = """<!doctype html><html><head><meta charset="utf-8">
<style>
__FACES__
:root { --text: __TEXT__; --muted: __MUTED__; --bg: __BG__; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: transparent; color: var(--text);
  font-family: "Atkinson Hyperlegible", "Noto Sans Kannada", "Noto Sans Devanagari", sans-serif;
  font-variant-numeric: tabular-nums; }
.wrap { display: flex; align-items: flex-end; gap: 20px; padding: 4px 1px 0; }
.photo { position: relative; flex: none; width: var(--pw); }
.photo img { display: block; width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 12px; }
.photo .ring { position: absolute; width: 22px; height: 22px; margin: -11px 0 0 -11px; border-radius: 50%;
  border: 2px solid #fff; box-shadow: 0 0 0 1px rgba(27,35,64,.5); }
.scale { position: relative; flex: 1; min-width: 0; padding-top: var(--top); }
.bar { position: relative; height: var(--bh); border-radius: 999px; background: linear-gradient(90deg, __STOPS__);
  box-shadow: inset 0 0 0 1px rgba(27,35,64,.16), 0 1px 2px rgba(27,35,64,.10); overflow: hidden; }
.bar::after { content: ""; position: absolute; inset: 0; border-radius: inherit;
  background: linear-gradient(180deg, rgba(255,255,255,.42) 0%, rgba(255,255,255,.08) 46%, rgba(0,0,0,0) 54%, rgba(0,0,0,.08) 100%); }
.cut { position: absolute; top: calc(var(--top) - 10px); height: calc(var(--bh) + 20px); width: 0;
  border-left: 2px solid var(--text); }
.cut span { position: absolute; top: calc(100% + 30px); left: 0; transform: translateX(var(--cx, -50%));
  white-space: nowrap; font-size: 14px; color: var(--text); font-weight: 700; }
.ticks { position: relative; height: 30px; margin-top: 2px; }
.tick { position: absolute; top: 0; width: 0; display: flex; flex-direction: column; align-items: center; }
.tick i { display: block; width: 1px; height: 7px; background: var(--muted); }
.tick b { white-space: nowrap; font-weight: 400; font-size: 14px; color: var(--muted); margin-top: 3px; }
.unit { position: absolute; left: 0; top: calc(var(--top) + var(--bh) + 40px); font-size: 14px; color: var(--muted); }
.tick.first b { transform: translateX(50%); }
.tick.last b { transform: translateX(-50%); }
@media (max-width: 480px) { .tick:nth-child(even):not(.last) b { display: none; } .unit { display: none; } }
.swatch { position: absolute; top: 24px; width: 44px; margin-left: -22px; display: flex; flex-direction: column;
  align-items: center; will-change: transform; }
.chip { width: 44px; height: 44px; border-radius: 10px; border: 3px solid #fff;
  box-shadow: 0 6px 18px rgba(27,35,64,.28), 0 0 0 1px rgba(27,35,64,.18); }
.stem { width: 2px; height: calc(var(--top) - 74px); background: var(--text); opacity: .6; }
.swatch span { position: absolute; bottom: calc(100% + 4px); white-space: nowrap; font-size: 14px; font-weight: 700; }
.hidden { opacity: 0; }
</style></head><body>
<div class="wrap" role="img" aria-label="__ARIA__">
  __PHOTO__
  <div class="scale" id="scale">
    <div class="bar"></div>
    __CUT__
    __SWATCH__
    <div class="ticks">__TICKS__</div>
    <div class="unit">__UNIT__</div>
  </div>
</div>
<script>
(() => {
  const animate = __ANIMATE__;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const sw = document.getElementById("swatch"), cut = document.getElementById("cut");
  if (!sw || !animate || reduce) { if (sw) sw.classList.remove("hidden"); if (cut) cut.classList.remove("hidden"); return; }
  const ring = document.getElementById("ring");
  const end = sw.getBoundingClientRect();
  let dx, dy;
  if (ring) {
    const r = ring.getBoundingClientRect();
    dx = (r.left + r.width / 2) - (end.left + end.width / 2);
    dy = (r.top + r.height / 2) - (end.top + 42);
  } else { dx = -end.left + 12; dy = 6; }
  const travel = sw.animate([
    { transform: `translate(${dx}px, ${dy}px) scale(.35)`, opacity: 0 },
    { transform: `translate(${dx}px, ${dy - 18}px) scale(1.15)`, opacity: 1, offset: .28 },
    { transform: "translate(0, -6px) scale(1.05)", offset: .86 },
    { transform: "none", opacity: 1 }
  ], { duration: 1300, delay: 250, easing: "cubic-bezier(.3,.7,.2,1)", fill: "both" });
  sw.classList.remove("hidden");
  travel.finished.then(() => {
    cut.classList.remove("hidden");
    cut.animate([{ transform: "translateY(-14px)", opacity: 0 }, { transform: "none", opacity: 1 }],
                { duration: 320, easing: "cubic-bezier(.2,.8,.2,1)" });
  });
})();
</script></body></html>"""


def hb_strip(hb: float | None = None, swatch_rgb: tuple[int, int, int] | None = None, threshold: float = 11.0,
             photo_url: str | None = None, photo_point: tuple[float, float] = (0.5, 0.5),
             animate: bool = True, show_cutoff: bool = True, photo_width: int = 120, bar_height: int = 30,
             swatch_label: str | None = None) -> None:
    """The digital Hb colour scale. With hb and swatch_rgb, the tissue swatch lifts out of the photo (if given)
    and settles at its position; then the cut-off marker drops. prefers-reduced-motion shows the final state."""
    tk = tokens()
    has_swatch = hb is not None and swatch_rgb is not None
    top = 116 if has_swatch else 14
    photo = ""
    if photo_url:
        px, py = photo_point
        photo = (f'<div class="photo"><img src="{html.escape(photo_url)}" alt="">'
                 f'<div class="ring" id="ring" style="left:{px * 100:.1f}%;top:{py * 100:.1f}%"></div></div>')
    cut = ""
    if show_cutoff:
        cls = "cut hidden" if has_swatch and animate else "cut"
        cut = (f'<div class="{cls}" id="cut" style="left:{_hb_frac(threshold) * 100:.2f}%">'
               f'<span>{html.escape(t("cutoff"))} {threshold:g} g/dL</span></div>')
    swatch = ""
    if has_swatch:
        r, g, b = (int(c) for c in swatch_rgb)
        swatch = (f'<div class="swatch{" hidden" if animate else ""}" id="swatch" style="left:{_hb_frac(hb) * 100:.2f}%">'
                  f'<span>{html.escape(swatch_label or t("this_photo"))}</span>'
                  f'<div class="chip" style="background:rgb({r},{g},{b})"></div><div class="stem"></div></div>')
    ticks = "".join(
        f'<div class="tick{" first" if v == HB_MIN else " last" if v == HB_MAX else ""}" '
        f'style="left:{_hb_frac(v) * 100:.2f}%"><i></i><b>{v:g}</b></div>'
        for v in range(int(HB_MIN), int(HB_MAX) + 1))
    doc = (_STRIP_HTML.replace("__TICKS__", ticks).replace("__FACES__", FONT_FACES).replace("__TEXT__", tk["text"])
           .replace("__MUTED__", tk["muted"]).replace("__BG__", tk["bg"]).replace("__STOPS__", ", ".join(STRIP_STOPS))
           .replace("__UNIT__", html.escape(t("strip_unit"))).replace("__ARIA__", html.escape(t("strip_aria"))).replace("__PHOTO__", photo).replace("__CUT__", cut)
           .replace("__SWATCH__", swatch).replace("__ANIMATE__", "true" if animate else "false"))
    doc = doc.replace("<style>", f"<style>:root{{--top:{top}px;--bh:{bar_height}px;--pw:{photo_width}px}}", 1)
    label_room = 60
    height = max(top + bar_height + label_room + 6, photo_width + 12 if photo_url else 0)
    st.iframe(doc, height=height, tab_index=-1)   # decorative: the result is also given as text


_ICON_OK = '<span class="nh-icon nh-icon-sm nh-icon-ok" aria-hidden="true"></span>'
_ICON_RETAKE = '<span class="nh-icon nh-icon-sm nh-icon-retake" aria-hidden="true"></span>'
CHECK_ICONS = {"light": "light", "glare": "glare", "sharp": "sharp", "makeup": "makeup"}


def quality_chips(checks: dict[str, bool]) -> bool:
    """checks maps light / glare / sharp / makeup to pass (True) or retake (False). Returns True if all pass."""
    chips, fixes = [], []
    for name, ok in checks.items():
        chips.append(f'<span class="nh-chip{"" if ok else " retake"}">{icon(CHECK_ICONS[name], "nh-icon-sm")}'
                     f'{html.escape(t("q_" + name))}: {html.escape(t("q_ok") if ok else t("q_retake"))}'
                     f'{_ICON_OK if ok else _ICON_RETAKE}</span>')
        if not ok:
            fixes.append(f"<li>{html.escape(t('fix_' + name))}</li>")
    fix_html = f'<ul class="nh-fixes">{"".join(fixes)}</ul>' if fixes else ""
    st.html(f'<div class="nh-chips" role="status">{"".join(chips)}</div>{fix_html}')
    return not fixes


def known_limits() -> None:
    items = "".join(f"<li>{icon('alert', 'nh-icon-sm')}<span>{html.escape(t(k))}</span></li>" for k in LIMITS)
    st.html(f'<aside class="nh-limits"><h4>{html.escape(t("limits_title"))}</h4><ul>{items}</ul></aside>')


def empty_state(key: str) -> None:
    st.html(f'<div class="nh-empty">{html.escape(t(key))}</div>')


# ---------------------------------------------------------------- small animated components (iframes)
_FRAME = """<!doctype html><html><head><meta charset="utf-8"><style>__FACES__
:root { --text: __TEXT__; --muted: __MUTED__; --line: __LINE__; --state: __STATE__; }
html, body { margin: 0; background: transparent; color: var(--text);
  font-family: "Atkinson Hyperlegible", "Noto Sans Kannada", "Noto Sans Devanagari", sans-serif; font-variant-numeric: tabular-nums; }
__CSS__
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
</style></head><body>__BODY__</body></html>"""


def _frame(body: str, css: str, height: int, state: str | None = None) -> None:
    tk = tokens()
    doc = (_FRAME.replace("__FACES__", FONT_FACES).replace("__TEXT__", tk["text"]).replace("__MUTED__", tk["muted"])
           .replace("__LINE__", tk["line"]).replace("__STATE__", state or tk["text"]).replace("__CSS__", css)
           .replace("__BODY__", body))
    st.iframe(doc, height=height, tab_index=-1)


def gauge(p: float, refer: bool, animate: bool = True) -> None:
    """Circular risk gauge: the arc fills to the calibrated chance of anaemia, in the result's state colour."""
    tk = tokens()
    r, c = 52, 2 * 3.14159 * 52
    off = c * (1 - max(min(p, 1), 0))
    css = (f".g {{ display: flex; flex-direction: column; align-items: center; }} svg {{ width: 150px; height: 150px; }}"
           f".track {{ stroke: {tk['line']}; }} .arc {{ stroke: var(--state); stroke-dasharray: {c:.1f};"
           f" stroke-dashoffset: {off:.1f}; transform: rotate(-90deg); transform-origin: 60px 60px; }}"
           f".anim .arc {{ animation: fill 1.2s cubic-bezier(.3,.7,.2,1) .2s both; }}"
           f"@keyframes fill {{ from {{ stroke-dashoffset: {c:.1f}; }} to {{ stroke-dashoffset: {off:.1f}; }} }}"
           ".num { font: 700 30px 'Bricolage Grotesque', sans-serif; fill: var(--text); }"
           ".lbl { font-size: 14px; color: var(--muted); text-align: center; max-width: 150px; margin-top: 2px; }")
    body = (f'<div class="g{" anim" if animate else ""}" role="img" aria-label="{round(p * 100)}% {html.escape(t("gauge_label"))}">'
            f'<svg viewBox="0 0 120 120"><circle class="track" cx="60" cy="60" r="{r}" fill="none" stroke-width="11"/>'
            f'<circle class="arc" cx="60" cy="60" r="{r}" fill="none" stroke-width="11" stroke-linecap="round"/>'
            f'<text class="num" x="60" y="70" text-anchor="middle">{round(p * 100)}%</text></svg>'
            f'<div class="lbl">{html.escape(t("gauge_label"))}</div></div>')
    _frame(body, css, 196, tk["refer"] if refer else tk["normal"])


def scan_view(url: str, height: int = 300, animate: bool = True) -> None:
    """The analysis view: photo with the measured-tissue mask, and a scan line that sweeps once while analysing."""
    tk = tokens()
    css = (f".w {{ position: relative; height: {height - 6}px; border-radius: 12px; overflow: hidden; background: {tk['surface']}; }}"
           ".w img { width: 100%; height: 100%; object-fit: contain; image-rendering: pixelated; display: block; }"
           f".s {{ position: absolute; left: 0; right: 0; height: 3px; top: 0; background: {art.PALETTES[mode()]['accent']};"
           f" box-shadow: 0 0 16px 6px {art.PALETTES[mode()]['accent']}55; opacity: 0; }}"
           ".anim .s { animation: scan 1.4s ease-in-out .15s 1 both; }"
           "@keyframes scan { 0% { top: 0; opacity: 1; } 90% { opacity: 1; } 100% { top: 100%; opacity: 0; } }")
    _frame(f'<div class="w{" anim" if animate else ""}"><img src="{url}" alt=""><div class="s"></div></div>', css, height)


def _template(tk: dict) -> go.layout.Template:
    axis = dict(gridcolor=tk["grid"], linecolor=tk["line"], zerolinecolor=tk["line"], tickcolor=tk["line"],
                tickfont=dict(color=tk["muted"], size=14), title=dict(font=dict(color=tk["muted"], size=14)),
                showline=True, ticks="outside")
    return go.layout.Template(layout=dict(
        font=dict(family=BODY_FONT, color=tk["text"], size=14),
        title=dict(font=dict(family=DISPLAY_FONT, size=20, color=tk["text"]), x=0, xanchor="left"),
        colorway=[tk["refer"], tk["normal"], tk["muted"]],
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=axis, yaxis=axis,
        legend=dict(font=dict(color=tk["text"], size=14), bgcolor="rgba(0,0,0,0)", orientation="h",
                    yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(font=dict(family=BODY_FONT, size=14, color=tk["text"]), bgcolor=tk["surface"],
                        bordercolor=tk["line"]),
        annotationdefaults=dict(font=dict(color=tk["muted"], size=13)),
        margin=dict(l=56, r=16, t=48, b=48),
        colorscale=dict(sequential=[[i / 4, c] for i, c in enumerate(STRIP_STOPS)]),
    ))


pio.templates["netra"] = _template(LIGHT)
pio.templates["netra_dark"] = _template(DARK)


def class_color(anaemic: bool) -> str:
    return tokens()["refer"] if anaemic else tokens()["normal"]


def chart(fig: go.Figure, takeaway: str, height: int | None = None, key: str | None = None) -> None:
    """Every chart carries a one-line plain-language takeaway above it."""
    st.html(f'<p class="nh-takeaway">{html.escape(takeaway)}</p>')
    fig.update_layout(template="netra_dark" if is_dark() else "netra", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", **({"height": height} if height else {}))
    st.plotly_chart(fig, config={"displayModeBar": False}, key=key, theme=None)   # our template, not Streamlit's
