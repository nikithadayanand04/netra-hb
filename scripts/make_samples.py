"""Six demo patients for the Screen page (app/samples/): per site one Refer and one Normal, each correctly classified
both out-of-fold and by the saved bundle through the app's own photo pipeline, passing the quality gate, with at
least 2 of its 3 reasons pointing the way of its label.
They come from the training sets, so they show the flow; they are not test results."""
import json
import shutil

import joblib
import numpy as np
import pandas as pd

import config
from netra import screening
from netra.masks import load_image

OUT = config.ROOT / "app" / "samples"
CSV = {"eye": config.FEATURES_CSV, "palm": config.GHANA_SITES["palm"]["csv"], "nail": config.GHANA_SITES["nail"]["csv"]}
# typical, varied out-of-fold scores (one per site and class), so the demo does not look staged
TARGET_P = {("eye", 1): 0.82, ("eye", 0): 0.12, ("palm", 1): 0.66, ("palm", 0): 0.28, ("nail", 1): 0.74, ("nail", 0): 0.20}


def source(site: str, row: pd.Series):
    if site == "eye":
        return config.DATA_DIR / f"{row['patient_id']}.png"
    return next(config.GHANA_SITES[site]["images"].rglob(row["file"]))


def run_app_pipeline(bundle: dict, path, site: str, label: int) -> tuple[float, bool] | None:
    """None unless the photo passes the checks and at least 2 of its 3 shown reasons point the way of its label,
    so a demo result can be explained in plain words."""
    rgb, alpha = load_image(path)
    tissue = screening.auto_tissue(rgb, alpha)
    photo = screening.analyse_photo(rgb, np.ones(rgb.shape[:2], bool) if tissue is None else tissue, site)
    if photo is None or not all(c["ok"] for c in photo.checks.values()):
        return None
    feats = screening.features(photo)
    if sum(r["agrees"] for r in screening.reasons(bundle, feats, bool(label))) < 2:
        return None
    return screening.probability(bundle, feats), tissue is None


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    samples = []
    for site, csv in CSV.items():
        bundle = joblib.load(config.OUT_DIR / "models" / f"screen_{site}.joblib")
        df = pd.read_csv(csv).reset_index(drop=True).assign(oof=bundle["oof_p"])
        thr = bundle["threshold"]
        for label in (1, 0):
            pool = df[(df.label == label) & ((df.oof >= thr) if label else (df.oof < thr))]
            pool = pool.iloc[np.argsort(np.abs(pool.oof.to_numpy() - TARGET_P[(site, label)]))]
            for _, row in pool.iterrows():
                got = run_app_pipeline(bundle, source(site, row), site, label)
                if got and (got[0] >= thr) == bool(label):
                    break
            else:
                raise RuntimeError(f"no usable {site} sample with label {label}")
            p, whole = got
            name = f"{site}_{'refer' if label else 'normal'}.png"
            shutil.copy(source(site, row), OUT / name)
            samples.append({"id": f"{site}_{'refer' if label else 'normal'}", "site": site, "file": name,
                            "age_band": "age_6_59m", "whole_image_is_tissue": whole,
                            "label": int(label), "hb": None if pd.isna(row.get("hb")) else float(row["hb"]),
                            "label_source": bundle["label_source"], "source_id": str(row.get("patient_id")),
                            "oof_p": float(row["oof"]), "app_p": p})
            print(f"  {name:<18} label {label}  OOF p {row['oof']:.2f}  app p {p:.2f}  (threshold {thr:.2f})")
    order = ["eye_refer", "palm_normal", "nail_refer", "eye_normal", "palm_refer", "nail_normal"]
    samples.sort(key=lambda s: order.index(s["id"]))
    (OUT / "samples.json").write_text(json.dumps({"note": __doc__, "samples": samples}, indent=2))


if __name__ == "__main__":
    main()
