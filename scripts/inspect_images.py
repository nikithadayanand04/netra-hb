from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

import config

WHO_CUTOFF = 11.0


def load_meta() -> pd.DataFrame:
    df = pd.read_excel(config.METADATA_FILE, sheet_name=config.METADATA_SHEET)
    df["path"] = df[config.ID_COL].map(lambda s: config.DATA_DIR / f"{s}.png")
    df["anaemic"] = df[config.HB_COL] < WHO_CUTOFF
    return df


def image_stats(path) -> dict:
    im = Image.open(path)
    arr = np.asarray(im.convert("RGBA"))
    rgb, alpha = arr[..., :3].astype(int), arr[..., 3]
    transparent = alpha == 0
    black = (rgb.max(axis=2) < config.BLACK_THRESH) & ~transparent
    tissue = ~(transparent | black)
    hsv = np.asarray(im.convert("RGB").convert("HSV")).astype(float) / 255
    glare = (hsv[..., 2] > config.GLARE_V) & (hsv[..., 1] < config.GLARE_S) & tissue
    return {
        "mode": im.mode,
        "w": im.width,
        "h": im.height,
        "transparent_frac": transparent.mean(),
        "black_frac": black.mean(),
        "tissue_frac": tissue.mean(),
        "tissue_px": int(tissue.sum()),
        "glare_frac_of_tissue": glare.sum() / max(tissue.sum(), 1),
    }


def sample_grid(df: pd.DataFrame, out) -> None:
    rng = np.random.default_rng(config.SEED)
    picks = []
    for flag in (True, False):
        sub = df[df["anaemic"] == flag]
        picks.append(sub.iloc[rng.choice(len(sub), 6, replace=False)])
    sel = pd.concat(picks)
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    for ax, (_, r) in zip(axes.flat, sel.iterrows()):
        im = Image.open(r["path"]).convert("RGBA")
        ax.imshow(im)
        ax.set_facecolor("#7f7fff")
        tag = "ANAEMIC" if r["anaemic"] else "normal"
        ax.set_title(f"{r[config.ID_COL]}  Hb={r[config.HB_COL]:.1f}  {tag}  {im.width}x{im.height}", fontsize=9)
        ax.set_xticks([]), ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(out, dpi=120)


def main() -> None:
    df = load_meta()
    stats = pd.DataFrame([image_stats(p) for p in df["path"]])
    df = pd.concat([df, stats], axis=1)
    print("n images:", len(df), "| anaemic (Hb<11):", int(df["anaemic"].sum()))
    print("colour modes:", dict(Counter(df["mode"])))
    print("\nresolution (w x h) top 10:")
    print(df.groupby(["w", "h"]).size().sort_values(ascending=False).head(10).to_string())
    print("\n", df[["w", "h", "transparent_frac", "black_frac", "tissue_frac", "tissue_px", "glare_frac_of_tissue"]]
          .describe(percentiles=[0.05, 0.5, 0.95]).round(3).to_string())
    print("\nimages with tissue_px <", config.MIN_PIXELS, ":", int((df["tissue_px"] < config.MIN_PIXELS).sum()))
    print("images with glare >1% of tissue:", int((df["glare_frac_of_tissue"] > 0.01).sum()))
    out = config.OUT_DIR / "figures" / "samples.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sample_grid(df, out)
    print("saved", out)


if __name__ == "__main__":
    main()
