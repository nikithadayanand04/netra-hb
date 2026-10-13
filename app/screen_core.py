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

import art
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
    return png_url(rgb, alpha)   # transparent background: works in light and dark mode


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
    bg = np.array(ui_rgb(ui.tokens()["surface"]), float)
    a = (alpha.astype(float) / 255)[..., None]
    return (rgb * a + bg * (1 - a)).astype(np.uint8)


def measured_preview(photo: screening.Photo, long_side: int = 420) -> str:
    """Analysis view of exactly the measured pixels: tissue tinted with the accent (measured), grey = removed
    (makeup, lashes, glare), transparent = not selected. Nearest-neighbour enlargement keeps every pixel a pixel."""
    accent = np.array(ui_rgb(art.PALETTES[ui.mode()]["accent"]), float)
    grey = np.array((128, 134, 148), float)
    rgb = photo.rgb.astype(float)
    out = np.zeros((*rgb.shape[:2], 4), np.uint8)
    out[photo.mask, :3] = (rgb[photo.mask] * 0.45 + accent * 0.55).astype(np.uint8)
    removed = photo.tissue & ~photo.mask
    out[removed, :3] = (rgb[removed].mean(axis=1, keepdims=True) * 0.35 + grey * 0.65).astype(np.uint8)
    out[photo.tissue, 3] = 255
    scale = max(1, long_side // max(out.shape[:2]))
    big = cv2.resize(out, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    return png_url(big[..., :3], big[..., 3])


def swatch_point(photo: screening.Photo) -> tuple[float, float]:
    """Fractional point inside the tissue whose colour is closest to the median swatch (where the swatch lifts off)."""
    ys, xs = np.nonzero(photo.mask if photo.mask.any() else photo.tissue)
    d = np.abs(photo.rgb[ys, xs].astype(float) - np.array(photo.swatch)).sum(axis=1)
    i = int(np.argmin(d + 0.002 * ((ys - ys.mean()) ** 2 + (xs - xs.mean()) ** 2)))
    h, w = photo.rgb.shape[:2]
    return xs[i] / w, ys[i] / h


def square_thumb(photo: screening.Photo, point: tuple[float, float]) -> tuple[str, tuple[float, float]]:
    """Tissue crop padded to a transparent square, with the point re-expressed in the square."""
    h, w = photo.rgb.shape[:2]
    s = max(h, w)
    canvas, alpha = np.zeros((s, s, 3), np.uint8), np.zeros((s, s), np.uint8)
    oy, ox = (s - h) // 2, (s - w) // 2
    canvas[oy:oy + h, ox:ox + w] = photo.rgb
    alpha[oy:oy + h, ox:ox + w] = photo.tissue * 255
    return png_url(canvas, alpha), ((point[0] * w + ox) / s, (point[1] * h + oy) / s)


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
            "thumb": thumb, "thumb_point": thumb_pt, "checks": photo.checks,
            "typical": {k: _median_rgb(b[site][f"{k}_median"]) for k in ("healthy", "anaemic")}}


def _median_rgb(med: dict) -> tuple[int, int, int]:
    """Typical tissue colour of a training class: its median R, G, B."""
    return tuple(int(round(med[c])) for c in ("R_med", "G_med", "B_med"))


def reason_text(site: str, r: dict) -> str:
    high = r["pct"] >= 50
    pct = min(max(round(r["pct"]) if high else round(100 - r["pct"]), 1), 99)
    return ui.t(f"r_{r['group']}_{'high' if high else 'low'}", site=ui.t(f"noun_{site}"), pct=pct)


def noun(site: str) -> str:
    return ui.t(f"noun_{site}")
