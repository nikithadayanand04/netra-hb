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
SURFACE, INK, INK_2, GRID, SERIES = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"
PRIMARY = "primary"

# Every experiment starts from candidate columns; redundancy pruning runs inside each training fold
# (config.MODEL_FEATURES is what the same rule picks on all rows, i.e. the final refit's inputs).
EXPERIMENTS = {
    PRIMARY: {"csv": config.FEATURES_CSV, "candidates": config.CANDIDATE_FEATURES,
              "note": "PRIMARY: quality-clean images (no blur / upscaled / high-glare flags), colour candidates "
                      "pruned in-fold."},
    "secondary_all": {"csv": config.FEATURES_ALL_CSV, "candidates": config.CANDIDATE_FEATURES,
                      "note": "Secondary analysis: all kept images, quality-flagged ones included."},
    "shortcut_ablation": {"csv": config.FEATURES_CSV,
                          "candidates": config.CANDIDATE_FEATURES + config.EXCLUDED_FEATURES,
                          "note": "NOT THE REAL MODEL. Primary images plus glare_frac and tissue_px "
                                  "(image-acquisition shortcuts) to show how much they inflate scores."},
}
# Columns derived from the label, Hb or identity: never model inputs.
NON_FEATURES = {"patient_id", "cv_group", "dataset", "hb", "label", "severity", "hb_cutoff"}


def run_experiment(df: pd.DataFrame, features: list[str]) -> tuple[dict, pd.DataFrame]:
    assert not NON_FEATURES & set(features), "label-derived column used as a feature"
    X, y, groups = df[features].to_numpy(float), df["label"].to_numpy(), df["cv_group"].to_numpy()
    results, oof = {}, []
    for name, pipe in build_models(columns=features).items():
        res = cross_validate(pipe, X, y, groups)
        results[name] = {"label": LABELS[name], "imbalance": IMBALANCE[name], **res.summary()}
        oof += [pd.DataFrame({"patient_id": df["patient_id"].to_numpy(), "hb": df["hb"].to_numpy(), "label": y,
                              "model": name, "repeat": r, "fold": res.fold[r], "proba": res.proba[r]})
                for r in range(len(res.proba))]
        fm = results[name]["fold_mean"]
        print(f"  {name:<18} ROC-AUC {fm['roc_auc']['value']:.3f} [{fm['roc_auc']['ci_low']:.3f}-"
              f"{fm['roc_auc']['ci_high']:.3f}]  sens {fm['sensitivity']['value']:.3f}  "
              f"spec {fm['specificity']['value']:.3f}")
    return results, pd.concat(oof, ignore_index=True)


