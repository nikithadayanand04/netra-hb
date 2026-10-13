import argparse
import json
import time
from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

import config
from netra.evaluate import corrected_ci, cross_validate
from netra.tuning import LateFusion, TunedScreen, candidates
from scripts.train_baselines import NON_FEATURES

RESULTS = config.OUT_DIR / "results" / "sites"
FIG_DIR = config.OUT_DIR / "figures" / "sites"
COLS = list(config.CANDIDATE_FEATURES)
SITES = {
    "eye": {"csv": config.FEATURES_CSV, "data": "CP-AnemiC primary (conjunctiva)", "labels": "Hb, WHO < 11 g/dL"},
    "palm": {"csv": config.GHANA_SITES["palm"]["csv"], "data": "Ghana palm", "labels": "folder (file name)"},
    "nail": {"csv": config.GHANA_SITES["nail"]["csv"], "data": "Ghana fingernail", "labels": "folder (file name)"},
    "eye_extra": {"csv": config.GHANA_SITES["eye_extra"]["csv"],
                  "data": "SECONDARY: Ghana conjunctiva not in CP-AnemiC", "labels": "folder (file name)"},
}
COLOUR = {"eye": "#2a78d6", "palm": "#eb6834", "nail": "#1baf7a", "eye_extra": "#eda100"}
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
FIXED = "random_forest"   # untuned P5 defaults: same model at every site and size, nothing tuned on the subsample
FUSION_SERIES = ("main", "small")


def load(site: str) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    df = pd.read_csv(SITES[site]["csv"]).reset_index(drop=True)
    assert not NON_FEATURES & set(COLS)
    return df, df[COLS].to_numpy(float), df["label"].to_numpy(), df["cv_group"].astype(str).to_numpy()


def fixed_model(n_jobs: int = 1) -> TunedScreen:
    pipe, _ = candidates(COLS, [FIXED])[FIXED]
    return TunedScreen({FIXED: (pipe, {})}, n_jobs=n_jobs)


def fold_mean(res, metric: str) -> float:
    return float(np.nanmean([f[metric] for f in res.fold_metrics if f[metric] is not None]))


# ---------- 1. full-data nested CV per site (P6 procedure: tuned soft vote of top 3) ----------
def run_main() -> None:
    p6 = json.loads((config.OUT_DIR / "results" / "final.json").read_text())
    out = {"eye": {"source": "P6 outputs/results/final.json headline (same TunedScreen top-3 procedure)",
                   **p6["headline"]}}
    for site in ("palm", "nail", "eye_extra"):
        t0 = time.time()
        df, X, y, g = load(site)
        res = cross_validate(TunedScreen(candidates(COLS), top_k=3), X, y, g)
        s = res.summary()
        s["fold_sens_floor_met"] = float(np.mean([f["sensitivity"] >= config.SENS_FLOOR for f in res.fold_metrics]))
        s["members"] = Counter(m for f in res.fold_metrics for m in f["members"])
        out[site] = s
        fm = s["fold_mean"]
        print(f"  {site:<10} n={len(y)} ROC-AUC {fm['roc_auc']['value']:.3f} [{fm['roc_auc']['ci_low']:.2f}-"
              f"{fm['roc_auc']['ci_high']:.2f}]  sens {fm['sensitivity']['value']:.3f}  spec "
              f"{fm['specificity']['value']:.3f}  ({time.time() - t0:.0f}s)", flush=True)
        if fm["roc_auc"]["value"] > 0.95:
            print(f"  WARNING: {site} ROC-AUC > 0.95, check for leakage")
    (RESULTS / "main.json").write_text(json.dumps(out, indent=2, default=dict))


# ---------- 2. equal-n comparison and learning curves (fixed model) ----------
def subsample(y: np.ndarray, g: np.ndarray, n: int, seed: int) -> np.ndarray:
    """Whole patient groups, keeping the site's own prevalence, until ~n images."""
    rng = np.random.default_rng(seed)
    grp = pd.DataFrame({"g": g, "y": y}).groupby("g").agg(y=("y", "first"), size=("y", "size")).reset_index()
    target = {1: round(n * y.mean()), 0: n - round(n * y.mean())}
    keep = []
    for lab, t in target.items():
        d = grp[grp["y"] == lab].sample(frac=1, random_state=int(rng.integers(1 << 31)))
        keep += list(d["g"][d["size"].cumsum() <= t])
    return np.flatnonzero(np.isin(g, keep))


