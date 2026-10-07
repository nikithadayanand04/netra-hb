import cv2
import numpy as np
import pandas as pd

import config


def laplacian_var(rgb: np.ndarray, tissue: np.ndarray, erode_px: int = 2) -> float:
    k = np.ones((2 * erode_px + 1, 2 * erode_px + 1), np.uint8)
    inner = cv2.erode(tissue.astype(np.uint8), k) > 0
    if inner.sum() < 10:
        return float("nan")
    grey = cv2.cvtColor(np.ascontiguousarray(rgb, dtype=np.uint8), cv2.COLOR_RGB2GRAY).astype(float)
    return float(cv2.Laplacian(grey, cv2.CV_64F)[inner].var())


def pixel_eq_frac(rgb: np.ndarray, tissue: np.ndarray) -> float:
    both = tissue[:, 1:] & tissue[:, :-1]
    if both.sum() == 0:
        return float("nan")
    eq = np.all(rgb[:, 1:] == rgb[:, :-1], axis=2) & both
    return float(eq.sum() / both.sum())


def _tissue_crop(rgb: np.ndarray, tissue: np.ndarray, size: int) -> np.ndarray:
    ys, xs = np.nonzero(tissue)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    img = np.where(tissue[..., None], rgb, 0)[sl].astype(np.uint8)
    return cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)


def phash(rgb: np.ndarray, tissue: np.ndarray) -> np.ndarray:
    grey = cv2.cvtColor(_tissue_crop(rgb, tissue, 32), cv2.COLOR_RGB2GRAY).astype(np.float32)
    low = cv2.dct(grey)[:8, :8].flatten()
    return low > np.median(low[1:])


def thumbnail(rgb: np.ndarray, tissue: np.ndarray) -> np.ndarray:
    return _tissue_crop(rgb, tissue, 64).astype(float)


def quality_row(rgb: np.ndarray, tissue: np.ndarray, glare_frac: float) -> dict:
    return {
        "tissue_px": int(tissue.sum()),
        "glare_frac": glare_frac,
        "lap_var": laplacian_var(rgb, tissue),
        "pixel_eq_frac": pixel_eq_frac(rgb, tissue),
    }


def find_duplicates(ids: list[str], hashes: list[np.ndarray], thumbs: list[np.ndarray]) -> pd.DataFrame:
    n = len(ids)
    H = np.array(hashes)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    pairs = []
    for i in range(n):
        ham = (H[i + 1:] != H[i]).sum(axis=1)
        for j in np.nonzero(ham <= config.DUP_HAMMING)[0] + i + 1:
            mae = float(np.abs(thumbs[i] - thumbs[j]).mean())
            if mae < config.DUP_MAE:
                pairs.append((ids[i], ids[j], int(ham[j - i - 1]), mae))
                parent[find(j)] = find(i)
    roots = [find(i) for i in range(n)]
    first = {}
    dup_of = []
    for i, r in enumerate(roots):
        dup_of.append(ids[first[r]] if r in first else "")
        first.setdefault(r, i)
    sizes = pd.Series(roots).map(pd.Series(roots).value_counts())
    groups = {r: k for k, r in enumerate(sorted(set(r for r, s in zip(roots, sizes) if s > 1)))}
    out = pd.DataFrame({
        "id": ids,
        "dup_group": [groups.get(r, -1) for r in roots],
        "dup_of": dup_of,
    })
    out.attrs["pairs"] = pairs
    return out


def add_flags(log: pd.DataFrame) -> pd.DataFrame:
    log = log.copy()
    log["flag_low_tissue"] = log["tissue_px"] < config.MIN_PIXELS
    log["flag_high_glare"] = log["glare_frac"] > config.GLARE_MAX_FRAC
    log["flag_blur"] = log["lap_var"] < config.BLUR_VAR_MIN
    log["flag_upscaled"] = log["pixel_eq_frac"] > config.PIXEL_EQ_MAX
    log["flag_duplicate"] = log["dup_of"] != ""
    grp = log[log["dup_group"] >= 0].groupby("dup_group")
    conflict = (grp["label"].nunique() > 1) | (grp["hb"].agg(np.ptp) > config.DUP_HB_TOL)
    log["dup_conflict"] = log["dup_group"].map(conflict).fillna(False).astype(bool)
    reasons = {"low_tissue": log["flag_low_tissue"], "duplicate_conflicting_hb": log["dup_conflict"]}
    log["drop_reason"] = [
        ";".join(r for r, m in reasons.items() if m.iloc[i]) for i in range(len(log))
    ]
    log["drop"] = log["drop_reason"] != ""
    log["exclude_reason"] = [
        ";".join(q for q in config.QUALITY_EXCLUDE if log[f"flag_{q}"].iloc[i]) for i in range(len(log))
    ]
    log["exclude"] = log["drop"] | (log["exclude_reason"] != "")
    return log
