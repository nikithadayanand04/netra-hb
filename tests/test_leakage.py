import numpy as np
import pandas as pd
import pytest

import config
from netra.evaluate import cross_validate
from netra.features import prune_redundant
from netra.models import build_models, pruner
from scripts.extract_features import find_col


def test_find_col_matches_whole_words_only():
    df = pd.DataFrame(columns=["Image_ID", "File_Name", "Folder_Label", "Hb_g_dl"])
    assert find_col(df, None, ("age",)) is None
    assert find_col(pd.DataFrame(columns=["Image_ID", "Age_months"]), None, ("age",)) == "Age_months"
    assert find_col(pd.DataFrame(columns=["Gender"]), None, ("sex", "gender")) == "Gender"


def _redundant_frame(n: int = 80) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    a = rng.normal(size=n)
    return pd.DataFrame({"lab_a_med": a, "R_med": a + rng.normal(0, 1e-3, n), "G_med": rng.normal(size=n)})


def test_pruner_matches_prune_redundant_on_training_rows():
    X = _redundant_frame()
    p = pruner(list(X.columns)).fit(X.to_numpy())
    keep, _ = prune_redundant(X, config.INTERPRETABILITY, config.REDUNDANCY_RHO)
    assert p.keep_ == keep == ["lab_a_med", "G_med"]
    assert p.transform(X.to_numpy()).shape == (len(X), 2)


def test_pruning_runs_inside_each_fold():
    X = _redundant_frame()
    y = (X["G_med"] > 0).astype(int).to_numpy()
    pipe = build_models(columns=list(X.columns))["logreg"]
    assert pipe.steps[0][0] == "prune"
    res = cross_validate(pipe, X.to_numpy(), y, np.arange(len(X)), n_boot=10)
    assert all(f["features"] == ["lab_a_med", "G_med"] for f in res.fold_metrics)


def test_kept_duplicates_share_a_cv_group():
    log_path = config.OUT_DIR / "cleaning_log.csv"
    if not (config.FEATURES_ALL_CSV.exists() and log_path.exists()):
        pytest.skip("features CSV not built (run scripts.extract_features)")
    df = pd.read_csv(config.FEATURES_ALL_CSV)
    log = pd.read_csv(log_path)
    assert "cv_group" in df
    kept = df.merge(log[["id", "dup_group"]], left_on="patient_id", right_on="id")
    assert (kept[kept.dup_group >= 0].groupby("dup_group")["cv_group"].nunique() <= 1).all()