def curve_point(site: str, n: int, r: int) -> dict:
    df, X, y, g = load(site)
    idx = subsample(y, g, n, config.SEED + 1000 * r + n) if n < len(y) else np.arange(len(y))
    res = cross_validate(fixed_model(), X[idx], y[idx], g[idx], n_repeats=1, seed=config.SEED + r, n_boot=20)
    return {"site": site, "n_target": n, "n": int(len(idx)), "r": r,
            **{m: fold_mean(res, m) for m in ("roc_auc", "pr_auc", "sensitivity", "specificity")}}


def run_curves() -> None:
    jobs = []
    for site in SITES:
        n_all = len(load(site)[2])
        sizes = sorted({s for s in config.LC_SIZES if s < n_all} | {min(config.EQUAL_N, n_all), n_all})
        jobs += [(site, n, r) for n in sizes for r in range(config.N_SUBSAMPLES)]
    print(f"  {len(jobs)} subsample CVs ...", flush=True)
    rows = Parallel(n_jobs=-1, verbose=0)(delayed(curve_point)(*j) for j in jobs)
    pd.DataFrame(rows).to_csv(RESULTS / "curves.csv", index=False)


# ---------- 3. exploratory palm + nail late fusion with the shift control ----------
def pair_frame(shift: int) -> pd.DataFrame:
    palm, nail = (pd.read_csv(SITES[s]["csv"]) for s in ("palm", "nail"))
    palm, nail = (d[d["series"].isin(FUSION_SERIES)] for d in (palm, nail))
    nail = nail.assign(num=nail["num"] - shift)         # palm n <-> nail n + shift
    pairs = palm.merge(nail, on=["label", "series", "num"], suffixes=("_palm", "_nail")).reset_index(drop=True)
    # a fused row must stay with every other row that shares its palm group or its nail group
    ids = pd.factorize(pd.concat([pairs["cv_group_palm"], pairs["cv_group_nail"]]))[0]
    n = len(pairs)
    adj = coo_matrix((np.ones(n), (ids[:n], ids[n:])), shape=(ids.max() + 1,) * 2)
    comp = connected_components(adj, directed=False)[1]
    pairs["cv_group"] = comp[ids[:n]]
    return pairs


def run_fusion() -> None:
    out = {}
    k = len(COLS)
    for shift in config.FUSION_SHIFTS:
        pairs = pair_frame(shift)
        X = pairs[[f"{c}_palm" for c in COLS] + [f"{c}_nail" for c in COLS]].to_numpy(float)
        y, g = pairs["label"].to_numpy(), pairs["cv_group"].to_numpy()
        res = {"palm": cross_validate(fixed_model(-1), X[:, :k], y, g),
               "nail": cross_validate(fixed_model(-1), X[:, k:], y, g),
               "fused": cross_validate(LateFusion([(list(range(k)), fixed_model(-1)),
                                                   (list(range(k, 2 * k)), fixed_model(-1))]), X, y, g)}
        ratio = res["fused"].test_train_ratio
        block = {"n_pairs": int(len(pairs)), "n_groups": int(len(np.unique(g))), "anaemic": int(y.sum())}
        for name, r in res.items():
            block[name] = {m: r.summary()["fold_mean"][m] for m in ("roc_auc", "pr_auc", "sensitivity", "specificity")}
        for single in ("palm", "nail"):
            d = np.array([a["roc_auc"] - b["roc_auc"] for a, b in zip(res["fused"].fold_metrics,
                                                                       res[single].fold_metrics)])
            lo, hi = corrected_ci(d, ratio, bounds=(-1.0, 1.0))
            block[f"gain_vs_{single}"] = {"delta": float(d.mean()), "ci_low": lo, "ci_high": hi}
        out[str(shift)] = block
        print(f"  shift {shift:+d}: {len(pairs)} pairs  AUC palm {block['palm']['roc_auc']['value']:.3f}  nail "
              f"{block['nail']['roc_auc']['value']:.3f}  fused {block['fused']['roc_auc']['value']:.3f}  "
              f"gain vs palm {block['gain_vs_palm']['delta']:+.3f} [{block['gain_vs_palm']['ci_low']:+.3f}, "
              f"{block['gain_vs_palm']['ci_high']:+.3f}]", flush=True)
    (RESULTS / "fusion.json").write_text(json.dumps(out, indent=2))


