import numpy as np

from ._base import ScratchClassifier, as_float


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return np.where(z >= 0, 1 / (1 + np.exp(-np.abs(z))), np.exp(-np.abs(z)) / (1 + np.exp(-np.abs(z))))


class LogisticRegression(ScratchClassifier):
    """Binary logistic regression, batch gradient descent on mean log-loss + ||w||^2 / (2 C n) (bias unpenalised).

    Same optimum as sklearn's LogisticRegression(C=C, penalty="l2"). lr="auto" uses step 1/L, where
    L = lambda_max(X1^T X1 / n) / 4 + 1/(C n) bounds the loss curvature (X1 = X with a bias column), so the
    descent is guaranteed stable. Stops when the largest gradient component falls below tol.
    """

    def __init__(self, C: float = 1.0, lr: float | str = "auto", max_iter: int = 20000, tol: float = 1e-6,
                 verbose: bool = False):
        self.C = C
        self.lr = lr
        self.max_iter = max_iter
        self.tol = tol
        self.verbose = verbose

    def fit(self, X, y) -> "LogisticRegression":
        X = as_float(X)
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        if len(self.classes_) != 2:
            raise ValueError("binary classification only")
        t = (y == self.classes_[1]).astype(float)
        n, d = X.shape
        w, b = np.zeros(d), 0.0
        lam = 1.0 / (self.C * n)
        if self.lr == "auto":
            X1 = np.column_stack([X, np.ones(n)])
            self.lr_ = 1.0 / (np.linalg.eigvalsh(X1.T @ X1 / n).max() / 4 + lam)
        else:
            self.lr_ = float(self.lr)
        self.loss_history_ = []
        self.converged_ = False
        for self.n_iter_ in range(1, self.max_iter + 1):
            p = _sigmoid(X @ w + b)
            err = p - t
            gw = X.T @ err / n + lam * w
            gb = err.mean()
            w -= self.lr_ * gw
            b -= self.lr_ * gb
            eps = 1e-15
            loss = -np.mean(t * np.log(p + eps) + (1 - t) * np.log(1 - p + eps)) + 0.5 * lam * w @ w
            self.loss_history_.append(float(loss))
            if max(np.abs(gw).max(), abs(gb)) < self.tol:
                self.converged_ = True
                break
        self.coef_ = w.reshape(1, -1)
        self.intercept_ = np.array([b])
        if self.verbose:
            self.summary()
        return self

    def decision_function(self, X) -> np.ndarray:
        return as_float(X) @ self.coef_[0] + self.intercept_[0]

    def predict_proba(self, X) -> np.ndarray:
        p1 = _sigmoid(self.decision_function(X))
        return np.column_stack([1 - p1, p1])

    def summary(self, feature_names: list[str] | None = None) -> None:
        names = feature_names or [f"x{i}" for i in range(self.coef_.shape[1])]
        print(f"LogisticRegression  C={self.C}  lr={self.lr_:.4f}  iters={self.n_iter_}"
              f"{'' if self.converged_ else ' (not converged)'}  final loss={self.loss_history_[-1]:.5f}")
        print(f"  bias = {self.intercept_[0]:+.4f}")
        for name, w in zip(names, self.coef_[0]):
            print(f"  w[{name}] = {w:+.4f}")
