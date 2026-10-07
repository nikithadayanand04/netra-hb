import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve

import config
from netra.evaluate import METRICS, cross_validate
from netra.models import IMBALANCE, LABELS, build_models

RESULTS = config.OUT_DIR / "results"
FIG_DIR = config.OUT_DIR / "figures" / "baselines"
CLEANING_LOG = config.OUT_DIR / "cleaning_log.csv"
SURFACE, INK, INK_2, GRID, SERIES = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"

EXPERIMENTS = {
    "main": {"features": config.MODEL_FEATURES, "subset": "all",
             "note": "Headline baselines: all kept images, MODEL_FEATURES."},
    "unflagged": {"features": config.MODEL_FEATURES, "subset": "unflagged",
                  "note": "Sensitivity check: drops images with any quality flag (blur, upscaled, high glare)."},
    "shortcut_ablation": {"features": config.MODEL_FEATURES + config.EXCLUDED_FEATURES, "subset": "all",
                          "note": "NOT THE REAL MODEL. Adds glare_frac and tissue_px (image-acquisition shortcuts) "
                                  "to show how much they inflate scores."},
}


def load() -> pd.DataFrame:
    df = pd.read_csv(config.FEATURES_CSV)
    log = pd.read_csv(CLEANING_LOG).set_index("id")
    flags = [c for c in log.columns if c.startswith("flag_")]
    df["flagged"] = df["patient_id"].map(log[flags].any(axis=1)).astype(bool)
    return df


def run_experiment(df: pd.DataFrame, features: list[str]) -> tuple[dict, pd.DataFrame]:
    X, y, groups = df[features].to_numpy(float), df["label"].to_numpy(), df["patient_id"].to_numpy()
    results, oof = {}, []
    for name, pipe in build_models().items():
        res = cross_validate(pipe, X, y, groups)
        results[name] = {"label": LABELS[name], "imbalance": IMBALANCE[name], **res.summary()}
        oof.append(pd.DataFrame({"patient_id": groups, "hb": df["hb"].to_numpy(), "label": y,
                                 "model": name, "fold": res.fold, "proba": res.proba}))
        auc = res.pooled["roc_auc"]
        print(f"  {name:<18} ROC-AUC {auc:.3f}  sens {res.pooled['sensitivity']:.3f}  "
              f"spec {res.pooled['specificity']:.3f}")
    return results, pd.concat(oof, ignore_index=True)


def table(all_results: dict) -> pd.DataFrame:
    rows = []
    for exp, block in all_results.items():
        for name, r in block["models"].items():
            row = {"experiment": exp, "model": r["label"], "imbalance": r["imbalance"]}
            for m in METRICS:
                p = r["pooled"][m]
                row[m] = p["value"]
                row[f"{m}_ci"] = f"{p['ci_low']:.2f}-{p['ci_high']:.2f}"
            row.update(r["confusion_matrix"])
            rows.append(row)
    return pd.DataFrame(rows)