# ---------- 4. shortcut and transfer checks for unexpectedly high scores ----------
def run_checks() -> None:
    from sklearn.metrics import roc_auc_score
    import joblib
    log = pd.read_csv(config.GHANA_LOG)
    out = {"acquisition_only_roc_auc": {}, "cp_model_transfer": {},
           "note": "acquisition_only: fixed RF on tissue_px + glare_frac only (no colour), 5x5 grouped CV; ~0.5 = no "
                   "acquisition shortcut. cp_model_transfer: P6 final model (CP-AnemiC, Hb labels) applied unchanged."}
    bundle = joblib.load(config.OUT_DIR / "models" / "final.joblib")
    for site in ("palm", "nail", "eye_extra"):
        df = pd.read_csv(SITES[site]["csv"]).merge(log[log.site == site][["file", "tissue_px", "glare_frac"]],
                                                   on="file")
        y, g = df["label"].to_numpy(), df["cv_group"].astype(str).to_numpy()
        pipe, _ = candidates(COLS, [FIXED])[FIXED]
        res = cross_validate(pipe.steps[-1][1], df[["tissue_px", "glare_frac"]].to_numpy(float), y, g, n_boot=20)
        out["acquisition_only_roc_auc"][site] = fold_mean(res, "roc_auc")
        p = bundle["model"].predict_proba(df[bundle["input_columns"]].to_numpy(float))[:, 1]
        pred = p >= bundle["threshold"]
        out["cp_model_transfer"][site] = {"roc_auc": float(roc_auc_score(y, p)), "sensitivity": float(pred[y == 1].mean()),
                                          "specificity": float((~pred[y == 0]).mean())}
        print(f"  {site:<10} acquisition-only AUC {out['acquisition_only_roc_auc'][site]:.3f}  CP-model transfer AUC "
              f"{out['cp_model_transfer'][site]['roc_auc']:.3f}", flush=True)
    (RESULTS / "checks.json").write_text(json.dumps(out, indent=2))


# ---------- 5. table, figures, sites.json ----------
def fmt(p: dict) -> str:
    return f"{p['value']:.3f} [{p['ci_low']:.2f}–{p['ci_high']:.2f}]"


