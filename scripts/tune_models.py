import json
import time

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.base import clone
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.tree import DecisionTreeClassifier

import config
from netra.evaluate import METRICS, corrected_ci, cross_validate
from netra.models import LABELS, pruner
from netra.tuning import GRIDS, TunedScreen, candidates
from scripts.train_baselines import NON_FEATURES, PRIMARY

RESULTS = config.OUT_DIR / "results"
FIG_DIR = config.OUT_DIR / "figures" / "tuning"
MODEL_PATH = config.OUT_DIR / "models" / "final.joblib"
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
CRITERION_COLOUR = {"gini": "#2a78d6", "entropy": "#eb6834"}
DEPTHS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, None]
ALPHAS = [0.0, 0.002, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.05]
TOP_K = 3
FINAL = "soft_vote_top3"


def outer_splits(X, y, groups) -> list[tuple]:
    return [(tr, te) for r in range(config.N_REPEATS)
            for tr, te in StratifiedGroupKFold(config.N_FOLDS, shuffle=True, random_state=config.SEED + r)
            .split(X, y, groups)]


def _tree_point(X, y, tr, te, cols, criterion, depth, alpha) -> tuple[float, float]:
    tree = DecisionTreeClassifier(criterion=criterion, max_depth=depth, ccp_alpha=alpha,
                                  class_weight="balanced", random_state=config.SEED)
    prune = pruner(cols).fit(X[tr])
    tree.fit(prune.transform(X[tr]), y[tr])
    auc = lambda rows: roc_auc_score(y[rows], tree.predict_proba(prune.transform(X[rows]))[:, 1])
    return auc(tr), auc(te)


def tree_curves(X, y, groups, cols) -> dict:
    """Validation curves (train vs held-out ROC-AUC over the 25 outer folds) for the overfitting section. These
    describe complexity, they do not pick the reported model: that happens inside nested CV."""
    splits = outer_splits(X, y, groups)
    out = {}
    for kind, values in (("max_depth", DEPTHS), ("ccp_alpha", ALPHAS)):
        out[kind] = {}
        for crit in CRITERION_COLOUR:
            rows = []
            for v in values:
                depth, alpha = (v, 0.0) if kind == "max_depth" else (None, v)
                pts = np.array(Parallel(n_jobs=-1)(delayed(_tree_point)(X, y, tr, te, cols, crit, depth, alpha)
                                                   for tr, te in splits))
                rows.append({"value": v, "train_mean": pts[:, 0].mean(), "train_sd": pts[:, 0].std(ddof=1),
                             "val_mean": pts[:, 1].mean(), "val_sd": pts[:, 1].std(ddof=1)})
            out[kind][crit] = rows
    return out


def plot_tree_curves(curves: dict, path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), dpi=200, facecolor=SURFACE)
    for ax, (kind, xlabel) in zip(axes, (("max_depth", "max_depth (rightmost = unlimited)"),
                                         ("ccp_alpha", "ccp_alpha (cost-complexity pruning, unlimited depth)"))):
        ax.set_facecolor(SURFACE)
        ax.grid(color=GRID, lw=0.6)
        ax.tick_params(labelsize=7, colors=INK_2, length=0)
        for side in ax.spines.values():
            side.set_visible(False)
        for crit, rows in curves[kind].items():
            x = np.arange(len(rows)) if kind == "max_depth" else [r["value"] for r in rows]
            for part, ls in (("train", (0, (3, 2))), ("val", "-")):
                m = np.array([r[f"{part}_mean"] for r in rows])
                ax.plot(x, m, color=CRITERION_COLOUR[crit], lw=2, ls=ls, marker="o", ms=4,
                        label=f"{crit} {'train' if part == 'train' else 'validation'}")
                if part == "val":
                    sd = np.array([r["val_sd"] for r in rows])
                    ax.fill_between(x, m - sd, m + sd, color=CRITERION_COLOUR[crit], alpha=0.12, lw=0)
                    best = int(np.argmax(m))
                    ax.annotate(f"{crit} best {m[best]:.2f}", (x[best], m[best]), xytext=(4, -12),
                                textcoords="offset points", fontsize=7, color=INK)
        if kind == "max_depth":
            ax.set_xticks(np.arange(len(DEPTHS)), [str(d) if d else "None" for d in DEPTHS])
        ax.axhline(0.5, color=INK_2, lw=1, ls=(0, (1, 2)))
        ax.set_ylim(0.4, 1.02)
        ax.set_xlabel(xlabel, fontsize=8, color=INK_2)
        ax.set_ylabel("ROC-AUC", fontsize=8, color=INK_2)
    axes[0].legend(fontsize=7, frameon=False, loc="lower left")
    fig.suptitle(f"Decision tree complexity: train (dashed) vs validation (solid, ±1 SD band), "
                 f"{config.N_REPEATS}x{config.N_FOLDS} patient-grouped folds; dotted = chance",
                 x=0.01, ha="left", fontsize=9, color=INK)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def nested(name: str, cands: dict, X, y, groups, top_k: int = 1) -> tuple[dict, object]:
    t0 = time.time()
    res = cross_validate(TunedScreen(cands, top_k=top_k), X, y, groups)
    s = res.summary()
    s["brier_pooled"] = float(brier_score_loss(y, res.proba[0]))
    s["fold_sens_floor_met"] = float(np.mean([f["sensitivity"] >= config.SENS_FLOOR for f in res.fold_metrics]))
    fm = s["fold_mean"]
    print(f"  {name:<22} ROC-AUC {fm['roc_auc']['value']:.3f} [{fm['roc_auc']['ci_low']:.2f}-"
          f"{fm['roc_auc']['ci_high']:.2f}]  sens {fm['sensitivity']['value']:.3f}  "
          f"spec {fm['specificity']['value']:.3f}  ({time.time() - t0:.0f}s)", flush=True)
    return s, res


