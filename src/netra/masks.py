from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

import config


@dataclass
class MaskResult:
    mask: np.ndarray        # tissue minus glare
    tissue: np.ndarray      # tissue incl. glare
    glare_frac: float       # glare pixels / tissue pixels


def load_image(path: str | Path) -> tuple[np.ndarray, np.ndarray | None]:
    im = Image.open(path)
    has_alpha = im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info)
    if has_alpha:
        arr = np.asarray(im.convert("RGBA"))
        return arr[..., :3].copy(), arr[..., 3].copy()
    return np.asarray(im.convert("RGB")).copy(), None


def tissue_mask(rgb: np.ndarray, alpha: np.ndarray | None, black_thresh: int = config.BLACK_THRESH) -> np.ndarray:
    if alpha is not None and (alpha < 255).any():
        return alpha > 0
    return rgb.max(axis=2) >= black_thresh


def glare_mask(rgb: np.ndarray, v_thresh: float = config.GLARE_V, s_thresh: float = config.GLARE_S) -> np.ndarray:
    x = rgb.astype(float)
    mx, mn = x.max(axis=2), x.min(axis=2)
    v = mx / 255.0
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0.0)
    return (v > v_thresh) & (s < s_thresh)


def make_mask(rgb: np.ndarray, alpha: np.ndarray | None = None) -> MaskResult:
    tissue = tissue_mask(rgb, alpha)
    glare = glare_mask(rgb) & tissue
    n = int(tissue.sum())
    return MaskResult(mask=tissue & ~glare, tissue=tissue, glare_frac=float(glare.sum() / n) if n else 0.0)
