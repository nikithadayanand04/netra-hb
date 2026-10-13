import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin

from netra.evaluate import cross_validate
from netra.tuning import TunedScreen, candidates, sens_floor_threshold

COLS = ["lab_a_med", "R_med", "G_med"]


def _data(n: int = 120):
    rng = np.random.default_rng(1)
    X = rng.normal(size=(n, 3))
    y = (X[:, 0] + rng.normal(0, 0.8, n) > 0.3).astype(int)
    return X, y, np.repeat(np.arange(n // 2), 2)


def test_threshold_reaches_floor_with_best_specificity():
    y = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0])
    p = np.array([0.9, 0.8, 0.7, 0.6, 0.1, 0.65, 0.5, 0.3, 0.2])
    t = sens_floor_threshold(y, p, 0.8)
    assert t == 0.55
    assert (p[y == 1] >= t).mean() >= 0.8


class _GroupSpy(ClassifierMixin, BaseEstimator):
    seen: list = []

    def __init__(self, a: int = 0):
        self.a = a

    def fit(self, X, y):
        _GroupSpy.seen.append(set(X[:, 0].round(6)))
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X):
        p = 1 / (1 + np.exp(-X[:, 1]))
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


def test_tuning_never_sees_outer_test_rows():
    X, y, g = _data()
    X = np.column_stack([np.arange(len(y)), X[:, 0]])
    _GroupSpy.seen = []
    res = cross_validate(TunedScreen({"spy": (_GroupSpy(), {"a": [0, 1]})}, n_jobs=1), X, y, g,
                         n_repeats=1, n_boot=10)
    outer_test = [set(np.flatnonzero(res.fold[0] == k)) for k in range(5)]
    per_fold = len(_GroupSpy.seen) // 5
    for k, test_rows in enumerate(outer_test):
        for seen in _GroupSpy.seen[k * per_fold:(k + 1) * per_fold]:
            assert not seen & test_rows
    assert all(0 < f["threshold"] < 1 for f in res.fold_metrics)
    assert not np.allclose(res.threshold[0], 0.5)


def test_soft_vote_ensemble_fits_and_keeps_feature_list():
    X, y, g = _data()
    cands = candidates(COLS, ["logreg", "knn", "decision_tree", "gaussian_nb"])
    cands = {n: (p, {k: v[:2] for k, v in grid.items()}) for n, (p, grid) in cands.items()}
    m = TunedScreen(cands, top_k=3, n_jobs=1).fit(X, y, g)
    assert len(m.members_) == 3
    assert set(m.kept_features()) <= set(COLS)
    p = m.predict_proba(X)[:, 1]
    assert ((p > 0) & (p < 1)).all()
    assert (y[p >= m.threshold_] == 1).sum() / y.sum() >= 0.7
