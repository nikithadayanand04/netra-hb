from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (AdaBoostClassifier, BaggingClassifier, GradientBoostingClassifier,
                              RandomForestClassifier)
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

import config
from netra import scratch
from netra.features import RedundancyPruner

# Imbalance: class_weight="balanced" where the estimator supports it, SMOTE (inside the pipeline, so only on
# training folds) where it does not. Scratch models mirror their sklearn twin's scaling and k / C settings.
IMBALANCE = {
    "all_normal": "-", "decision_tree": "class_weight", "knn": "SMOTE", "gaussian_nb": "SMOTE",
    "logreg": "class_weight", "bagging": "class_weight", "adaboost": "SMOTE",
    "gradient_boosting": "SMOTE", "random_forest": "class_weight",
    "scratch_logreg": "SMOTE", "scratch_nb": "SMOTE", "scratch_knn": "SMOTE",
}
LABELS = {
    "all_normal": "All-normal (dummy)", "decision_tree": "Decision tree", "knn": "KNN",
    "gaussian_nb": "Gaussian NB", "logreg": "Logistic regression", "bagging": "Bagging",
    "adaboost": "AdaBoost", "gradient_boosting": "Gradient boosting", "random_forest": "Random forest",
    "scratch_logreg": "Scratch LogReg", "scratch_nb": "Scratch NB", "scratch_knn": "Scratch KNN",
}
K = 15


class Scratch(ClassifierMixin, BaseEstimator):
    """Wraps a netra.scratch model so sklearn/imblearn treat it as a fitted classifier (scratch/ stays sklearn-free)."""

    def __init__(self, model=None):
        self.model = model

    def fit(self, X, y) -> "Scratch":
        self.model_ = clone(self.model).fit(X, y)
        self.classes_ = self.model_.classes_
        return self

    def predict_proba(self, X):
        return self.model_.predict_proba(X)

    def predict(self, X):
        return self.model_.predict(X)


def _smote(seed: int) -> SMOTE:
    return SMOTE(random_state=seed)


def pruner(columns: list[str]) -> RedundancyPruner:
    return RedundancyPruner(tuple(columns), tuple(config.INTERPRETABILITY), config.REDUNDANCY_RHO,
                            tuple(config.COLLINEAR_DROP))


def build_models(seed: int = config.SEED, columns: list[str] | None = None) -> dict[str, Pipeline]:
    """With `columns`, every pipeline starts with in-fold redundancy pruning over those candidate columns."""
    models = _models(seed)
    if columns is None:
        return models
    return {name: Pipeline([("prune", pruner(columns)), *p.steps]) for name, p in models.items()}


def _models(seed: int) -> dict[str, Pipeline]:
    tree = dict(class_weight="balanced", random_state=seed)
    return {
        "all_normal": Pipeline([("clf", DummyClassifier(strategy="constant", constant=0))]),
        "decision_tree": Pipeline([("clf", DecisionTreeClassifier(max_depth=4, min_samples_leaf=5, **tree))]),
        "knn": Pipeline([("scale", StandardScaler()), ("smote", _smote(seed)),
                         ("clf", KNeighborsClassifier(n_neighbors=K))]),
        "gaussian_nb": Pipeline([("smote", _smote(seed)), ("clf", GaussianNB())]),
        "logreg": Pipeline([("scale", StandardScaler()),
                            ("clf", LogisticRegression(C=1.0, class_weight="balanced", max_iter=5000))]),
        "bagging": Pipeline([("clf", BaggingClassifier(DecisionTreeClassifier(min_samples_leaf=3, **tree),
                                                       n_estimators=200, random_state=seed, n_jobs=-1))]),
        # SMOTE, not class_weight: AdaBoost scores each stump by plain weighted error, so a class-weighted stump
        # can look "worse than random" and abort the fit
        "adaboost": Pipeline([("smote", _smote(seed)),
                              ("clf", AdaBoostClassifier(DecisionTreeClassifier(max_depth=1, random_state=seed),
                                                         n_estimators=200, learning_rate=0.5,
                                                         random_state=seed))]),
        "gradient_boosting": Pipeline([("smote", _smote(seed)),
                                       ("clf", GradientBoostingClassifier(n_estimators=150, max_depth=2,
                                                                          learning_rate=0.05, subsample=0.8,
                                                                          random_state=seed))]),
        "random_forest": Pipeline([("clf", RandomForestClassifier(n_estimators=300, min_samples_leaf=3,
                                                                  max_features="sqrt", n_jobs=-1,
                                                                  class_weight="balanced_subsample",
                                                                  random_state=seed))]),
        "scratch_logreg": Pipeline([("scale", StandardScaler()), ("smote", _smote(seed)),
                                    ("clf", Scratch(scratch.LogisticRegression(C=1.0)))]),
        "scratch_nb": Pipeline([("smote", _smote(seed)), ("clf", Scratch(scratch.GaussianNaiveBayes()))]),
        "scratch_knn": Pipeline([("scale", StandardScaler()), ("smote", _smote(seed)),
                                 ("clf", Scratch(scratch.KNN(n_neighbors=K)))]),
    }
