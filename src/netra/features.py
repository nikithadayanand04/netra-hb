import numpy as np
import pandas as pd
from skimage.color import rgb2lab
from sklearn.base import BaseEstimator, TransformerMixin

EPS = 1e-6
PCT_FEATURES = ("chrom_r", "lab_a", "a_over_L", "erythema_index", "hsv_s")
COLOUR_FEATURES = (
    "R", "G", "B", "chrom_r", "chrom_g", "chrom_b",
    "lab_L", "lab_a", "lab_b", "a_over_L", "hsv_h", "hsv_s", "hsv_v", "erythema_index",
)


def pixel_channels(px: np.ndarray) -> dict[str, np.ndarray]:
    px = px.astype(float)
    R, G, B = px[:, 0], px[:, 1], px[:, 2]
    tot = R + G + B + EPS
    lab = rgb2lab(np.clip(px, 0, 255)[None] / 255.0)[0]
    mx, mn = px.max(axis=1), px.min(axis=1)
    delta = mx - mn
    safe = np.maximum(delta, EPS)
    hue = np.select(
        [delta == 0, mx == R, mx == G],
        [0.0, ((G - B) / safe) % 6, (B - R) / safe + 2],
        (R - G) / safe + 4,
    ) * 60.0
    return {
        "R": R, "G": G, "B": B,
        "chrom_r": R / tot, "chrom_g": G / tot, "chrom_b": B / tot,
        "lab_L": lab[:, 0], "lab_a": lab[:, 1], "lab_b": lab[:, 2],
        "a_over_L": lab[:, 1] / np.maximum(lab[:, 0], 1.0),
        "hsv_h": (hue + 180) % 360 - 180,  # red-centred so the circular median is well defined
        "hsv_s": np.where(mx > 0, delta / np.maximum(mx, EPS), 0.0),
        "hsv_v": mx / 255.0,
        "erythema_index": np.log10(R + 1) - np.log10(G + 1),
    }


def feature_names() -> list[str]:
    names = [f"{c}_med" for c in COLOUR_FEATURES]
    names += [f"{c}_p{q}" for c in PCT_FEATURES for q in (10, 90)]
    return names


def colour_features(rgb: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    px = rgb[mask]
    if len(px) == 0:
        return {n: np.nan for n in feature_names()}
    ch = pixel_channels(px)
    out = {f"{c}_med": float(np.median(ch[c])) for c in COLOUR_FEATURES}
    for c in PCT_FEATURES:
        p10, p90 = np.percentile(ch[c], [10, 90])
        out[f"{c}_p10"], out[f"{c}_p90"] = float(p10), float(p90)
    return out


def image_features(rgb: np.ndarray, mask: np.ndarray, glare_frac: float) -> dict[str, float]:
    return {**colour_features(rgb, mask), "tissue_px": int(mask.sum()), "glare_frac": glare_frac}


def _base(feature: str) -> str:
    return feature.rsplit("_", 1)[0]


def prune_redundant(X: pd.DataFrame, preference: list[str], thresh: float) -> tuple[list[str], list[tuple[str, str, float]]]:
    rank = {b: i for i, b in enumerate(preference)}
    corr = X.corr(method="spearman").abs()
    pairs = corr.where(np.triu(np.ones(corr.shape, bool), 1)).stack().dropna()
    keep, dropped = list(X.columns), []
    for (a, b), r in pairs[pairs > thresh].sort_values(ascending=False).items():
        if a in keep and b in keep:
            loser = max(a, b, key=lambda f: (rank.get(_base(f), len(rank)), f))
            keep.remove(loser)
            dropped.append((loser, b if loser == a else a, float(r)))
    return keep, dropped


class RedundancyPruner(TransformerMixin, BaseEstimator):
    """prune_redundant as a pipeline step, so the kept columns are chosen from training-fold rows only."""

    def __init__(self, columns=(), preference=(), thresh: float = 0.95, always_drop=()):
        self.columns = columns
        self.preference = preference
        self.thresh = thresh
        self.always_drop = always_drop

    def fit(self, X, y=None) -> "RedundancyPruner":
        cols = list(self.columns)
        keep, _ = prune_redundant(pd.DataFrame(np.asarray(X, float), columns=cols), list(self.preference), self.thresh)
        self.keep_ = [c for c in keep if c not in self.always_drop]
        self.idx_ = [cols.index(c) for c in self.keep_]
        return self

    def transform(self, X):
        return np.asarray(X, float)[:, self.idx_]
