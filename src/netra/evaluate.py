from dataclasses import dataclass, field

import numpy as np
from sklearn.base import clone
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

import config

METRICS = ["sensitivity", "specificity", "roc_auc", "pr_auc", "f1"]


@dataclass
class CVResult:
    proba: np.ndarray
    fold: np.ndarray
    fold_metrics: list[dict]
    pooled: dict
    ci: dict = field(default_factory=dict)

    def summary(self) -> dict:
        per_fold = {m: [np.nan if f[m] is None else f[m] for f in self.fold_metrics] for m in METRICS}
        return {
            "pooled": {m: {"value": self.pooled[m], "ci_low": self.ci[m][0], "ci_high": self.ci[m][1]}
                       for m in METRICS},
            "confusion_matrix": self.pooled["confusion_matrix"],
            "fold_mean": {m: float(np.nanmean(v)) for m, v in per_fold.items()},
            "fold_sd": {m: float(np.nanstd(v, ddof=1)) for m, v in per_fold.items()},
            "folds": self.fold_metrics,
        }


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
        res = metrics_at(y[idx], proba[idx], threshold)
        for m in METRICS:
            draws[m].append(res[m])
    q = [100 * alpha / 2, 100 * (1 - alpha / 2)]
    return {m: tuple(float(v) for v in np.nanpercentile(d, q)) for m, d in draws.items()}


def cross_validate(pipe, X, y, groups, n_splits: int = config.N_FOLDS, seed: int = config.SEED,
                   threshold: float = 0.5, n_boot: int = config.N_BOOT) -> CVResult:
    """Stratified patient-grouped K-fold. The pipeline is cloned and refit per fold, so every learned
    preprocessing step (scaler, SMOTE, ...) only ever sees that fold's training patients."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    groups = np.asarray(groups)
    proba = np.full(len(y), np.nan)
    fold = np.full(len(y), -1)
    fold_metrics = []
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for k, (tr, te) in enumerate(cv.split(X, y, groups)):
        assert not set(groups[tr]) & set(groups[te]), "patient leaked across folds"
        model = clone(pipe).fit(X[tr], y[tr])
        proba[te] = model.predict_proba(X[te])[:, 1]
        fold[te] = k
        fold_metrics.append({"fold": k, "n": int(len(te)), **_jsonable(metrics_at(y[te], proba[te], threshold))})
    pooled = _jsonable(metrics_at(y, proba, threshold))
    return CVResult(proba, fold, fold_metrics, pooled, bootstrap_ci(y, proba, groups, threshold, n_boot, seed))


def _jsonable(d: dict) -> dict:
    return {k: (None if isinstance(v, float) and np.isnan(v) else float(v)) if k in METRICS else v
            for k, v in d.items()}