def site_table(main: dict, curves: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for site, spec in SITES.items():
        df = pd.read_csv(spec["csv"])
        fm = main[site]["fold_mean"]
        eq = curves[(curves.site == site) & (curves.n_target == min(config.EQUAL_N, len(df)))]["roc_auc"]
        rows.append({"site": site, "data": spec["data"], "labels": spec["labels"], "n_images": len(df),
                     "n_groups": df["cv_group"].nunique(), "pct_anaemic": f"{df['label'].mean():.0%}",
                     "roc_auc": fmt(fm["roc_auc"]), "pr_auc": fmt(fm["pr_auc"]),
                     "sensitivity": fmt(fm["sensitivity"]), "specificity": fmt(fm["specificity"]),
                     "folds_sens_floor_met": f"{main[site].get('fold_sens_floor_met', float('nan')):.0%}",
                     f"roc_auc_n{config.EQUAL_N}_fixed_rf": f"{eq.mean():.3f} [{eq.quantile(.025):.2f}–"
                                                             f"{eq.quantile(.975):.2f}]"})
    return pd.DataFrame(rows)


def _style(ax) -> None:
    ax.set_facecolor(SURFACE)
    ax.grid(color=GRID, lw=0.6)
    ax.tick_params(labelsize=7, colors=INK_2, length=0)
    for side in ax.spines.values():
        side.set_visible(False)


def plot_learning_curves(curves: pd.DataFrame, path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=200, facecolor=SURFACE)
    _style(ax)
    for site in SITES:
        d = curves[curves.site == site].groupby("n_target").agg(n=("n", "mean"), m=("roc_auc", "mean"),
                                                                 sd=("roc_auc", "std"))
        ls = (0, (4, 2)) if site == "eye_extra" else "-"
        ax.fill_between(d["n"], d["m"] - d["sd"], d["m"] + d["sd"], color=COLOUR[site], alpha=0.12, lw=0)
        ax.plot(d["n"], d["m"], color=COLOUR[site], lw=2, ls=ls, marker="o", ms=4, label=SITES[site]["data"])
        ax.annotate(site, (d["n"].iloc[-1], d["m"].iloc[-1]), xytext=(5, 0), textcoords="offset points",
                    fontsize=7, color=INK, va="center")
    ax.axvline(config.EQUAL_N, color=INK_2, lw=1, ls=(0, (1, 2)))
    ax.axhline(0.5, color=INK_2, lw=1, ls=(0, (1, 2)))
    ax.set_xlabel("images per site (subsampled by patient group, site prevalence kept)", fontsize=8, color=INK_2)
    ax.set_ylabel("ROC-AUC, 5-fold grouped CV", fontsize=8, color=INK_2)
    ax.set_ylim(0.4, 1.0)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title(f"Learning curves: fixed random forest, {config.N_SUBSAMPLES} subsamples per size (±1 SD)\n"
                 f"dotted: n={config.EQUAL_N} and chance",
                 loc="left", fontsize=8, color=INK)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def plot_site_auc(main: dict, curves: pd.DataFrame, path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2), dpi=200, facecolor=SURFACE, sharex=True)
    names = list(SITES)[::-1]
    for ax, title in zip(axes, ("All data: nested-tuned soft vote, 5x5 folds, corrected 95% CI",
                                f"n={config.EQUAL_N}: fixed RF, {config.N_SUBSAMPLES} subsamples, 2.5–97.5%")):
        _style(ax)
        for i, site in enumerate(names):
            if ax is axes[0]:
                p = main[site]["fold_mean"]["roc_auc"]
                m, lo, hi = p["value"], p["ci_low"], p["ci_high"]
            else:
                n = min(config.EQUAL_N, len(pd.read_csv(SITES[site]["csv"])))
                v = curves[(curves.site == site) & (curves.n_target == n)]["roc_auc"]
                m, lo, hi = v.mean(), v.quantile(.025), v.quantile(.975)
            ax.plot([lo, hi], [i, i], color=COLOUR[site], lw=2, solid_capstyle="round")
            ax.plot(m, i, "o", ms=8, color=COLOUR[site], mec=SURFACE, mew=2)
            ax.annotate(f"{m:.2f}", (m, i), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=7,
                        color=INK)
        ax.axvline(0.5, color=INK_2, lw=1, ls=(0, (1, 2)))
        ax.set_yticks(range(len(names)), [f"{s}\n({SITES[s]['labels'].split(',')[0].split(' (')[0]} labels)" for s in names])
        ax.set_title(title, loc="left", fontsize=8, color=INK)
        ax.set_xlim(0.4, 1.0)
        ax.set_xlabel("ROC-AUC", fontsize=8, color=INK_2)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def run_report() -> None:
    main = json.loads((RESULTS / "main.json").read_text())
    curves = pd.read_csv(RESULTS / "curves.csv")
    fusion = json.loads((RESULTS / "fusion.json").read_text())
    checks = json.loads((RESULTS / "checks.json").read_text())
    ghana = json.loads((config.OUT_DIR / "results" / "ghana_data.json").read_text())
    tab = site_table(main, curves)
    tab.to_csv(config.OUT_DIR / "results" / "sites_table.csv", index=False)
    plot_learning_curves(curves, FIG_DIR / "learning_curves.png")
    plot_site_auc(main, curves, FIG_DIR / "site_auc.png")
    lc = (curves.groupby(["site", "n_target"])[["n", "roc_auc", "pr_auc", "sensitivity", "specificity"]]
          .agg(["mean", "std"]).round(4))
    lc.columns = [f"{a}_{b}" for a, b in lc.columns]
    out = {"meta": {
        "main": "per site: repeated grouped nested CV of the P6 procedure (grid search per family on inner "
                "StratifiedGroupKFold, soft vote of top 3, Platt calibration, threshold for inner sens >= "
                f"{config.SENS_FLOOR}); same {len(COLS)} candidate colour features, redundancy pruning in-fold",
        "equal_n_and_curves": f"fixed untuned random forest (P5 defaults) + in-fold calibration/threshold; each site "
                              f"subsampled by patient group at its own prevalence, {config.N_SUBSAMPLES} subsamples "
                              "x 5-fold grouped CV; eye at n=220 is the full set (only the CV seed varies)",
        "labels": "eye = Hb (WHO < 11 g/dL); palm, nail, eye_extra = Ghana folder labels (file names), no Hb. "
                  f"Folder-vs-WHO agreement on the CP overlap: {ghana['label_agreement']['agreement']:.1%} "
                  f"({ghana['label_agreement']['agree']}/{ghana['label_agreement']['matched_with_one_label']}) -> "
                  f"label-noise estimate {ghana['label_agreement']['label_noise_estimate']:.1%}",
        "not_comparable": "eye (CP-AnemiC) and palm/nail (Ghana) are different children; site differences mix "
                          "body site with dataset, label source and prevalence",
        "fusion": "EXPLORATORY. Palm and nail paired by (label, series, number); child identity is not documented. "
                  "Late fusion = mean of each site's calibrated probability (fixed RF per site). Shift +-1 pairs "
                  "palm n with nail n+-1 (same label): if fusion helps as much there, the gain is not from "
                  "same-child pairing."},
        "table": tab.to_dict("records"), "main": main, "learning_curves": lc.reset_index().to_dict("records"),
        "fusion": fusion, "checks": checks, "ghana_data": ghana,
        "figures": {k: str((FIG_DIR / f"{k}.png").relative_to(config.ROOT)) for k in ("learning_curves", "site_auc")}}
    (config.OUT_DIR / "results" / "sites.json").write_text(json.dumps(out, indent=2, default=str))
    show = ["site", "labels", "n_images", "pct_anaemic", "roc_auc", "sensitivity", "specificity",
            "folds_sens_floor_met", f"roc_auc_n{config.EQUAL_N}_fixed_rf"]
    print(tab[show].to_string(index=False))
    print("\nfusion (fixed RF per site, 5x5 grouped CV on paired rows):")
    for s, b in fusion.items():
        print(f"  shift {int(s):+d}: n={b['n_pairs']}  palm {fmt(b['palm']['roc_auc'])}  nail {fmt(b['nail']['roc_auc'])}"
              f"  fused {fmt(b['fused']['roc_auc'])}  gain vs palm {b['gain_vs_palm']['delta']:+.3f} "
              f"[{b['gain_vs_palm']['ci_low']:+.3f}, {b['gain_vs_palm']['ci_high']:+.3f}]  vs nail "
              f"{b['gain_vs_nail']['delta']:+.3f} [{b['gain_vs_nail']['ci_low']:+.3f}, {b['gain_vs_nail']['ci_high']:+.3f}]")
    print(f"\nsaved outputs/results/sites.json, sites_table.csv, {FIG_DIR.relative_to(config.ROOT)}/*.png")


STAGES = {"main": run_main, "curves": run_curves, "fusion": run_fusion, "checks": run_checks, "report": run_report}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stages", nargs="*", help=f"any of {list(STAGES)}; default all")
    args = ap.parse_args()
    if bad := set(args.stages) - set(STAGES):
        ap.error(f"unknown stages {bad}")
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for st in args.stages or list(STAGES):
        print(f"[{st}]", flush=True)
        STAGES[st]()


if __name__ == "__main__":
    main()
