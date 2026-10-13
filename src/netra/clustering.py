import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn import cluster
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from netra import scratch

# Higher = redder tissue. Pallor score of a centroid = minus the mean z-score of these features.
REDNESS = ["lab_a_med", "erythema_index_med", "chrom_r_med", "lab_a_p10", "erythema_index_p10"]
PALLOR_NAMES = {
    2: ["Pale", "Red"],
    3: ["Pale", "Intermediate", "Red"],
    4: ["Very pale", "Pale", "Pink", "Red"],
    5: ["Very pale", "Pale", "Intermediate", "Pink", "Red"],
}


def make_model(kind: str, k: int, seed: int, n_init: int = 10):
    if kind == "sklearn":
        return cluster.KMeans(k, n_init=n_init, random_state=seed)
    if kind == "scratch":
        return scratch.KMeans(k, n_init=n_init, random_state=seed)
    if kind == "bisecting":
        return cluster.BisectingKMeans(k, n_init=n_init, random_state=seed)
    if kind == "scratch_bisecting":
        return scratch.BisectingKMeans(k, n_init=n_init, random_state=seed)
    raise ValueError(kind)


def pipeline(k: int, seed: int, n_init: int = 10) -> Pipeline:
    return Pipeline([("scale", StandardScaler()), ("kmeans", cluster.KMeans(k, n_init=n_init, random_state=seed))])


def k_scan(Z: np.ndarray, ks, seed: int, kinds=("sklearn", "scratch", "bisecting")) -> pd.DataFrame:
    rows = []
    for k in ks:
        for kind in kinds:
            m = make_model(kind, k, seed).fit(Z)
            rows.append({"k": k, "kind": kind, "sse": float(m.inertia_),
                         "silhouette": float(silhouette_score(Z, m.labels_))})
    return pd.DataFrame(rows)


def elbow_k(ks, sse) -> int:
    """Kneedle: the k whose (normalised) SSE lies furthest below the chord from the first to the last k."""
    k = np.asarray(ks, float)
    s = np.asarray(sse, float)
    kn = (k - k[0]) / (k[-1] - k[0])
    sn = (s - s[-1]) / (s[0] - s[-1])
    return int(k[np.argmax((1 - kn) - sn)])


def contingency(clusters: np.ndarray, classes: np.ndarray, class_order=None) -> pd.DataFrame:
    t = pd.crosstab(pd.Series(np.asarray(clusters), name="cluster"), pd.Series(np.asarray(classes), name="class"))
    return t.reindex(columns=[c for c in class_order if c in t.columns]) if class_order is not None else t


def purity(clusters: np.ndarray, classes: np.ndarray) -> float:
    t = contingency(clusters, classes).to_numpy()
    return float(t.max(axis=1).sum() / t.sum())


def entropy(clusters: np.ndarray, classes: np.ndarray) -> float:
    """Size-weighted mean of each cluster's class entropy, in bits (0 = every cluster is one class)."""
    t = contingency(clusters, classes).to_numpy(float)
    p = t / t.sum(axis=1, keepdims=True)
    e = -(np.where(p > 0, p * np.log2(np.where(p > 0, p, 1)), 0)).sum(axis=1)
    return float((t.sum(axis=1) / t.sum() * e).sum())


def class_entropy(classes: np.ndarray) -> float:
    p = pd.Series(classes).value_counts(normalize=True).to_numpy()
    return float(-(p * np.log2(p)).sum())


def permutation_null(clusters: np.ndarray, classes: np.ndarray, n: int, seed: int) -> dict:
    """Purity/entropy when class labels are shuffled: what the same cluster sizes give by chance."""
    rng = np.random.default_rng(seed)
    pur, ent = [], []
    for _ in range(n):
        c = rng.permutation(classes)
        pur.append(purity(clusters, c))
        ent.append(entropy(clusters, c))
    pur, ent = np.array(pur), np.array(ent)
    obs_p, obs_e = purity(clusters, classes), entropy(clusters, classes)
    return {"purity_null_mean": float(pur.mean()), "purity_null_p95": float(np.quantile(pur, 0.95)),
            "purity_p_value": float((1 + (pur >= obs_p).sum()) / (n + 1)),
            "entropy_null_mean": float(ent.mean()), "entropy_null_p05": float(np.quantile(ent, 0.05)),
            "entropy_p_value": float((1 + (ent <= obs_e).sum()) / (n + 1))}


def sorted_proximity(Z: np.ndarray, labels: np.ndarray, order=None) -> tuple[np.ndarray, np.ndarray]:
    """Euclidean distance matrix with points sorted by cluster (in `order`), then by distance to their centroid."""
    order = np.unique(labels) if order is None else order
    idx = []
    for c in order:
        m = np.flatnonzero(labels == c)
        d = np.linalg.norm(Z[m] - Z[m].mean(axis=0), axis=1)
        idx.extend(m[np.argsort(d)])
    idx = np.array(idx)
    return cdist(Z[idx], Z[idx]), labels[idx]


def pallor_order(centers_z: np.ndarray, features: list[str]) -> np.ndarray:
    """Cluster ids sorted from most pale to most red, by mean redness z-score of the centroid."""
    cols = [features.index(f) for f in REDNESS if f in features]
    return np.argsort(centers_z[:, cols].mean(axis=1))


def pallor_names(centers_z: np.ndarray, features: list[str]) -> dict[int, str]:
    order = pallor_order(centers_z, features)
    names = PALLOR_NAMES.get(len(order), [f"Pallor rank {i + 1}" for i in range(len(order))])
    return {int(c): names[i] for i, c in enumerate(order)}


def centroid_table(model: Pipeline, features: list[str], names: dict[int, str]) -> pd.DataFrame:
    z = model["kmeans"].cluster_centers_
    raw = model["scale"].inverse_transform(z)
    t = pd.DataFrame(raw, columns=features)
    t.insert(0, "redness_z", z[:, [features.index(f) for f in REDNESS if f in features]].mean(axis=1))
    t.insert(0, "name", [names[i] for i in range(len(t))])
    return t.loc[pallor_order(z, features)].reset_index(names="cluster")


def init_stability(Z: np.ndarray, k: int, seeds, kind: str = "sklearn") -> dict:
    """Single-init runs from different seeds: spread of SSE and pairwise ARI of the partitions."""
    runs = [make_model(kind, k, s, n_init=1).fit(Z) for s in seeds]
    sse = np.array([r.inertia_ for r in runs])
    ari = [adjusted_rand_score(a.labels_, b.labels_) for i, a in enumerate(runs) for b in runs[i + 1:]]
    return {"sse_min": float(sse.min()), "sse_max": float(sse.max()),
            "sse_rel_spread": float((sse.max() - sse.min()) / sse.min()),
            "ari_mean": float(np.mean(ari)), "ari_min": float(np.min(ari))}
