"""Bundles the Screen page reads: one per site, so the app never retrains.

eye: the P6 final model (outputs/models/final.joblib) unchanged, with its outer out-of-fold probabilities.
palm, nail: the same P6 procedure (TunedScreen, soft vote of top 3) fit on all rows (folder labels), plus 1 x 5
grouped out-of-fold probabilities from cross_validate for the uncertainty band.
Each bundle adds a healthy-class reference (per-feature quantiles) for the plain-language reasons and, for the eye,
a probability-to-Hb map from the outer out-of-fold probabilities (CP-AnemiC is the only set with Hb)."""
import argparse
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

import config
from netra.evaluate import cross_validate
from netra.tuning import TunedScreen, candidates
from scripts.train_baselines import NON_FEATURES

MODELS = config.OUT_DIR / "models"
COLS = list(config.CANDIDATE_FEATURES)
CSV = {"eye": config.FEATURES_CSV, "palm": config.GHANA_SITES["palm"]["csv"], "nail": config.GHANA_SITES["nail"]["csv"]}
HB_BINS = 10


def healthy_reference(df: pd.DataFrame) -> dict:
    h, a = df[df.label == 0], df[df.label == 1]
    return {"quantiles": {c: np.percentile(h[c], np.arange(101)).tolist() for c in COLS},
            "healthy_median": h[COLS].median().to_dict(), "anaemic_median": a[COLS].median().to_dict()}


def nn_reference(df: pd.DataFrame) -> dict:
    """Unfamiliar-photo reference (KNN, Unit IV): scaled training features and the NN_PCT percentile of each
    training photo's mean distance to its NN_K nearest other training photos. Uses no labels."""
    sc = StandardScaler().fit(df[COLS])
    X = sc.transform(df[COLS])
    d, _ = NearestNeighbors(n_neighbors=config.NN_K + 1).fit(X).kneighbors(X)
    own = d[:, 1:].mean(axis=1)                    # column 0 is the photo itself
    return {"mean": sc.mean_, "scale": sc.scale_, "X": X, "threshold": float(np.percentile(own, config.NN_PCT)),
            "train_distances": own}


def hb_map(p: np.ndarray, hb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Binned medians of Hb against calibrated probability, forced non-increasing."""
    edges = np.quantile(p, np.linspace(0, 1, HB_BINS + 1))
    idx = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, HB_BINS - 1)
    pk = np.array([np.median(p[idx == b]) for b in range(HB_BINS)])
    hk = np.minimum.accumulate(np.array([np.median(hb[idx == b]) for b in range(HB_BINS)]))
    return pk, hk


def hb_map_mae(p: np.ndarray, hb: np.ndarray, groups: np.ndarray) -> float:
    """Cross-validated mean absolute error of the map itself (5 grouped folds)."""
    err = np.empty(len(p))
    y = (hb < 11).astype(int)
    for tr, te in StratifiedGroupKFold(config.N_FOLDS, shuffle=True, random_state=config.SEED).split(p, y, groups):
        pk, hk = hb_map(p[tr], hb[tr])
        err[te] = np.abs(np.interp(p[te], pk, hk) - hb[te])
    return float(err.mean())


def eye_bundle(df: pd.DataFrame) -> dict:
    final = joblib.load(MODELS / "final.joblib")
    assert final["input_columns"] == COLS
    oof = pd.read_csv(config.OUT_DIR / "results" / "oof_tuned.csv").query("model == 'soft_vote_top3' and repeat == 0")
    oof = oof.set_index("patient_id").loc[df["patient_id"]]
    p, hb = oof["proba"].to_numpy(), oof["hb"].to_numpy()
    pk, hk = hb_map(p, hb)
    return {"model": final["model"], "threshold": final["threshold"], "oof_p": p, "oof_y": oof["label"].to_numpy(),
            "hb_knots": (pk.tolist(), hk.tolist()), "hb_mae": hb_map_mae(p, hb, df["cv_group"].to_numpy()),
            "members": final["members"], "label_source": "Hb, WHO < 11 g/dL",
            "trained_on": final["trained_on"]}


def ghana_bundle(site: str, df: pd.DataFrame) -> dict:
    X, y, g = df[COLS].to_numpy(float), df["label"].to_numpy(), df["cv_group"].astype(str).to_numpy()
    print(f"  {site}: out-of-fold probabilities (1 x {config.N_FOLDS} grouped) ...", flush=True)
    res = cross_validate(TunedScreen(candidates(COLS), top_k=3), X, y, g, n_repeats=1, n_boot=20)
    auc = float(np.nanmean([f["roc_auc"] for f in res.fold_metrics]))
    print(f"  {site}: OOF ROC-AUC {auc:.3f}; fitting on all {len(y)} rows ...", flush=True)
    if auc > 0.95:
        print(f"  WARNING: {site} ROC-AUC > 0.95, check for leakage")
    model = TunedScreen(candidates(COLS), top_k=3).fit(X, y, g)
    assert len(model.kept_features()) <= 15
    return {"model": model, "threshold": model.threshold_, "oof_p": res.proba[0], "oof_y": y, "oof_roc_auc": auc,
            "hb_knots": None, "hb_mae": None, "members": model.members_,
            "label_source": "folder labels (file names), no Hb", "trained_on": f"Ghana {site} originals, n={len(y)}"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference-only", action="store_true",
                    help="keep the saved models, recompute only the healthy and unfamiliar-photo references")
    args = ap.parse_args()
    assert not NON_FEATURES & set(COLS)
    path = config.OUT_DIR / "results" / "screen_models.json"
    summary = json.loads(path.read_text()) if args.reference_only and path.exists() else {"meta": __doc__, "sites": {}}
    for site, csv in CSV.items():
        df = pd.read_csv(csv).reset_index(drop=True)
        if args.reference_only:
            b = joblib.load(MODELS / f"screen_{site}.joblib")
        else:
            b = eye_bundle(df) if site == "eye" else ghana_bundle(site, df)
        b |= {"site": site, "input_columns": COLS, "n": len(df), "n_anaemic": int(df.label.sum()),
              **healthy_reference(df), "nn": nn_reference(df)}
        joblib.dump(b, MODELS / f"screen_{site}.joblib", compress=3)   # committed: keep each well under 5 MB
        summary["sites"][site] = {k: b[k] for k in ("n", "n_anaemic", "threshold", "members", "label_source",
                                                     "trained_on", "hb_mae")} | {"oof_roc_auc": b.get("oof_roc_auc")}
        summary["sites"][site]["unfamiliar_threshold"] = b["nn"]["threshold"]
        print(f"  {site}: unfamiliar-photo threshold {b['nn']['threshold']:.2f} (k={config.NN_K}, "
              f"{config.NN_PCT}th percentile of training distances)", flush=True)
        if args.reference_only:
            continue
        print(f"  {site}: saved, threshold {b['threshold']:.3f}, members {b['members']}"
              + (f", Hb map MAE {b['hb_mae']:.2f} g/dL" if b["hb_mae"] else ""), flush=True)
    path.write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
