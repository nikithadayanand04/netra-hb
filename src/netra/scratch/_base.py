import inspect

import numpy as np


class ScratchEstimator:
    """Minimal get_params/set_params so sklearn.clone and imblearn Pipelines accept these models."""

    def get_params(self, deep: bool = True) -> dict:
        names = [p for p in inspect.signature(type(self).__init__).parameters if p != "self"]
        return {n: getattr(self, n) for n in names}

    def set_params(self, **params) -> "ScratchEstimator":
        for k, v in params.items():
            setattr(self, k, v)
        return self

    def __repr__(self) -> str:
        args = ", ".join(f"{k}={v!r}" for k, v in self.get_params().items())
        return f"{type(self).__name__}({args})"


class ScratchClassifier(ScratchEstimator):
    _estimator_type = "classifier"

    def predict(self, X) -> np.ndarray:
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]

    def score(self, X, y) -> float:
        return float(np.mean(self.predict(X) == np.asarray(y)))


def as_float(X) -> np.ndarray:
    return np.asarray(X, dtype=float)
