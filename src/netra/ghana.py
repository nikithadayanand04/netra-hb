import re
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.sparse.csgraph import connected_components

import config
from netra import cleaning
from netra.features import feature_names, image_features
from netra.masks import load_image, make_mask
from netra.normalise import grey_world

# Prefix + number, optional stray "png" typo (Anemic-145png.png is an original), then anything else. Originals have
# nothing after the number; "(n)", "- Copy", FV/RA/R and " 1"-style suffixes are rotated or exact copies.
NAME = re.compile(r"^(?P<prefix>[A-Za-z]+(?:-[A-Za-z]+)*)-?(?P<num>\d+)(?:png)?(?P<rest>.*)\.png$")
SERIES = {
    "main": {"anemic", "non-anemic", "anemicp", "non-anemicp", "anemic-fn", "non-anrmic-fn"},
    "small": {"anemic-conj", "non-anemic-con", "anemic-pa", "non-anemic-pa", "anemic-fin", "non-anemic-fin"},
}


def parse_name(name: str) -> dict | None:
    m = NAME.match(name)
    if m is None:
        return None
    prefix = m["prefix"].lower()
    series = next((s for s, p in SERIES.items() if prefix in p), "extra")
    return {"label": int(not prefix.startswith("non")), "prefix": m["prefix"], "num": int(m["num"]),
            "series": series, "original": m["rest"] == ""}


def dihedral_hashes(rgb: np.ndarray, tissue: np.ndarray) -> np.ndarray:
    out = []
    for k in range(4):
        r, t = np.rot90(rgb, k), np.rot90(tissue, k)
        out += [cleaning.phash(np.ascontiguousarray(r), t), cleaning.phash(np.ascontiguousarray(r[:, ::-1]), t[:, ::-1])]
    return np.array(out)


def describe(path: Path) -> dict:
    rgb, alpha = load_image(path)
    m = make_mask(rgb, alpha)
    raw = image_features(rgb, m.mask, m.glare_frac)
    gw = image_features(grey_world(rgb, m.mask), m.mask, m.glare_frac)
    px = rgb[m.tissue] if m.tissue.any() else rgb.reshape(-1, 3)
    return {"file": path.name, **raw, **{f"gw_{k}": gw[k] for k in feature_names()},
            "median_rgb": np.median(px, axis=0), "hashes": dihedral_hashes(rgb, m.tissue)}


def scan(paths: list[Path]) -> pd.DataFrame:
    return pd.DataFrame(Parallel(n_jobs=-1)(delayed(describe)(p) for p in paths))


def originals(folder: Path) -> list[tuple[Path, dict]]:
    out = []
    for p in sorted(folder.glob("*.png")):
        info = parse_name(p.name)
        if info is not None and info["original"]:
            out.append((p, info))
    return out


def match_matrix(a: pd.DataFrame, b: pd.DataFrame, max_ham: int = config.GHANA_DUP_HAMMING,
                 max_colour: float = config.GHANA_DUP_COLOUR) -> np.ndarray:
    """a[i] ~ b[j] if some rotation/mirror of a[i] is within max_ham bits of b[j] and their median tissue colours
    differ by at most max_colour per channel."""
    Ha, Hb = np.stack(a["hashes"]), np.stack(b["hashes"])[:, 0]
    ham = np.min([(Ha[:, t, None, :] != Hb[None]).sum(-1) for t in range(Ha.shape[1])], axis=0)
    colour = np.abs(np.stack(a["median_rgb"])[:, None] - np.stack(b["median_rgb"])[None]).max(-1)
    return (ham <= max_ham) & (colour <= max_colour)


def duplicate_clusters(df: pd.DataFrame) -> np.ndarray:
    adj = match_matrix(df, df)
    return connected_components(adj | adj.T, directed=False)[1]


def group_and_clean(df: pd.DataFrame, site: str) -> pd.DataFrame:
    """One cv_group per duplicate cluster; clusters whose members carry both labels are dropped, as are images with
    too little tissue."""
    df = df.copy()
    df["cluster"] = duplicate_clusters(df)
    size = df.groupby("cluster")["file"].transform("size")
    df["cv_group"] = site + ":" + df.groupby("cluster")["file"].transform("first").str.removesuffix(".png")
    df["dup_conflict"] = df.groupby("cluster")["label"].transform("nunique") > 1
    df["low_tissue"] = df["tissue_px"] < config.MIN_PIXELS
    df["n_in_cluster"] = size
    reasons = np.where(df["dup_conflict"], "duplicate_conflicting_label", np.where(df["low_tissue"], "low_tissue", ""))
    df["drop_reason"] = reasons
    return df
