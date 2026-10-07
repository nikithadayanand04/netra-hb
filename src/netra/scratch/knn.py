import numpy as np

from ._base import ScratchClassifier, as_float


def pairwise_distances(A: np.ndarray, B: np.ndarray, metric: str) -> np.ndarray:
    diff = A[:, None, :] - B[None, :, :]
    if metric == "euclidean":
        return np.sqrt((diff ** 2).sum(axis=2))
    if metric == "manhattan":
        return np.abs(diff).sum(axis=2)
    raise ValueError(f"unknown metric {metric!r}")


class KNN(ScratchClassifier):
    """k-nearest neighbours; weights="distance" uses 1/d, and exact matches (d=0) take all the vote."""

    def __init__(self, n_neighbors: int = 5, metric: str = "euclidean", weights: str = "uniform"):
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.weights = weights

    def fit(self, X, y) -> "KNN":
        self.X_ = as_float(X)
        y = np.asarray(y)
        self.classes_, self.y_ = np.unique(y, return_inverse=True)
        return self

    def kneighbors(self, X) -> tuple[np.ndarray, np.ndarray]:
        D = pairwise_distances(as_float(X), self.X_, self.metric)
        idx = np.argsort(D, axis=1, kind="stable")[:, : self.n_neighbors]
        return np.take_along_axis(D, idx, axis=1), idx

    def predict_proba(self, X) -> np.ndarray:
        dist, idx = self.kneighbors(X)
        if self.weights == "uniform":
            w = np.ones_like(dist)
        elif self.weights == "distance":
            with np.errstate(divide="ignore"):
                w = 1.0 / dist
            exact = np.isinf(w)
            w[exact.any(axis=1)] = exact[exact.any(axis=1)].astype(float)
        else:
            raise ValueError(f"unknown weights {self.weights!r}")
        votes = np.zeros((len(idx), len(self.classes_)))
        for k in range(len(self.classes_)):
            votes[:, k] = (w * (self.y_[idx] == k)).sum(axis=1)
        return votes / votes.sum(axis=1, keepdims=True)