def paired_delta(after: list[dict], before: list[dict], ratio: float) -> dict:
    assert [f["n"] for f in after] == [f["n"] for f in before], "baseline used different splits"
    out = {}
    for m in ("roc_auc", "pr_auc"):
        d = np.array([a[m] - b[m] for a, b in zip(after, before)])
        lo, hi = corrected_ci(d, ratio, bounds=(-1.0, 1.0))
        out[m] = {"delta": float(d.mean()), "ci_low": lo, "ci_high": hi}
    return out


def before_after(tuned: dict, base: dict, ratio: float) -> tuple[pd.DataFrame, dict]:
    rows, deltas = [], {}
    for name, s in tuned.items():
        b = base.get(name)
        for stage, block in (("before", b), ("after", s)):
            if block is None:
                continue
            row = {"model": name, "stage": stage}
            for m in METRICS:
                p = block["fold_mean"][m]
                row[m] = p["value"]
                row[f"{m}_ci"] = f"{p['ci_low']:.2f}-{p['ci_high']:.2f}"
            rows.append(row)
        if b is not None:
            deltas[name] = paired_delta(s["folds"], b["folds"], ratio)
    return pd.DataFrame(rows), deltas


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(config.FEATURES_CSV).reset_index(drop=True)
    cols = list(config.CANDIDATE_FEATURES)
    assert not NON_FEATURES & set(cols)
    X, y, groups = df[cols].to_numpy(float), df["label"].to_numpy(), df["cv_group"].to_numpy()
    print(f"[primary] n={len(y)} ({int(y.sum())} anaemic), {len(cols)} candidates, sens floor {config.SENS_FLOOR}")

    print("decision-tree validation curves ...", flush=True)
    curves = tree_curves(X, y, groups, cols)
    plot_tree_curves(curves, FIG_DIR / "tree_depth_pruning_curves.png")

    print("nested CV (inner StratifiedGroupKFold tuning + calibration + sens-floor threshold) ...", flush=True)
    all_c = candidates(cols)
    tuned, oof = {}, []
    dt_pipe, dt_grid = all_c["decision_tree"]
    crit_runs = {f"decision_tree_{c}": {"decision_tree": (dt_pipe, {**dt_grid, "clf__criterion": [c]})}
                 for c in ("gini", "entropy")}
    runs = {**{n: {n: all_c[n]} for n in GRIDS}, **crit_runs, FINAL: all_c}
    for name, cands in runs.items():
        s, res = nested(name, cands, X, y, groups, top_k=TOP_K if name == FINAL else 1)
        tuned[name] = s
        oof += [pd.DataFrame({"patient_id": df["patient_id"], "hb": df["hb"], "label": y, "model": name,
                              "repeat": r, "fold": res.fold[r], "proba": res.proba[r],
                              "threshold": res.threshold[r]}) for r in range(len(res.proba))]
        ratio = res.test_train_ratio
        best = s["fold_mean"]["roc_auc"]["value"]
        if best > 0.95:
            print(f"  WARNING: {name} ROC-AUC {best:.3f} > 0.95, check for leakage")

    base_all = json.loads((RESULTS / "baselines.json").read_text())["experiments"][PRIMARY]["models"]
    base = {n: b for n, b in base_all.items() if n in GRIDS}
    base_oof = pd.read_csv(RESULTS / "oof_baselines.csv").query("experiment == @PRIMARY and repeat == 0")
    for n in base:
        d = base_oof[base_oof.model == n]
        base[n]["brier_pooled"] = float(brier_score_loss(d["label"], d["proba"]))
    tab, deltas = before_after(tuned, base, ratio)

    print(f"fitting final model ({FINAL}) on all {len(y)} rows ...", flush=True)
    final = TunedScreen(all_c, top_k=TOP_K).fit(X, y, groups)
    features = final.kept_features()
    assert len(features) <= 15, features
    bundle = {"model": final, "input_columns": cols, "features": features, "threshold": final.threshold_,
              "members": final.members_, "sens_floor": config.SENS_FLOOR,
              "positive_label": "Refer for Hb test", "negative_label": "Normal",
              "trained_on": f"{config.DATASET_NAME} primary, n={len(y)}"}
    joblib.dump(bundle, MODEL_PATH)

    final_info = {"model": FINAL, "path": str(MODEL_PATH.relative_to(config.ROOT)),
                  "input_columns": cols, "features": features, "threshold": final.threshold_,
                  **{k: v for k, v in final.fold_info().items() if k != "threshold"}}
    meta = {"cv": f"outer: {config.N_REPEATS} x StratifiedGroupKFold(n_splits={config.N_FOLDS}, shuffle=True), "
                  f"random_state = {config.SEED} + repeat, same splits as baselines.json; inner: "
                  f"StratifiedGroupKFold(n_splits={config.N_FOLDS}) on the outer training fold only",
            "per_training_fold": "in-fold redundancy pruning -> grid search on inner ROC-AUC -> best model (or "
                                 f"soft vote of top {TOP_K} by inner ROC-AUC) -> Platt calibration on inner "
                                 "out-of-fold probabilities -> threshold = highest calibrated cut-off with inner "
                                 f"OOF sensitivity >= {config.SENS_FLOOR} -> refit on the whole training fold",
            "final_model_choice": f"{FINAL} was fixed before seeing outer results (brief: soft-voting ensemble of "
                                  "the best syllabus models); it is not picked as the best outer score",
            "before": "baselines.json primary (default hyperparameters, uncalibrated, threshold 0.5)",
            "headline": f"fold_mean: mean over {config.N_REPEATS * config.N_FOLDS} outer folds, 95% Nadeau-Bengio "
                        "corrected t-interval; delta = paired per-fold after - before, same correction",
            "grids": GRIDS, "sens_floor": config.SENS_FLOOR, "n": len(y), "n_anaemic": int(y.sum()),
            "positive_class": "anaemic (Refer for Hb test)"}
    out = {"meta": meta, "final": final_info, "headline": tuned[FINAL], "tuned": tuned,
           "before": {n: {k: b[k] for k in ("fold_mean", "pooled", "confusion_matrix", "brier_pooled")}
                      for n, b in base.items()},
           "delta_vs_before": deltas, "tree_curves": curves,
           "figures": {"tree_curves": str((FIG_DIR / "tree_depth_pruning_curves.png").relative_to(config.ROOT))}}
    (RESULTS / "final.json").write_text(json.dumps(out, indent=2, default=lambda o: o.item()))
    tab.to_csv(RESULTS / "tuned_table.csv", index=False)
    pd.concat(oof, ignore_index=True).to_csv(RESULTS / "oof_tuned.csv", index=False)

    cols_show = ["model", "stage"] + [c for m in METRICS for c in (m, f"{m}_ci")]
    print(f"\n## before (defaults, t=0.5) vs after (nested-tuned, calibrated, t for sens>={config.SENS_FLOOR})")
    print(tab[cols_show].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print("\n## paired delta ROC-AUC (after - before), corrected 95% CI")
    for n, d in deltas.items():
        print(f"  {n:<18} {d['roc_auc']['delta']:+.3f} [{d['roc_auc']['ci_low']:+.3f}, {d['roc_auc']['ci_high']:+.3f}]"
              f"  PR-AUC {d['pr_auc']['delta']:+.3f}")
    print("\n## sens floor met per outer fold / Brier (pooled repeat 0, before -> after)")
    for n, s in tuned.items():
        b = base.get(n, {}).get("brier_pooled")
        print(f"  {n:<22} {s['fold_sens_floor_met']:.0%}  brier {'' if b is None else f'{b:.3f} -> '}"
              f"{s['brier_pooled']:.3f}")
    print(f"\nfinal: members {final.members_}, threshold {final.threshold_:.3f}, {len(features)} features")
    print(f"saved {MODEL_PATH}, {RESULTS / 'final.json'}, tuned_table.csv, oof_tuned.csv, {FIG_DIR}")


if __name__ == "__main__":
    main()
