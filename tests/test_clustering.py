import numpy as np
import pytest

from netra import clustering as C


def test_purity_and_entropy_extremes():
    clusters = np.array([0, 0, 1, 1])
    assert C.purity(clusters, np.array(["a", "a", "b", "b"])) == 1.0
    assert C.entropy(clusters, np.array(["a", "a", "b", "b"])) == 0.0
    assert C.purity(clusters, np.array(["a", "b", "a", "b"])) == 0.5
    assert C.entropy(clusters, np.array(["a", "b", "a", "b"])) == pytest.approx(1.0)


def test_contingency_ignores_pandas_index():
    import pandas as pd
    classes = pd.Series(["a", "a", "b", "b"], index=[10, 11, 12, 13])
    assert C.contingency(np.array([0, 0, 1, 1]), classes).to_numpy().sum() == 4


def test_elbow_on_clear_knee():
    assert C.elbow_k([1, 2, 3, 4, 5, 6], [100, 30, 20, 15, 12, 10]) == 2


def test_pallor_names_order_by_redness():
    feats = ["lab_a_med", "lab_L_med"]
    centers = np.array([[1.5, 0.0], [-1.0, 0.0], [0.2, 0.0]])
    assert C.pallor_names(centers, feats) == {1: "Pale", 2: "Intermediate", 0: "Red"}


def test_sorted_proximity_groups_clusters():
    rng = np.random.default_rng(0)
    Z = np.vstack([rng.normal(0, 0.1, (5, 2)), rng.normal(5, 0.1, (5, 2))])
    labels = np.array([1] * 5 + [0] * 5)
    D, lab = C.sorted_proximity(Z, labels, order=[1, 0])
    assert list(lab) == [1] * 5 + [0] * 5
    assert D[:5, :5].mean() < D[:5, 5:].mean()
