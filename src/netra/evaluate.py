import inspect
from dataclasses import dataclass, field

import numpy as np
from scipy import stats
from sklearn.base import clone
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

import config

METRICS = ["sensitivity", "specificity", "roc_auc", "pr_auc", "f1"]


@dataclass
class CVResult:
    proba: np.ndarray           # (n_repeats, n) out-of-fold probabilities
    fold: np.ndarray            # (n_repeats, n) fold index per repeat
    fold_metrics: list[dict]    # one entry per (repeat, fold)
    pooled: dict                # first repeat's pooled out-of-fold metrics
    threshold: np.ndarray | None = None              # (n_repeats, n) decision threshold each row was scored at
    ci: dict = field(default_factory=dict)          # patient bootstrap CI on `pooled`
    test_train_ratio: float = 0.25

    def summary(self) -> dict:
        per_fold = {m: [np.nan if f[m] is None else f[m] for f in self.fold_metrics] for m in METRICS}
        return {
            "fold_mean": {m: {"value": float(np.nanmean(v)), "sd": float(np.nanstd(v, ddof=1)),
                              **dict(zip(("ci_low", "ci_high"), corrected_ci(v, self.test_train_ratio)))}
                          for m, v in per_fold.items()},
            "pooled": {m: {"value": self.pooled[m], "ci_low": self.ci[m][0], "ci_high": self.ci[m][1]}
                       for m in METRICS},
            "confusion_matrix": self.pooled["confusion_matrix"],
            "folds": self.fold_metrics,
        }


def corrected_ci(values, test_train_ratio: float, alpha: float = 0.05,
                 bounds: tuple[float, float] = (0.0, 1.0)) -> tuple[float, float]:
    """Nadeau-Bengio corrected t-interval for the mean over repeated-CV folds. Folds share training rows,
    so the naive standard error is too small; the variance is inflated by n_test / n_train."""
    v = np.asarray(values, float)
    v = v[~np.isnan(v)]
    if len(v) < 2:
        return float("nan"), float("nan")
    half = stats.t.ppf(1 - alpha / 2, len(v) - 1) * np.sqrt((1 / len(v) + test_train_ratio) * v.var(ddof=1))
    return float(max(v.mean() - half, bounds[0])), float(min(v.mean() + half, bounds[1]))


def metrics_at(y: np.ndarray, proba: np.ndarray, threshold: float = 0.5) -> dict:
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    both = len(np.unique(y)) == 2
    return {
        "sensitivity": tp / (tp + fn) if tp + fn else np.nan,
        "specificity": tn / (tn + fp) if tn + fp else np.nan,
        "roc_auc": roc_auc_score(y, proba) if both else np.nan,
        "pr_auc": average_precision_score(y, proba) if both else np.nan,
        "f1": f1_score(y, pred, zero_division=0),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def bootstrap_ci(y: np.ndarray, proba: np.ndarray, groups: np.ndarray, threshold: float = 0.5,
                 n_boot: int = config.N_BOOT, seed: int = config.SEED, alpha: float = 0.05) -> dict:
    """Percentile CIs from resampling whole patients, so an image and its patient-mates move together."""
    rng = np.random.default_rng(seed)
    uniq, inv = np.unique(groups, return_inverse=True)
    members = [np.flatnonzero(inv == g) for g in range(len(uniq))]
    draws = {m: [] for m in METRICS}
    for _ in range(n_boot):
        idx = np.concatenate([members[g] for g in rng.integers(len(uniq), size=len(uniq))])
        if len(np.unique(y[idx])) < 2:
            continue
        res = metrics_at(y[idx], proba[idx], threshold[idx] if np.ndim(threshold) else threshold)
        for m in METRICS:
            draws[m].append(res[m])
    q = [100 * alpha / 2, 100 * (1 - alpha / 2)]
    return {m: tuple(float(v) for v in np.nanpercentile(d, q)) for m, d in draws.items()}


def cross_validate(pipe, X, y, groups, n_splits: int = config.N_FOLDS, n_repeats: int = config.N_REPEATS,
                   seed: int = config.SEED, threshold: float = 0.5, n_boot: int = config.N_BOOT) -> CVResult:
    """Repeated stratified patient-grouped K-fold (repeat r shuffles with seed + r). The pipeline is cloned and
    refit per fold, so every learned preprocessing step (scaler, SMOTE, pruning, ...) only ever sees that
    fold's training patients. An estimator whose fit takes `groups` gets the training patients' groups (for
    inner grouped CV); one exposing `threshold_` after fit is scored at its own fold-learned threshold."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    groups = np.asarray(groups)
    proba = np.full((n_repeats, len(y)), np.nan)
    fold = np.full((n_repeats, len(y)), -1)
    thr = np.full((n_repeats, len(y)), float(threshold))
    takes_groups = "groups" in inspect.signature(pipe.fit).parameters
    fold_metrics, ratios = [], []
    for r in range(n_repeats):
        cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed + r)
        for k, (tr, te) in enumerate(cv.split(X, y, groups)):
            assert not set(groups[tr]) & set(groups[te]), "patient leaked across folds"
            model = clone(pipe).fit(X[tr], y[tr], **({"groups": groups[tr]} if takes_groups else {}))
            proba[r, te] = model.predict_proba(X[te])[:, 1]
            fold[r, te] = k
            thr[r, te] = getattr(model, "threshold_", threshold)
            ratios.append(len(te) / len(tr))
            info = model.fold_info() if hasattr(model, "fold_info") else {}
            prune = getattr(model, "named_steps", {}).get("prune")
            if prune is not None:
                info["features"] = prune.keep_
            fold_metrics.append({"repeat": r, "seed": seed + r, "fold": k, "n": int(len(te)),
                                 **_jsonable(metrics_at(y[te], proba[r, te], thr[r, te])), **info})
    pooled = _jsonable(metrics_at(y, proba[0], thr[0]))
    ci = bootstrap_ci(y, proba[0], groups, thr[0], n_boot, seed)
    return CVResult(proba, fold, fold_metrics, pooled, thr, ci, float(np.mean(ratios)))


def _jsonable(d: dict) -> dict:
    return {k: (None if isinstance(v, float) and np.isnan(v) else float(v)) if k in METRICS else v
            for k, v in d.items()}
