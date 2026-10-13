from __future__ import annotations

import base64
import io
import json
import sys
from urllib.parse import quote

import cv2
import joblib
import numpy as np
import streamlit as st
from PIL import Image, ImageOps

import ui

for p in (ui.ROOT, ui.ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from netra import screening  # noqa: E402
from netra.masks import load_image  # noqa: E402

MODELS_DIR = ui.ROOT / "outputs" / "models"
SAMPLES_DIR = ui.APP_DIR / "samples"
SITES = ("eye", "palm", "nail")
DISPLAY_MAX = 900   # photos are downscaled to this long side for display and clicking


@st.cache_resource(show_spinner=False)
def bundles() -> dict[str, dict] | None:
    paths = {s: MODELS_DIR / f"screen_{s}.joblib" for s in SITES}
    if not all(p.exists() for p in paths.values()):
        return None
    return {s: joblib.load(p) for s, p in paths.items()}


@st.cache_data(show_spinner=False)
def samples() -> list[dict]:
    path = SAMPLES_DIR / "samples.json"
    return json.loads(path.read_text(encoding="utf-8"))["samples"] if path.exists() else []


def decode(data: bytes) -> tuple[np.ndarray, np.ndarray | None] | None:
    try:
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
    except Exception:
        return None
    im.thumbnail((DISPLAY_MAX, DISPLAY_MAX))
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    buf.seek(0)
    return load_image(buf)


def load_sample(sample: dict) -> tuple[np.ndarray, np.ndarray | None]:
    return load_image(SAMPLES_DIR / sample["file"])


def sample_thumb(rgb: np.ndarray, alpha: np.ndarray | None) -> str:
    """Crop to the tissue (transparent or black background trimmed) for the sample tiles."""
    tissue = screening.auto_tissue(rgb, alpha)
    if tissue is not None:
        ys, xs = np.nonzero(tissue)
        sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        rgb, alpha = rgb[sl], None if alpha is None else alpha[sl]
    return png_url(on_black(rgb, alpha))


def png_url(rgb: np.ndarray, alpha: np.ndarray | None = None) -> str:
    arr = rgb if alpha is None else np.dstack([rgb, alpha])
    buf = io.BytesIO()
    Image.fromarray(arr.astype(np.uint8)).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def overlay(rgb: np.ndarray, tissue: np.ndarray | None, point: tuple[int, int] | None = None,
            dim: bool = True, box: tuple[int, int, int, int] | None = None) -> np.ndarray:
    """Photo with the selected tissue outlined (white over ink, readable on any skin or background).
    dim=False for photos whose background is already cleared (transparent or black)."""
    out = rgb.copy()
    if tissue is not None and tissue.any():
        if dim:
            d = out.astype(float)
            d[~tissue] = d[~tissue] * 0.55 + 255 * 0.12
            out = d.astype(np.uint8)
        cs, _ = cv2.findContours(tissue.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        lw = max(2, round(max(rgb.shape[:2]) / 250))
        cv2.drawContours(out, cs, -1, ui_rgb(ui.INK), lw + 2)
        cv2.drawContours(out, cs, -1, (255, 255, 255), lw)
    if box is not None:
        lw = max(2, round(max(rgb.shape[:2]) / 300))
        cv2.rectangle(out, box[:2], box[2:], ui_rgb(ui.INK), lw + 2)
        cv2.rectangle(out, box[:2], box[2:], (255, 255, 255), lw)
    if point is not None:
        r = max(6, round(max(rgb.shape[:2]) / 60))
        cv2.circle(out, point, r + 2, ui_rgb(ui.INK), 2)
        cv2.circle(out, point, r, (255, 255, 255), 2)
    return out


def display_size(rgb: np.ndarray, tissue: np.ndarray | None, alpha: np.ndarray | None = None, long_side: int = 560):
    """Small training-set crops are enlarged for display so the outline is not jagged."""
    scale = long_side / max(rgb.shape[:2])
    if scale <= 1:
        return rgb, tissue, alpha
    size = (round(rgb.shape[1] * scale), round(rgb.shape[0] * scale))
    up = lambda m: None if m is None else cv2.resize(m.astype(np.uint8), size, interpolation=cv2.INTER_LINEAR)
    t = up(tissue)
    return (cv2.resize(rgb, size, interpolation=cv2.INTER_CUBIC), None if t is None else t > 0, up(alpha))


def ui_rgb(hex_: str) -> tuple[int, int, int]:
    return tuple(int(hex_[i:i + 2], 16) for i in (1, 3, 5))


def on_black(rgb: np.ndarray, alpha: np.ndarray | None) -> np.ndarray:
    """Transparent pixels shown on the page background colour rather than black noise."""
    if alpha is None:
        return rgb
    bg = np.array(ui_rgb(ui.LIGHT["surface"]), float)
    a = (alpha.astype(float) / 255)[..., None]
    return (rgb * a + bg * (1 - a)).astype(np.uint8)


def measured_preview(photo: screening.Photo, long_side: int = 420) -> str:
    """Zoomed view of exactly the measured pixels: colour = measured, slate = removed (makeup, lashes, glare),
    surface = not selected. Nearest-neighbour enlargement so every pixel stays a pixel."""
    bg, grey = ui_rgb(ui.LIGHT["surface"]), ui_rgb(ui.SLATE)
    out = np.empty_like(photo.rgb)
    out[:] = bg
    out[photo.tissue & ~photo.mask] = grey
    out[photo.mask] = photo.rgb[photo.mask]
    scale = max(1, long_side // max(out.shape[:2]))
    return png_url(cv2.resize(out, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST))


def swatch_point(photo: screening.Photo) -> tuple[float, float]:
    """Fractional point inside the tissue whose colour is closest to the median swatch (where the swatch lifts off)."""
    ys, xs = np.nonzero(photo.mask if photo.mask.any() else photo.tissue)
    d = np.abs(photo.rgb[ys, xs].astype(float) - np.array(photo.swatch)).sum(axis=1)
    i = int(np.argmin(d + 0.002 * ((ys - ys.mean()) ** 2 + (xs - xs.mean()) ** 2)))
    h, w = photo.rgb.shape[:2]
    return xs[i] / w, ys[i] / h


def square_thumb(photo: screening.Photo, point: tuple[float, float]) -> tuple[str, tuple[float, float]]:
    """Tissue crop padded to a square on the surface colour, with the point re-expressed in the square."""
    h, w = photo.rgb.shape[:2]
    s = max(h, w)
    bg = ui_rgb(ui.LIGHT["surface"])
    canvas = np.full((s, s, 3), bg, np.uint8)
    oy, ox = (s - h) // 2, (s - w) // 2
    crop = np.where(photo.tissue[..., None], photo.rgb, np.array(bg, np.uint8))
    canvas[oy:oy + h, ox:ox + w] = crop
    return png_url(canvas), ((point[0] * w + ox) / s, (point[1] * h + oy) / s)


def analyse(site: str, photo: screening.Photo, p_override: float | None = None) -> dict:
    b = bundles()
    knots = screening.hb_knots(b["eye"])
    feats = screening.features(photo)
    p = screening.probability(b[site], feats) if p_override is None else p_override
    pos = screening.strip_position(p, b[site]["threshold"], knots)
    lo, hi = screening.uncertainty_band(b[site], p)
    point = swatch_point(photo)
    thumb, thumb_pt = square_thumb(photo, point)
    return {"site": site, "p": p, "band": (lo, hi), "position": pos, "makeup_frac": photo.makeup_frac,
            "familiarity": screening.familiarity(b[site], feats),
            "hb_mae": b["eye"]["hb_mae"], "feats_key": tuple(sorted(feats.items())), "swatch": photo.swatch,
            "thumb": thumb, "thumb_point": thumb_pt, "checks": photo.checks}


NOUNS = {"eye": "eyelid", "palm": "palm", "nail": "nail bed"}
REASONS = {
    ("redness", False): "The {site} is less red than {pct}% of healthy children.",
    ("redness", True): "The {site} is redder than {pct}% of healthy children.",
    ("lightness", False): "The {site} is darker than {pct}% of healthy children.",
    ("lightness", True): "The {site} is paler than {pct}% of healthy children.",
    ("blood_index", False): "Its blood-colour index is lower than in {pct}% of healthy children.",
    ("blood_index", True): "Its blood-colour index is higher than in {pct}% of healthy children.",
    ("red_share", False): "Red makes up less of its colour than in {pct}% of healthy children.",
    ("red_share", True): "Red makes up more of its colour than in {pct}% of healthy children.",
    ("tone", False): "Its colour is less yellow than in {pct}% of healthy children.",
    ("tone", True): "Its colour is more yellow than in {pct}% of healthy children.",
}


def reason_text(site: str, r: dict) -> str:
    high = r["pct"] >= 50
    pct = min(max(round(r["pct"]) if high else round(100 - r["pct"]), 1), 99)
    return REASONS[(r["group"], high)].format(site=NOUNS[site], pct=pct)


# ---- Line illustrations: CSS masks (st.html strips inline SVG), lines in currentColor and tissue in pallor ----
_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 150" fill="none" stroke="black" ' \
       'stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{}</svg>'
_SUN = ('<circle cx="196" cy="22" r="8"/><path d="M196 6v-3M196 41v-3M180 22h-3M215 22h-3M184.7 10.7l-2-2'
        'M209.3 35.3l-2-2M184.7 33.3l-2 2M209.3 8.7l-2 2"/>'
        '<path d="M26 8l-9 15h9l-7 13"/><path d="M10 6l26 32"/>')
ILLUSTRATIONS = {
    "eye": (
        '<path d="M38 64 Q110 14 182 64"/><path d="M38 64 Q110 96 182 64"/><circle cx="110" cy="57" r="17"/>'
        '<circle cx="110" cy="57" r="6"/><path d="M48 72 Q110 132 172 72"/>'
        '<path d="M60 26l-4-9M86 17l-2-9M134 17l2-9M160 26l4-9"/>'
        '<path d="M92 150v-28 q18-16 36 0v28"/><path d="M104 118 q6-3 12 0"/>' + _SUN,
        '<path d="M44 68 Q110 102 176 68 Q110 136 44 68 Z"/>'),
    "palm": (
        '<path d="M70 146 L66 92 Q64 80 74 80 L146 80 Q156 80 154 92 L150 146"/>'
        '<rect x="70" y="26" width="16" height="58" rx="8"/><rect x="89" y="16" width="16" height="66" rx="8"/>'
        '<rect x="108" y="18" width="16" height="64" rx="8"/><rect x="127" y="32" width="16" height="52" rx="8"/>'
        '<path d="M66 104 Q46 96 34 78 Q28 68 38 66 Q50 66 66 88"/>'
        '<path d="M84 96h-8v8M136 96h8v8M84 136h-8v-8M136 136h8v-8"/>' + _SUN,
        '<ellipse cx="110" cy="116" rx="22" ry="16"/>'),
    "nail": (
        '<rect x="52" y="34" width="34" height="116" rx="17"/><rect x="93" y="22" width="34" height="128" rx="17"/>'
        '<rect x="134" y="38" width="34" height="112" rx="17"/>'
        '<rect x="59" y="42" width="20" height="24" rx="9"/><rect x="100" y="30" width="20" height="26" rx="9"/>'
        '<rect x="141" y="46" width="20" height="24" rx="9"/>'
        '<path d="M46 20h-8v8M174 20h8v8M46 82h-8v-8M174 82h8v-8"/>' + _SUN,
        '<rect x="61" y="44" width="16" height="20" rx="7"/><rect x="102" y="32" width="16" height="22" rx="7"/>'
        '<rect x="143" y="48" width="16" height="20" rx="7"/>'),
}


def _mask_url(inner: str, fill: bool = False) -> str:
    svg = _SVG.format(inner)
    if fill:
        svg = svg.replace('fill="none" stroke="black"', 'fill="black" stroke="none"')
    return f'url("data:image/svg+xml,{quote(svg)}")'


def illustration(site: str) -> str:
    lines, tint = ILLUSTRATIONS[site]
    return (f'<div class="nh-illo" aria-hidden="true">'
            f'<span class="nh-illo-tint" style=\'--icon:{_mask_url(tint, fill=True)}\'></span>'
            f'<span class="nh-illo-line" style=\'--icon:{_mask_url(lines)}\'></span></div>')