def _style(ax) -> None:
    ax.set_facecolor(SURFACE)
    ax.grid(color=GRID, lw=0.6)
    ax.tick_params(labelsize=7, colors=INK_2, length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_aspect("equal")


def plot_curves(oof: pd.DataFrame, results: dict, kind: str, path) -> None:
    names = [n for n in results if n != "all_normal"]
    ncol = 4
    nrow = int(np.ceil(len(names) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(10, 2.7 * nrow), dpi=200, facecolor=SURFACE)
    prevalence = oof.drop_duplicates("patient_id")["label"].mean()
    for ax, name in zip(axes.flat, names):
        d = oof[oof["model"] == name]
        _style(ax)
        if kind == "roc":
            fpr, tpr, _ = roc_curve(d["label"], d["proba"])
            ax.plot([0, 1], [0, 1], color=INK_2, lw=1, ls=(0, (3, 3)))
            ax.plot(fpr, tpr, color=SERIES, lw=2, solid_capstyle="round")
            p = results[name]["pooled"]["roc_auc"]
            head = f"AUC {p['value']:.2f} [{p['ci_low']:.2f}–{p['ci_high']:.2f}]"
        else:
            prec, rec, _ = precision_recall_curve(d["label"], d["proba"])
            ax.axhline(prevalence, color=INK_2, lw=1, ls=(0, (3, 3)))
            ax.plot(rec[:-1], prec[:-1], color=SERIES, lw=2, drawstyle="steps-post")   # drop the (0, 1) sentinel
            p = results[name]["pooled"]["pr_auc"]
            head = f"AP {p['value']:.2f} [{p['ci_low']:.2f}–{p['ci_high']:.2f}]"
        ax.set_title(f"{LABELS[name]}\n{head}", loc="left", fontsize=8, color=INK)
    for ax in axes.flat[len(names):]:
        ax.set_visible(False)
    xl, yl = ("False positive rate (1 − specificity)", "Sensitivity") if kind == "roc" else \
        ("Recall (sensitivity)", "Precision")
    ref = "diagonal = chance" if kind == "roc" else f"dashed = prevalence {prevalence:.2f} (all-normal / chance)"
    fig.supxlabel(xl, fontsize=9, color=INK_2)
    fig.supylabel(yl, fontsize=9, color=INK_2)
    fig.suptitle(f"{'ROC' if kind == 'roc' else 'Precision–recall'} curves, out-of-fold, patient-grouped 5-fold CV "
                 f"(n={oof['patient_id'].nunique()}; {ref}; 95% bootstrap CI)",
                 x=0.01, ha="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    df = load()
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    all_results, oofs = {}, []
    for exp, spec in EXPERIMENTS.items():
        d = df[~df["flagged"]] if spec["subset"] == "unflagged" else df
        print(f"[{exp}] n={len(d)} ({int(d['label'].sum())} anaemic), {len(spec['features'])} features")
        results, oof = run_experiment(d.reset_index(drop=True), spec["features"])
        all_results[exp] = {"note": spec["note"], "n": len(d), "n_anaemic": int(d["label"].sum()),
                            "features": spec["features"], "models": results}
        oofs.append(oof.assign(experiment=exp))
        if exp == "main":
            best = max(r["pooled"]["roc_auc"]["value"] for r in results.values())
            if best > 0.95:
                print(f"  WARNING: main ROC-AUC {best:.3f} > 0.95, check for leakage")
            plot_curves(oof, results, "roc", FIG_DIR / "roc_main.png")
            plot_curves(oof, results, "pr", FIG_DIR / "pr_main.png")

    meta = {"cv": f"StratifiedGroupKFold(n_splits={config.N_FOLDS}, shuffle=True, random_state={config.SEED}), "
                  "group = patient_id",
            "threshold": 0.5, "n_boot": config.N_BOOT,
            "ci": "95% percentile bootstrap over patients on pooled out-of-fold probabilities",
            "positive_class": "anaemic (Refer for Hb test)"}
    (RESULTS / "baselines.json").write_text(json.dumps({"meta": meta, "experiments": all_results}, indent=2))
    pd.concat(oofs, ignore_index=True).to_csv(RESULTS / "oof_baselines.csv", index=False)
    tab = table(all_results)
    tab.to_csv(RESULTS / "baselines_table.csv", index=False)

    for exp in EXPERIMENTS:
        t = tab[tab["experiment"] == exp]
        print(f"\n## {exp}: {EXPERIMENTS[exp]['note']}")
        cols = ["model", "imbalance"] + [c for m in METRICS for c in (m, f"{m}_ci")] + ["tn", "fp", "fn", "tp"]
        print(t[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print(f"\nsaved {RESULTS / 'baselines.json'}, baselines_table.csv, oof_baselines.csv, {FIG_DIR}/*.png")


if __name__ == "__main__":
    main()
