import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold, cross_val_predict

import config
from netra.models import build_models

PROBA_CLIP = 1e-3

# Searched inside each training fold only. Bagging/AdaBoost "estimator__max_depth" is the base tree's depth.
GRIDS = {
    "decision_tree": {"clf__criterion": ["gini", "entropy"], "clf__max_depth": [2, 3, 4, 5, 6, 8, None],
                      "clf__min_samples_leaf": [1, 5, 10], "clf__ccp_alpha": [0.0, 0.005, 0.01, 0.02]},
    "knn": {"clf__n_neighbors": [3, 5, 7, 9, 11, 15, 21, 25, 31],
            "clf__metric": ["euclidean", "manhattan", "chebyshev"], "clf__weights": ["uniform", "distance"]},
    "gaussian_nb": {"clf__var_smoothing": [1e-9, 1e-6, 1e-3]},
    "logreg": {"clf__C": [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]},
    "bagging": {"clf__estimator__max_depth": [3, 5, None], "clf__estimator__min_samples_leaf": [1, 3, 5],
                "clf__max_samples": [0.6, 1.0]},
    "random_forest": {"clf__max_depth": [4, 8, None], "clf__min_samples_leaf": [1, 3, 5],
                      "clf__max_features": ["sqrt", 0.5]},
    "gradient_boosting": {"clf__n_estimators": [100, 300], "clf__max_depth": [1, 2, 3],
                          "clf__learning_rate": [0.03, 0.1]},
    "adaboost": {"clf__estimator__max_depth": [1, 2, 3], "clf__n_estimators": [100, 300],
                 "clf__learning_rate": [0.1, 0.5, 1.0]},
}


def candidates(columns: list[str], names=None, seed: int = config.SEED) -> dict[str, tuple]:
    """(pipeline, grid) per model family; each pipeline starts with in-fold redundancy pruning over `columns`."""
    models = build_models(seed, columns)
    out = {}
    for name in names or GRIDS:
        pipe = models[name]
        if name in ("bagging", "random_forest"):
            pipe = pipe.set_params(clf__n_jobs=1)   # parallelism lives in the grid search
        out[name] = (pipe, GRIDS[name])
    return out


def sens_floor_threshold(y: np.ndarray, proba: np.ndarray, floor: float = config.SENS_FLOOR) -> float:
    """Highest threshold whose sensitivity is still >= floor (specificity only rises with the threshold), placed
    halfway to the next lower score so it does not sit exactly on a training point."""
    pos = np.sort(proba[y == 1])[::-1]
    t = pos[int(np.ceil(floor * len(pos))) - 1]
    below = proba[proba < t]
    return float((t + below.max()) / 2) if len(below) else float(t)


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, PROBA_CLIP, 1 - PROBA_CLIP)
    return np.log(p / (1 - p)).reshape(-1, 1)


class TunedScreen(ClassifierMixin, BaseEstimator):
    """Everything learned from the training rows it is given, nothing else:
    1. grid-search each candidate with inner StratifiedGroupKFold (ROC-AUC),
    2. keep the best (top_k=1) or soft-vote the top_k by inner ROC-AUC,
    3. Platt-calibrate on that model's inner out-of-fold probabilities,
    4. set the threshold on the calibrated out-of-fold probabilities to reach sens_floor with best specificity,
    5. refit the chosen model on all training rows."""

    def __init__(self, candidates=None, top_k: int = 1, sens_floor: float = config.SENS_FLOOR,
                 n_inner: int = config.N_FOLDS, seed: int = config.SEED, n_jobs: int = -1):
        self.candidates = candidates
        self.top_k = top_k
        self.sens_floor = sens_floor
        self.n_inner = n_inner
        self.seed = seed
        self.n_jobs = n_jobs

    def fit(self, X, y, groups=None) -> "TunedScreen":
        X, y = np.asarray(X, float), np.asarray(y)
        groups = np.arange(len(y)) if groups is None else np.asarray(groups)
        inner = list(StratifiedGroupKFold(self.n_inner, shuffle=True, random_state=self.seed).split(X, y, groups))
        self.search_ = {}
        for name, (pipe, grid) in self.candidates.items():
            if len(self.candidates) == 1 and not grid:   # fixed model: nothing to search or rank
                self.search_[name] = {"params": {}, "inner_roc_auc": float("nan")}
                continue
            gs = GridSearchCV(clone(pipe), grid, scoring="roc_auc", cv=inner, n_jobs=self.n_jobs, refit=False)
            gs.fit(X, y)
            self.search_[name] = {"params": gs.best_params_, "inner_roc_auc": float(gs.best_score_)}
        ranked = sorted(self.search_, key=lambda n: -self.search_[n]["inner_roc_auc"])
        self.members_ = ranked[:self.top_k]
        tuned = [(n, clone(self.candidates[n][0]).set_params(**self.search_[n]["params"])) for n in self.members_]
        model = tuned[0][1] if len(tuned) == 1 else VotingClassifier(tuned, voting="soft")

        oof = cross_val_predict(model, X, y, cv=inner, method="predict_proba", n_jobs=self.n_jobs)[:, 1]
        self.calibrator_ = LogisticRegression(C=1e6).fit(_logit(oof), y)
        self.oof_ = self.calibrator_.predict_proba(_logit(oof))[:, 1]
        self.threshold_ = sens_floor_threshold(y, self.oof_, self.sens_floor)
        self.model_ = model.fit(X, y)
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X):
        raw = self.model_.predict_proba(np.asarray(X, float))[:, 1]
        return self.calibrator_.predict_proba(_logit(raw))

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= self.threshold_).astype(int)

    def fold_info(self) -> dict:
        return {"members": self.members_, "threshold": self.threshold_,
                "params": {n: self.search_[n]["params"] for n in self.members_},
                "inner_roc_auc": {n: s["inner_roc_auc"] for n, s in self.search_.items()}}

    def kept_features(self) -> list[str]:
        steps = [self.model_] if not isinstance(self.model_, VotingClassifier) else self.model_.estimators_
        return sorted({f for s in steps for f in s.named_steps["prune"].keep_})


class LateFusion(ClassifierMixin, BaseEstimator):
    """Average of per-site calibrated probabilities. Each block is its own TunedScreen on its own columns (so each
    keeps its own <= 15-feature budget); the fused threshold is set on the mean of their inner out-of-fold
    probabilities, which share inner splits because the inner CV depends only on y and groups."""

    def __init__(self, blocks=None, sens_floor: float = config.SENS_FLOOR):
        self.blocks = blocks
        self.sens_floor = sens_floor

    def fit(self, X, y, groups=None) -> "LateFusion":
        X = np.asarray(X, float)
        self.models_ = [clone(m).fit(X[:, idx], y, groups) for idx, m in self.blocks]
        self.threshold_ = sens_floor_threshold(np.asarray(y), np.mean([m.oof_ for m in self.models_], axis=0),
                                               self.sens_floor)
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X):
        X = np.asarray(X, float)
        p = np.mean([m.predict_proba(X[:, idx])[:, 1] for (idx, _), m in zip(self.blocks, self.models_)], axis=0)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= self.threshold_).astype(int)