def table(all_results: dict) -> pd.DataFrame:
    rows = []
    for exp, block in all_results.items():
        for name, r in block["models"].items():
            row = {"experiment": exp, "model": r["label"], "imbalance": r["imbalance"]}
            for m in METRICS:
                p = r["fold_mean"][m]
                row[m] = p["value"]
                row[f"{m}_ci"] = f"{p['ci_low']:.2f}-{p['ci_high']:.2f}"
            row["pooled_roc_auc_r0"] = r["pooled"]["roc_auc"]["value"]
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
        d = oof[(oof["model"] == name) & (oof["repeat"] == 0)]
        _style(ax)
        if kind == "roc":
            fpr, tpr, _ = roc_curve(d["label"], d["proba"])
            ax.plot([0, 1], [0, 1], color=INK_2, lw=1, ls=(0, (3, 3)))
            ax.plot(fpr, tpr, color=SERIES, lw=2, solid_capstyle="round")
            p, f = results[name]["pooled"]["roc_auc"], results[name]["fold_mean"]["roc_auc"]
            head = f"AUC {p['value']:.2f}\n25-fold mean {f['value']:.2f} [{f['ci_low']:.2f}–{f['ci_high']:.2f}]"
        else:
            prec, rec, _ = precision_recall_curve(d["label"], d["proba"])
            ax.axhline(prevalence, color=INK_2, lw=1, ls=(0, (3, 3)))
            ax.plot(rec[:-1], prec[:-1], color=SERIES, lw=2, drawstyle="steps-post")   # drop the (0, 1) sentinel
            p, f = results[name]["pooled"]["pr_auc"], results[name]["fold_mean"]["pr_auc"]
            head = f"AP {p['value']:.2f}\n25-fold mean {f['value']:.2f} [{f['ci_low']:.2f}–{f['ci_high']:.2f}]"
        ax.set_title(f"{LABELS[name]}\n{head}", loc="left", fontsize=8, color=INK)
    for ax in axes.flat[len(names):]:
        ax.set_visible(False)
    xl, yl = ("False positive rate (1 − specificity)", "Sensitivity") if kind == "roc" else \
        ("Recall (sensitivity)", "Precision")
    ref = "diagonal = chance" if kind == "roc" else f"dashed = prevalence {prevalence:.2f} (all-normal / chance)"
    fig.supxlabel(xl, fontsize=9, color=INK_2)
    fig.supylabel(yl, fontsize=9, color=INK_2)
    fig.suptitle(f"{'ROC' if kind == 'roc' else 'Precision–recall'} curves, out-of-fold, patient-grouped 5-fold CV, "
                 f"seed-{config.SEED} repeat\n(n={oof['patient_id'].nunique()}; {ref}; "
                 f"[ ] = corrected 95% CI over {config.N_REPEATS}x{config.N_FOLDS} folds)",
                 x=0.01, ha="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    all_results, oofs = {}, []
    for exp, spec in EXPERIMENTS.items():
        d = pd.read_csv(spec["csv"])
        print(f"[{exp}] n={len(d)} ({int(d['label'].sum())} anaemic), {len(spec['candidates'])} candidates")
        results, oof = run_experiment(d.reset_index(drop=True), spec["candidates"])
        all_results[exp] = {"note": spec["note"], "n": len(d), "n_anaemic": int(d["label"].sum()),
                            "candidate_features": spec["candidates"], "models": results}
        oofs.append(oof.assign(experiment=exp))
        best = max(r["fold_mean"]["roc_auc"]["value"] for r in results.values())
        if best > 0.95:
            print(f"  WARNING: {exp} ROC-AUC {best:.3f} > 0.95, check for leakage")
        if exp == PRIMARY:
            plot_curves(oof, results, "roc", FIG_DIR / "roc_primary.png")
            plot_curves(oof, results, "pr", FIG_DIR / "pr_primary.png")

    meta = {"cv": f"{config.N_REPEATS} x StratifiedGroupKFold(n_splits={config.N_FOLDS}, shuffle=True), "
                  f"random_state = {config.SEED} + repeat, group = cv_group (patient_id, merged across "
                  "near-duplicate images)",
            "feature_selection": "label-free Spearman redundancy pruning fit inside each training fold "
                                 "(kept features per fold in folds[].features)",
            "primary": PRIMARY, "quality_exclude": config.QUALITY_EXCLUDE, "threshold": 0.5, "n_boot": config.N_BOOT,
            "headline": f"fold_mean: mean over all {config.N_REPEATS * config.N_FOLDS} folds with a 95% "
                        "Nadeau-Bengio corrected t-interval",
            "pooled": f"first repeat (seed {config.SEED}) pooled out-of-fold metrics, confusion matrix and curves; "
                      "95% percentile bootstrap over patients",
            "positive_class": "anaemic (Refer for Hb test)"}
    (RESULTS / "baselines.json").write_text(json.dumps({"meta": meta, "experiments": all_results}, indent=2))
    pd.concat(oofs, ignore_index=True).to_csv(RESULTS / "oof_baselines.csv", index=False)
    tab = table(all_results)
    tab.to_csv(RESULTS / "baselines_table.csv", index=False)

    for exp in EXPERIMENTS:
        t = tab[tab["experiment"] == exp]
        print(f"\n## {exp}: {EXPERIMENTS[exp]['note']}")
        cols = ["model", "imbalance"] + [c for m in METRICS for c in (m, f"{m}_ci")] + ["tn", "fp", "fn", "tp"]
        print(f"(mean over {config.N_REPEATS}x{config.N_FOLDS} folds, corrected 95% CI; tn..tp = seed-{config.SEED} "
              "repeat, pooled)")
        print(t[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print(f"\nsaved {RESULTS / 'baselines.json'}, baselines_table.csv, oof_baselines.csv, {FIG_DIR}/*.png")


if __name__ == "__main__":
    main()
