import numpy as np

from ._base import ScratchEstimator, as_float


def _sq_dists(X: np.ndarray, C: np.ndarray) -> np.ndarray:
    return ((X[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)


def kmeans_plusplus(X: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    centers = [X[rng.integers(len(X))]]
    for _ in range(1, k):
        d2 = _sq_dists(X, np.array(centers)).min(axis=1)
        centers.append(X[rng.choice(len(X), p=d2 / d2.sum())] if d2.sum() > 0 else X[rng.integers(len(X))])
    return np.array(centers)


def _lloyd(X: np.ndarray, centers: np.ndarray, max_iter: int, tol: float):
    sse_history = []
    for _ in range(max_iter):
        d2 = _sq_dists(X, centers)
        labels = d2.argmin(axis=1)
        sse_history.append(float(d2[np.arange(len(X)), labels].sum()))
        new = np.array([X[labels == j].mean(axis=0) if np.any(labels == j) else centers[j]
                        for j in range(len(centers))])
        shift = ((new - centers) ** 2).sum()
        centers = new
        if shift <= tol:
            break
    d2 = _sq_dists(X, centers)
    labels = d2.argmin(axis=1)
    return centers, labels, float(d2[np.arange(len(X)), labels].sum()), sse_history


class KMeans(ScratchEstimator):
    """Lloyd's algorithm with k-means++ init; keeps the best of n_init runs. sse_history_ is SSE per iteration."""

    def __init__(self, n_clusters: int = 2, n_init: int = 10, max_iter: int = 300, tol: float = 1e-4,
                 random_state: int | None = None, verbose: bool = False):
        self.n_clusters = n_clusters
        self.n_init = n_init
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.verbose = verbose

    def fit(self, X, y=None) -> "KMeans":
        X = as_float(X)
        rng = np.random.default_rng(self.random_state)
        tol = self.tol * X.var(axis=0).mean()   # sklearn scales tol by mean feature variance
        best = None
        for _ in range(self.n_init):
            run = _lloyd(X, kmeans_plusplus(X, self.n_clusters, rng), self.max_iter, tol)
            if best is None or run[2] < best[2]:
                best = run
        self.cluster_centers_, self.labels_, self.inertia_, self.sse_history_ = best
        self.n_iter_ = len(self.sse_history_)
        if self.verbose:
            self.summary()
        return self

    def predict(self, X) -> np.ndarray:
        return _sq_dists(as_float(X), self.cluster_centers_).argmin(axis=1)

    def transform(self, X) -> np.ndarray:
        return np.sqrt(_sq_dists(as_float(X), self.cluster_centers_))

    def fit_predict(self, X, y=None) -> np.ndarray:
        return self.fit(X).labels_

    def summary(self) -> None:
        print(f"KMeans k={self.n_clusters}  iters={self.n_iter_}  SSE={self.inertia_:.4f}")
        for i, s in enumerate(self.sse_history_, 1):
            print(f"  iter {i:>3}: SSE = {s:.4f}")


class BisectingKMeans(ScratchEstimator):
    """Repeatedly 2-means-split the cluster with the largest SSE. predict() descends the split tree, like sklearn."""

    def __init__(self, n_clusters: int = 2, n_init: int = 1, max_iter: int = 300, tol: float = 1e-4,
                 random_state: int | None = None, verbose: bool = False):
        self.n_clusters = n_clusters
        self.n_init = n_init
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.verbose = verbose

    def fit(self, X, y=None) -> "BisectingKMeans":
        X = as_float(X)
        rng = np.random.default_rng(self.random_state)
        root = {"center": X.mean(axis=0), "idx": np.arange(len(X))}
        root["sse"] = float(((X - root["center"]) ** 2).sum())
        leaves = [root]
        self.sse_history_ = [root["sse"]]
        while len(leaves) < self.n_clusters:
            node = max(leaves, key=lambda n: n["sse"])
            sub = X[node["idx"]]
            km = KMeans(2, n_init=self.n_init, max_iter=self.max_iter, tol=self.tol,
                        random_state=int(rng.integers(2**31))).fit(sub)
            node["children"] = []
            for j in range(2):
                m = km.labels_ == j
                c = km.cluster_centers_[j]
                node["children"].append({"center": c, "idx": node["idx"][m],
                                         "sse": float(((sub[m] - c) ** 2).sum())})
            leaves.remove(node)
            leaves.extend(node["children"])
            self.sse_history_.append(sum(n["sse"] for n in leaves))
        for i, leaf in enumerate(leaves):
            leaf["label"] = i
        self.tree_ = root
        self.cluster_centers_ = np.array([leaf["center"] for leaf in leaves])
        self.labels_ = self.predict(X)
        self.inertia_ = float(((X - self.cluster_centers_[self.labels_]) ** 2).sum())
        if self.verbose:
            self.summary()
        return self

    def predict(self, X) -> np.ndarray:
        X = as_float(X)
        out = np.empty(len(X), dtype=int)
        for i, x in enumerate(X):
            node = self.tree_
            while "children" in node:
                node = min(node["children"], key=lambda c: ((x - c["center"]) ** 2).sum())
            out[i] = node["label"]
        return out

    def fit_predict(self, X, y=None) -> np.ndarray:
        return self.fit(X).labels_

    def summary(self) -> None:
        print(f"BisectingKMeans k={self.n_clusters}  SSE={self.inertia_:.4f}")
        for k, s in enumerate(self.sse_history_, 1):
            print(f"  {k:>2} clusters: SSE = {s:.4f}")
