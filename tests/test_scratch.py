import numpy as np
import pandas as pd
import pytest
from sklearn import cluster, linear_model, naive_bayes, neighbors
from sklearn.base import clone
from sklearn.metrics import adjusted_rand_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler

import config
from netra import scratch
from netra.scratch.kmeans import _lloyd, kmeans_plusplus


@pytest.fixture(scope="module")
def split():
    if not config.FEATURES_CSV.exists():
        pytest.skip("features CSV not built (run scripts.extract_features)")
    df = pd.read_csv(config.FEATURES_CSV)
    X = df[config.MODEL_FEATURES].to_numpy(float)
    y = df["label"].to_numpy()
    cv = StratifiedGroupKFold(n_splits=config.N_FOLDS, shuffle=True, random_state=config.SEED)
    tr, te = next(cv.split(X, y, groups=df["patient_id"]))
    scaler = StandardScaler().fit(X[tr])
    return scaler.transform(X[tr]), y[tr], scaler.transform(X[te]), y[te]


def _auc(model, Xte, yte) -> float:
    return roc_auc_score(yte, model.predict_proba(Xte)[:, 1])


@pytest.mark.parametrize("C", [0.1, 1.0])
def test_logistic_regression_matches_sklearn(split, C):
    Xtr, ytr, Xte, yte = split
    ours = scratch.LogisticRegression(C=C).fit(Xtr, ytr)
    ref = linear_model.LogisticRegression(C=C, tol=1e-10, max_iter=10000).fit(Xtr, ytr)
    np.testing.assert_allclose(ours.coef_, ref.coef_, atol=2e-3)
    np.testing.assert_allclose(ours.intercept_, ref.intercept_, atol=2e-3)
    np.testing.assert_allclose(ours.predict_proba(Xte), ref.predict_proba(Xte), atol=1e-3)
    assert np.mean(ours.predict(Xte) == ref.predict(Xte)) >= 0.98
    assert abs(_auc(ours, Xte, yte) - _auc(ref, Xte, yte)) < 0.005
    assert ours.loss_history_[-1] <= ours.loss_history_[0]
    assert ours.converged_ and ours.n_iter_ < 5000
    assert np.all(np.diff(ours.loss_history_) <= 1e-12)


def test_gaussian_nb_matches_sklearn(split):
    Xtr, ytr, Xte, yte = split
    ours = scratch.GaussianNaiveBayes().fit(Xtr, ytr)
    ref = naive_bayes.GaussianNB().fit(Xtr, ytr)
    np.testing.assert_allclose(ours.class_prior_, ref.class_prior_)
    np.testing.assert_allclose(ours.theta_, ref.theta_)
    np.testing.assert_allclose(ours.var_, ref.var_)
    np.testing.assert_allclose(ours.predict_proba(Xte), ref.predict_proba(Xte), atol=1e-8)
    np.testing.assert_array_equal(ours.predict(Xte), ref.predict(Xte))


@pytest.mark.parametrize("metric", ["euclidean", "manhattan"])
@pytest.mark.parametrize("weights", ["uniform", "distance"])
def test_knn_matches_sklearn(split, metric, weights):
    Xtr, ytr, Xte, yte = split
    ours = scratch.KNN(n_neighbors=7, metric=metric, weights=weights).fit(Xtr, ytr)
    ref = neighbors.KNeighborsClassifier(7, metric=metric, weights=weights, algorithm="brute").fit(Xtr, ytr)
    np.testing.assert_allclose(ours.predict_proba(Xte), ref.predict_proba(Xte), atol=1e-8)
    assert np.mean(ours.predict(Xte) == ref.predict(Xte)) >= 0.98
    assert abs(_auc(ours, Xte, yte) - _auc(ref, Xte, yte)) < 0.01


def test_knn_distance_weight_exact_match():
    X = np.array([[0.0], [1.0], [2.0]])
    m = scratch.KNN(n_neighbors=3, weights="distance").fit(X, [0, 1, 1])
    np.testing.assert_allclose(m.predict_proba([[0.0]]), [[1.0, 0.0]])


@pytest.mark.parametrize("k", [2, 3, 4])
def test_kmeans_matches_sklearn(split, k):
    X = np.vstack([split[0], split[2]])
    ours = scratch.KMeans(k, n_init=10, random_state=config.SEED).fit(X)
    ref = cluster.KMeans(k, n_init=10, random_state=config.SEED).fit(X)
    # different random restarts can land in different local optima, so compare loosely here ...
    assert ours.inertia_ == pytest.approx(ref.inertia_, rel=0.02)
    assert adjusted_rand_score(ours.labels_, ref.labels_) > 0.75
    assert np.all(np.diff(ours.sse_history_) <= 1e-9)
    np.testing.assert_array_equal(ours.predict(X), ours.labels_)


@pytest.mark.parametrize("k", [2, 3, 4])
def test_lloyd_same_init_identical_to_sklearn(split, k):
    # ... and exactly when both start from the same centres
    X = np.vstack([split[0], split[2]])
    init = kmeans_plusplus(X, k, np.random.default_rng(config.SEED))
    centers, labels, sse, _ = _lloyd(X, init, max_iter=300, tol=0.0)
    ref = cluster.KMeans(k, init=init, n_init=1, tol=0.0).fit(X)
    np.testing.assert_array_equal(labels, ref.labels_)
    np.testing.assert_allclose(centers, ref.cluster_centers_, atol=1e-10)
    assert sse == pytest.approx(ref.inertia_)


@pytest.mark.parametrize("k", [2, 3, 4])
def test_bisecting_kmeans_matches_sklearn(split, k):
    X = np.vstack([split[0], split[2]])
    ours = scratch.BisectingKMeans(k, n_init=5, random_state=config.SEED).fit(X)
    ref = cluster.BisectingKMeans(k, n_init=5, random_state=config.SEED).fit(X)
    assert ours.inertia_ == pytest.approx(ref.inertia_, rel=0.05)
    assert adjusted_rand_score(ours.labels_, ref.labels_) > 0.8
    assert len(ours.sse_history_) == k
    assert np.all(np.diff(ours.sse_history_) < 0)


@pytest.mark.parametrize("model", [
    scratch.LogisticRegression(C=0.5), scratch.GaussianNaiveBayes(), scratch.KNN(3, weights="distance"),
    scratch.KMeans(3), scratch.BisectingKMeans(3),
])
def test_clone_compatible(model):
    assert clone(model).get_params() == model.get_params()


def test_summaries_print_parameters(split, capsys):
    Xtr, ytr, _, _ = split
    scratch.LogisticRegression(verbose=True).fit(Xtr, ytr)
    scratch.GaussianNaiveBayes(verbose=True).fit(Xtr, ytr)
    scratch.KMeans(2, random_state=0, verbose=True).fit(Xtr)
    scratch.BisectingKMeans(3, random_state=0, verbose=True).fit(Xtr)
    out = capsys.readouterr().out
    for s in ["bias =", "w[x0]", "prior =", "var =", "iter   1: SSE", "3 clusters: SSE"]:
        assert s in out
