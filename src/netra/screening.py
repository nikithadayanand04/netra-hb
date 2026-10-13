"""One photo in, one screening result out, using the saved bundles from scripts.build_screen_models."""
from dataclasses import dataclass

import cv2
import numpy as np

import config
from netra.cleaning import photo_checks
from netra.features import colour_features
from netra.masks import glare_mask

# Plain-language reason groups: (input columns substituted together, the feature its sentence describes)
REASON_GROUPS = {
    "redness": (["lab_a_med", "lab_a_p10", "lab_a_p90", "a_over_L_med", "a_over_L_p10", "a_over_L_p90"], "lab_a_med"),
    "lightness": (["lab_L_med", "R_med", "G_med", "B_med"], "lab_L_med"),
    "blood_index": (["erythema_index_med", "erythema_index_p10", "erythema_index_p90"], "erythema_index_med"),
    "red_share": (["chrom_r_med", "chrom_r_p10", "chrom_r_p90", "chrom_g_med", "chrom_b_med"], "chrom_r_med"),
    "tone": (["lab_b_med", "hsv_h_med", "hsv_s_med", "hsv_s_p10", "hsv_s_p90"], "lab_b_med"),
}

# WHO severity: (mild lower bound, moderate lower bound, severe below) per cut-off in g/dL
SEVERITY = {11.0: (10.0, 7.0), 11.5: (11.0, 8.0), 12.0: (11.0, 8.0), 13.0: (11.0, 8.0)}


@dataclass
class Photo:
    rgb: np.ndarray        # tissue crop, downscaled to SCREEN_LONG_SIDE
    tissue: np.ndarray
    mask: np.ndarray       # tissue minus glare minus makeup/lashes: the pixels that are measured
    glare_frac: float
    makeup: np.ndarray     # removed as makeup or lashes
    makeup_frac: float
    checks: dict
    swatch: tuple[int, int, int]


def auto_tissue(rgb: np.ndarray, alpha: np.ndarray | None) -> np.ndarray | None:
    """Tissue from a transparent or black background; None means the user has to click the tissue."""
    if alpha is not None and (alpha < 255).any():
        return alpha > 0
    dark = rgb.max(axis=2) < config.BLACK_THRESH
    return ~dark if 0.05 < dark.mean() < 0.95 else None


def grow_region(rgb: np.ndarray, x: int, y: int) -> np.ndarray:
    """Pixels connected to (x, y) whose Lab colour is within REGION_TOL of it, inside a disc around the click."""
    h, w = rgb.shape[:2]
    lab = cv2.cvtColor(cv2.GaussianBlur(np.ascontiguousarray(rgb, np.uint8), (5, 5), 0), cv2.COLOR_RGB2LAB)
    ff = np.zeros((h + 2, w + 2), np.uint8)
    tol = (config.REGION_TOL,) * 3
    cv2.floodFill(lab.copy(), ff, (int(x), int(y)), 0, tol, tol, 4 | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY
                  | (255 << 8))
    region = ff[1:-1, 1:-1] > 0
    yy, xx = np.ogrid[:h, :w]
    region &= (xx - x) ** 2 + (yy - y) ** 2 <= (config.REGION_RADIUS * min(h, w)) ** 2
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    region = cv2.morphologyEx(region.astype(np.uint8), cv2.MORPH_OPEN, k)
    region = cv2.morphologyEx(region, cv2.MORPH_CLOSE, k)
    n, lbl = cv2.connectedComponents(region)
    return lbl == lbl[int(y), int(x)] if n > 1 and lbl[int(y), int(x)] > 0 else region > 0


def box_region(shape: tuple[int, ...], x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    h, w = shape[:2]
    xa, xb = sorted((int(np.clip(x1, 0, w - 1)), int(np.clip(x2, 0, w - 1))))
    ya, yb = sorted((int(np.clip(y1, 0, h - 1)), int(np.clip(y2, 0, h - 1))))
    region = np.zeros((h, w), bool)
    region[ya:yb + 1, xa:xb + 1] = True
    return region


def makeup_mask(rgb: np.ndarray) -> np.ndarray:
    """Kajal, mascara and lashes: very dark and low in saturation (pink conjunctiva is neither)."""
    x = rgb.astype(float)
    mx, mn = x.max(axis=2), x.min(axis=2)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0.0)
    return (mx / 255.0 < config.MAKEUP_V_MAX) & (s < config.MAKEUP_S_MAX)


