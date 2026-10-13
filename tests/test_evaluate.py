import numpy as np
import pandas as pd
import pytest
from sklearn.base import BaseEstimator, ClassifierMixin

import config
from netra.evaluate import bootstrap_ci, corrected_ci, cross_validate, metrics_at
from netra.models import build_models


def test_metrics_at_known_values():
    y = np.array([1, 1, 1, 0, 0, 0, 0])
    p = np.array([0.9, 0.8, 0.2, 0.7, 0.1, 0.1, 0.3])
    m = metrics_at(y, p)
    assert m["confusion_matrix"] == {"tn": 3, "fp": 1, "fn": 1, "tp": 2}
    assert m["sensitivity"] == pytest.approx(2 / 3)
    assert m["specificity"] == pytest.approx(3 / 4)
    assert m["f1"] == pytest.approx(2 / 3)


class _FitSpy(ClassifierMixin, BaseEstimator):
    """Records the training rows each fold sees and predicts a constant."""

    seen: list = []

    def fit(self, X, y):
        _FitSpy.seen.append(set(X[:, 0].astype(int)))
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X):
        return np.tile([0.5, 0.5], (len(X), 1))


def test_cv_never_trains_on_test_patients():
    rng = np.random.default_rng(0)
    n = 60
    groups = np.repeat(np.arange(30), 2)
    X = np.column_stack([np.arange(n), rng.normal(size=n)])
    y = (groups % 3 == 0).astype(int)
    _FitSpy.seen = []
    res = cross_validate(_FitSpy(), X, y, groups, n_repeats=3, n_boot=20)
    assert not np.isnan(res.proba).any()
    assert len(_FitSpy.seen) == len(res.fold_metrics) == 3 * config.N_FOLDS
    for i, train_rows in enumerate(_FitSpy.seen):
        r, k = divmod(i, config.N_FOLDS)
        test_rows = set(np.flatnonzero(res.fold[r] == k))
        assert not train_rows & test_rows
        assert not set(groups[list(train_rows)]) & set(groups[list(test_rows)])


def test_repeats_reshuffle_folds():
    groups = np.arange(100)
    y = (groups % 4 == 0).astype(int)
    res = cross_validate(_FitSpy(), np.column_stack([groups, groups]), y, groups, n_repeats=2, n_boot=10)
    assert [f["seed"] for f in res.fold_metrics[::config.N_FOLDS]] == [config.SEED, config.SEED + 1]
    assert not np.array_equal(res.fold[0], res.fold[1])


def test_corrected_ci_is_wider_than_naive():
    v = np.random.default_rng(2).normal(0.7, 0.05, 25)
    lo, hi = corrected_ci(v, 0.25)
    naive = 2.064 * v.std(ddof=1) / np.sqrt(25)
    assert lo < v.mean() < hi
    assert hi - lo > 2 * naive
    assert corrected_ci([0.9, 1.0, 1.0], 0.25)[1] == 1.0


def test_bootstrap_ci_brackets_point_estimate():
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, 200)
    p = np.clip(y * 0.3 + rng.uniform(0, 0.7, 200), 0, 1)
    ci = bootstrap_ci(y, p, np.arange(200), n_boot=200)
    point = metrics_at(y, p)
    for m, (lo, hi) in ci.items():
        assert lo <= point[m] <= hi


@pytest.fixture(scope="module")
def data():
    if not config.FEATURES_CSV.exists():
        pytest.skip("features CSV not built (run scripts.extract_features)")
    df = pd.read_csv(config.FEATURES_CSV)
    return df[config.MODEL_FEATURES].to_numpy(float), df["label"].to_numpy(), df["patient_id"].to_numpy()


def test_all_normal_baseline(data):
    res = cross_validate(build_models()["all_normal"], *data, n_boot=50)
    assert res.pooled["sensitivity"] == 0 and res.pooled["specificity"] == 1
    assert res.pooled["roc_auc"] == pytest.approx(0.5)


@pytest.mark.parametrize("name", ["scratch_nb", "scratch_knn"])
def test_scratch_matches_sklearn_twin(data, name):
    models = build_models()
    ours = cross_validate(models[name], *data, n_boot=10).proba
    ref = cross_validate(models[name.replace("scratch_", "").replace("nb", "gaussian_nb")], *data, n_boot=10).proba
    np.testing.assert_allclose(ours, ref, atol=1e-6)
