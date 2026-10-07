import numpy as np

from ._base import ScratchClassifier, as_float


class GaussianNaiveBayes(ScratchClassifier):
    """Gaussian NB; var_smoothing adds eps * max feature variance, as sklearn does."""

    def __init__(self, var_smoothing: float = 1e-9, verbose: bool = False):
        self.var_smoothing = var_smoothing
        self.verbose = verbose

    def fit(self, X, y) -> "GaussianNaiveBayes":
        X = as_float(X)
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        self.epsilon_ = self.var_smoothing * X.var(axis=0).max()
        self.class_prior_ = np.array([np.mean(y == c) for c in self.classes_])
        self.theta_ = np.array([X[y == c].mean(axis=0) for c in self.classes_])
        self.var_ = np.array([X[y == c].var(axis=0) for c in self.classes_]) + self.epsilon_
        if self.verbose:
            self.summary()
        return self

    def _joint_log_likelihood(self, X) -> np.ndarray:
        X = as_float(X)
        ll = -0.5 * (np.log(2 * np.pi * self.var_)[None].sum(axis=2)
                     + (((X[:, None, :] - self.theta_[None]) ** 2) / self.var_[None]).sum(axis=2))
        return ll + np.log(self.class_prior_)

    def predict_log_proba(self, X) -> np.ndarray:
        jll = self._joint_log_likelihood(X)
        m = jll.max(axis=1, keepdims=True)
        return jll - (m + np.log(np.exp(jll - m).sum(axis=1, keepdims=True)))

    def predict_proba(self, X) -> np.ndarray:
        return np.exp(self.predict_log_proba(X))

    def summary(self, feature_names: list[str] | None = None) -> None:
        names = feature_names or [f"x{i}" for i in range(self.theta_.shape[1])]
        print("GaussianNaiveBayes")
        for k, c in enumerate(self.classes_):
            print(f"  class {c}: prior = {self.class_prior_[k]:.4f}")
            for j, name in enumerate(names):
                print(f"    {name:>22}: mean = {self.theta_[k, j]:+.4f}  var = {self.var_[k, j]:.4f}")
