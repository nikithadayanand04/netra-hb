import numpy as np
import pandas as pd

import config
from netra import cleaning
from netra.features import feature_names, image_features
from netra.labels import label_frame
from netra.masks import load_image, make_mask
from netra.normalise import grey_world


def find_col(df: pd.DataFrame, given: str | None, keys: tuple[str, ...]) -> str | None:
    if given:
        return given
    return next((c for c in df.columns if any(k in c.lower() for k in keys)), None)


def load_meta() -> pd.DataFrame:
    df = pd.read_excel(config.METADATA_FILE, sheet_name=config.METADATA_SHEET)
    age_col = find_col(df, config.AGE_COL, ("age",))
    sex_col = find_col(df, config.SEX_COL, ("sex", "gender"))
    labels = label_frame(
        df[config.HB_COL],
        df[age_col] if age_col else None,
        df[sex_col] if sex_col else None,
        config.AGE_IN_MONTHS,
        config.DEFAULT_AGE_MONTHS,
    )
    return pd.DataFrame({
        "patient_id": df[config.ID_COL].astype(str),
        "dataset": config.DATASET_NAME,
        "hb": df[config.HB_COL].astype(float),
        **labels,
    })


def image_path(stem: str):
    for ext in config.IMAGE_EXTS:
        p = config.DATA_DIR / f"{stem}{ext}"
        if p.exists():
            return p
    raise FileNotFoundError(stem)


def main() -> None:
    meta = load_meta()
    feats, quality, hashes, thumbs = [], [], [], []
    for pid in meta["patient_id"]:
        rgb, alpha = load_image(image_path(pid))
        m = make_mask(rgb, alpha)
        raw = image_features(rgb, m.mask, m.glare_frac)
        gw = image_features(grey_world(rgb, m.mask), m.mask, m.glare_frac)
        feats.append({**raw, **{f"gw_{k}": gw[k] for k in feature_names()}})
        quality.append({"id": pid, **cleaning.quality_row(rgb, m.tissue, m.glare_frac)})
        hashes.append(cleaning.phash(rgb, m.tissue))
        thumbs.append(cleaning.thumbnail(rgb, m.tissue))

    dups = cleaning.find_duplicates(list(meta["patient_id"]), hashes, thumbs)
    log = pd.DataFrame(quality).merge(dups, on="id")
    log.insert(1, "hb", meta["hb"].values)
    log.insert(2, "label", meta["label"].values)
    log = cleaning.add_flags(log)

    df = pd.concat([meta.reset_index(drop=True), pd.DataFrame(feats)], axis=1)
    df = df[~log["drop"].values].reset_index(drop=True)

    config.OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.FEATURES_CSV, index=False)
    log.to_csv(config.OUT_DIR / "cleaning_log.csv", index=False)
    summarise(meta, df, log, dups.attrs["pairs"])


def summarise(meta: pd.DataFrame, df: pd.DataFrame, log: pd.DataFrame, pairs: list) -> None:
    print(f"images: {len(meta)}  kept: {len(df)}  dropped: {int(log['drop'].sum())}")
    for _, r in log[log["drop"]].iterrows():
        print(f"  dropped {r['id']} (hb={r['hb']}): {r['drop_reason']}")
    n_pos = int(df["label"].sum())
    print(f"class balance: anaemic {n_pos} ({n_pos / len(df):.1%}) / normal {len(df) - n_pos}")
    print(f"severity: {df['severity'].value_counts().to_dict()}")
    print(f"MODEL_FEATURES: {len(config.MODEL_FEATURES)} (excludes glare_frac, tissue_px, quality flags)")
    flags = [c for c in log.columns if c.startswith("flag_")]
    print("flags:", {c[5:]: int(log[c].sum()) for c in flags})
    print("flag rate by label:")
    print(log.groupby("label")[flags].mean().round(3).to_string())
    for a, b, ham, mae in pairs:
        ha, hb = log.set_index("id").loc[[a, b], "hb"]
        print(f"  duplicate: {a} ~ {b}  hamming={ham} mae={mae:.1f}  hb={ha} vs {hb}")
    print(f"features: {len([c for c in df.columns if c not in meta.columns])} columns -> {config.FEATURES_CSV}")
    num = df.drop(columns=list(meta.columns)).select_dtypes("number")
    rho = num.corrwith(df["hb"], method="spearman").dropna()
    top = rho.reindex(rho.abs().sort_values(ascending=False).index).head(10)
    print("\ntop 10 |Spearman rho| with Hb:")
    print(top.round(3).to_string())


if __name__ == "__main__":
    main()
