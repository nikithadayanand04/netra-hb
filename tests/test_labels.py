import pandas as pd
import pytest

from netra.labels import is_anaemic, label_frame, severity, who_cutoff


@pytest.mark.parametrize("age_m, sex, cut", [
    (30, None, 11.0), (8 * 12, None, 11.5), (13 * 12, "M", 12.0),
    (30 * 12, "F", 12.0), (30 * 12, "male", 13.0), (30 * 12, "Female", 12.0),
])
def test_cutoffs(age_m, sex, cut):
    assert who_cutoff(age_m, sex) == cut


def test_boundary_is_not_anaemic():
    assert is_anaemic(11.0, 30) == 0
    assert is_anaemic(10.99, 30) == 1
    assert is_anaemic(12.5, 30 * 12, "m") == 1
    assert is_anaemic(12.5, 30 * 12, "f") == 0


@pytest.mark.parametrize("hb, age_m, sex, sev", [
    (11.0, 30, None, "normal"), (10.0, 30, None, "mild"), (7.0, 30, None, "moderate"), (6.9, 30, None, "severe"),
    (12.0, 400, "m", "mild"), (10.9, 400, "f", "moderate"), (7.9, 400, "f", "severe"),
])
def test_severity(hb, age_m, sex, sev):
    assert severity(hb, age_m, sex) == sev


def test_label_frame_defaults_age_when_missing():
    hb = pd.Series([10.5, 11.2, 12.5])
    out = label_frame(hb, default_age_months=30)
    assert out["label"].tolist() == [1, 0, 0]
    age = pd.Series([None, 30, 30])
    sex = pd.Series(["m", "m", "m"])
    out = label_frame(pd.Series([12.5, 12.5, 12.5]), age, sex, age_in_months=False, default_age_months=30)
    assert out["label"].tolist() == [0, 1, 1]