def crop_to_tissue(rgb: np.ndarray, tissue: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ys, xs = np.nonzero(tissue)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    rgb, tissue = rgb[sl], tissue[sl]
    scale = config.SCREEN_LONG_SIDE / max(rgb.shape[:2])
    if scale < 1:
        size = (max(1, round(rgb.shape[1] * scale)), max(1, round(rgb.shape[0] * scale)))
        rgb = cv2.resize(rgb, size, interpolation=cv2.INTER_AREA)
        tissue = cv2.resize(tissue.astype(np.uint8), size, interpolation=cv2.INTER_NEAREST) > 0
    return np.ascontiguousarray(rgb), tissue


def analyse_photo(rgb: np.ndarray, tissue: np.ndarray, site: str = "eye") -> Photo | None:
    if tissue.sum() < 50:
        return None
    rgb, tissue = crop_to_tissue(rgb, tissue)
    glare = glare_mask(rgb) & tissue
    makeup = makeup_mask(rgb) & tissue & ~glare
    n = int(tissue.sum())
    glare_frac = float(glare.sum() / n) if n else 0.0
    makeup_frac = float(makeup.sum() / n) if n else 0.0
    mask = tissue & ~glare & ~makeup
    checks = photo_checks(rgb, tissue & ~makeup, glare_frac, config.BLUR_VAR_MIN_SITE[site])
    if site == "eye":
        checks["makeup"] = {"value": makeup_frac, "ok": bool(makeup_frac <= config.MAKEUP_WARN_FRAC)}
    if mask.sum() < 50:
        return None
    sw = np.median(rgb[mask], axis=0)
    return Photo(rgb, tissue, mask, glare_frac, makeup, makeup_frac, checks, tuple(int(c) for c in sw))


def features(photo: Photo) -> dict[str, float]:
    return colour_features(photo.rgb, photo.mask)


def probability(bundle: dict, feats: dict[str, float]) -> float:
    x = np.array([[feats[c] for c in bundle["input_columns"]]], float)
    return float(bundle["model"].predict_proba(x)[0, 1])


def familiarity(bundle: dict, feats: dict[str, float]) -> dict:
    """KNN check: mean distance from this photo to its NN_K nearest training photos (scaled features) against the
    NN_PCT percentile of the same distance among the training photos themselves."""
    ref = bundle["nn"]
    x = (np.array([feats[c] for c in bundle["input_columns"]], float) - ref["mean"]) / ref["scale"]
    d = np.sort(np.sqrt(((ref["X"] - x) ** 2).sum(axis=1)))[:config.NN_K].mean()
    return {"distance": float(d), "threshold": float(ref["threshold"]), "unfamiliar": bool(d > ref["threshold"])}


def uncertainty_band(bundle: dict, p: float) -> tuple[float, float]:
    """95% Wilson interval of the true anaemia rate among the out-of-fold patients with the nearest scores."""
    oof_p, oof_y = np.asarray(bundle["oof_p"]), np.asarray(bundle["oof_y"])
    near = np.argsort(np.abs(oof_p - p))[:config.BAND_NEIGHBOURS]
    k, n, z = oof_y[near].sum(), len(near), 1.96
    phat = k / n
    mid = (phat + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return float(max(mid - half, 0.0)), float(min(mid + half, 1.0))


def hb_knots(eye_bundle: dict) -> tuple[np.ndarray, np.ndarray]:
    pk, hk = (np.asarray(v, float) for v in eye_bundle["hb_knots"])
    return pk, hk - 1e-3 * np.arange(len(hk))   # strictly decreasing, so position < 11 exactly when p > threshold


def strip_position(p: float, threshold: float, knots: tuple[np.ndarray, np.ndarray]) -> float:
    """Colour-implied Hb on the strip, shifted so the model's own threshold lands on 11 g/dL (the training cut-off).
    For other age bands the result is refer when this position is below that band's cut-off."""
    pk, hk = knots
    return float(np.interp(p, pk, hk) - np.interp(threshold, pk, hk) + 11.0)


def severity(position: float, cutoff: float) -> str:
    if position >= cutoff:
        return "none"
    mild, moderate = SEVERITY[cutoff]
    return "mild" if position >= mild else "moderate" if position >= moderate else "severe"


def reasons(bundle: dict, feats: dict[str, float], refer: bool, n: int = 3) -> list[dict]:
    """Rank reason groups by how much the probability moves when that group is set to the healthy median, listing
    first the groups whose value points the same way as the result; each reason carries the patient's percentile
    among healthy children for its feature."""
    cols = bundle["input_columns"]
    base = probability(bundle, feats)
    rows = []
    for name, (group, feat) in REASON_GROUPS.items():
        alt = {**feats, **{c: bundle["healthy_median"][c] for c in group if c in cols}}
        delta = base - probability(bundle, alt)
        pct = float(np.interp(feats[feat], bundle["quantiles"][feat], np.arange(101)))
        anaemic_low = bundle["anaemic_median"][feat] < bundle["healthy_median"][feat]
        rows.append({"group": name, "feature": feat, "delta": delta, "pct": pct, "anaemic_low": anaemic_low})
    sign = 1 if refer else -1
    for r in rows:   # does this child's value sit on the anaemic side of the healthy median, as the result says?
        r["agrees"] = ((r["pct"] < 50) == r["anaemic_low"]) == refer
    rows.sort(key=lambda r: (not r["agrees"], -sign * r["delta"]))   # agreeing reasons first, then by effect
    return rows[:n]
