import json
import subprocess

import numpy as np
import pandas as pd

import config
from netra.features import feature_names
from netra.ghana import group_and_clean, match_matrix, originals, scan
from scripts.extract_features import image_path, load_meta

META_COLS = ["patient_id", "cv_group", "dataset", "label", "label_source", "series", "num", "file"]


def ensure_extracted(spec: dict) -> None:
    """Unpack the original RAR next to it (data/<site>/extracted); the archive itself is only read."""
    if spec["images"].exists() or "archive" not in spec:
        return
    spec["images"].parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["bsdtar", "-xf", str(spec["archive"]), "-C", str(spec["images"].parent)], check=True)


def site_frame(site: str, spec: dict) -> pd.DataFrame:
    ensure_extracted(spec)
    found = originals(spec["images"])
    df = scan([p for p, _ in found])
    info = pd.DataFrame([i for _, i in found])
    df = pd.concat([info, df], axis=1)
    df["site"] = site
    return group_and_clean(df, site)


def cp_crosswalk(eye: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Which Ghana eye originals are CP-AnemiC images, and how often the Ghana folder label equals the WHO Hb label."""
    meta = load_meta()
    cp = scan([image_path(pid) for pid in meta["patient_id"]])
    cp["cp_id"] = meta["patient_id"].values
    hit = match_matrix(cp, eye)
    rows = [{"cp_id": cp["cp_id"][i], "ghana_file": eye["file"].iloc[j], "ghana_label": int(eye["label"].iloc[j])}
            for i, j in zip(*np.nonzero(hit))]
    cw = pd.DataFrame(rows).merge(meta[["patient_id", "hb", "label"]].rename(
        columns={"patient_id": "cp_id", "label": "who_label"}), on="cp_id")
    per_cp = cw.groupby("cp_id").agg(ghana=("ghana_label", "unique"), who=("who_label", "first"))
    unambiguous = per_cp[per_cp["ghana"].str.len() == 1].assign(ghana=lambda d: d["ghana"].str[0])
    agree = (unambiguous["ghana"] == unambiguous["who"])
    cm = pd.crosstab(unambiguous["who"], unambiguous["ghana"])
    stats = {"cp_images": int(len(meta)), "cp_images_matched": int(len(per_cp)),
             "matched_with_one_label": int(len(unambiguous)), "agree": int(agree.sum()),
             "agreement": float(agree.mean()), "label_noise_estimate": float(1 - agree.mean()),
             "confusion_who_rows_ghana_cols": {f"who_{r}": {f"ghana_{c}": int(cm.loc[r, c]) for c in cm.columns}
                                               for r in cm.index},
             "disagreements": unambiguous[~agree].reset_index()[["cp_id", "ghana", "who"]].to_dict("records"),
             "note": "Ghana file-name label vs WHO label (Hb < 11 g/dL) on CP-AnemiC images that also appear in "
                     "ghana_eye; used as the label-noise estimate for the folder-labelled Ghana sets."}
    return cw, stats


def main() -> None:
    logs, summary = [], {}
    for site, spec in config.GHANA_SITES.items():
        df = site_frame(site, spec)
        if site == "eye_extra":
            cw, agreement = cp_crosswalk(df)
            cw.to_csv(config.OUT_DIR / "ghana_cp_crosswalk.csv", index=False)
            overlap = df.loc[df["file"].isin(cw["ghana_file"]), "cluster"].unique()
            df["cp_overlap"] = df["cluster"].isin(overlap)
            df["drop_reason"] = np.where(df["cp_overlap"] & (df["drop_reason"] == ""), "in_cp_anemic", df["drop_reason"])
            summary["label_agreement"] = agreement
        df["kept"] = df["drop_reason"] == ""
        logs.append(df.drop(columns=["hashes", "median_rgb"] + feature_names()
                            + [f"gw_{f}" for f in feature_names()]))
        kept = df[df["kept"]].reset_index(drop=True)
        kept["patient_id"] = site + ":" + kept["file"].str.removesuffix(".png")
        kept["dataset"] = f"ghana_{site}"
        kept["label_source"] = "folder"
        out = kept[META_COLS + feature_names() + [f"gw_{f}" for f in feature_names()]]
        out.to_csv(spec["csv"], index=False)
        summary[site] = {"originals": int(len(df)), "duplicate_clusters": int((df.groupby("cluster").size() > 1).sum()),
                         "dropped": df["drop_reason"].value_counts().drop("", errors="ignore").to_dict(),
                         "kept_images": int(len(out)), "cv_groups": int(out["cv_group"].nunique()),
                         "anaemic": int(out["label"].sum()), "normal": int((out["label"] == 0).sum())}
        s = summary[site]
        print(f"{site:<9} originals {s['originals']}  dup clusters {s['duplicate_clusters']}  dropped {s['dropped']}  "
              f"kept {s['kept_images']} images / {s['cv_groups']} groups  ({s['anaemic']} anaemic / {s['normal']} normal)")
    pd.concat(logs, ignore_index=True).to_csv(config.GHANA_LOG, index=False)
    a = summary["label_agreement"]
    print(f"CP-AnemiC in ghana_eye: {a['cp_images_matched']}/{a['cp_images']} CP images matched; folder vs WHO label "
          f"agreement {a['agree']}/{a['matched_with_one_label']} = {a['agreement']:.1%}")
    (config.OUT_DIR / "results").mkdir(parents=True, exist_ok=True)
    (config.OUT_DIR / "results" / "ghana_data.json").write_text(json.dumps(summary, indent=2, default=int))
    print(f"saved {[str(s['csv'].name) for s in config.GHANA_SITES.values()]}, {config.GHANA_LOG.name}, "
          "ghana_cp_crosswalk.csv, results/ghana_data.json")


if __name__ == "__main__":
    main()
