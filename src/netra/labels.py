import numpy as np
import pandas as pd

# (cut-off, mild lower bound, severe upper bound) in g/dL, WHO 2011
_BANDS = {
    "child_6_59m": (11.0, 10.0, 7.0),
    "child_5_11y": (11.5, 11.0, 8.0),
    "child_12_14y": (12.0, 11.0, 8.0),
    "woman": (12.0, 11.0, 8.0),
    "man": (13.0, 11.0, 8.0),
}
SEVERITIES = ("normal", "mild", "moderate", "severe")


def parse_sex(sex) -> str | None:
    if sex is None or (isinstance(sex, float) and np.isnan(sex)):
        return None
    s = str(sex).strip().lower()
    if s[:1] == "m":
        return "m"
    if s[:1] == "f" or s[:1] == "w":
        return "f"
    return None


def who_group(age_months: float, sex=None) -> str:
    if age_months < 60:
        return "child_6_59m"
    if age_months < 144:
        return "child_5_11y"
    if age_months < 180:
        return "child_12_14y"
    return "man" if parse_sex(sex) == "m" else "woman"


def who_cutoff(age_months: float, sex=None) -> float:
    return _BANDS[who_group(age_months, sex)][0]


def is_anaemic(hb: float, age_months: float, sex=None) -> int:
    return int(hb < who_cutoff(age_months, sex))


def severity(hb: float, age_months: float, sex=None) -> str:
    cut, mild_lo, severe_hi = _BANDS[who_group(age_months, sex)]
    if hb >= cut:
        return "normal"
    if hb >= mild_lo:
        return "mild"
    if hb >= severe_hi:
        return "moderate"
    return "severe"


def label_frame(
    hb: pd.Series,
    age: pd.Series | None = None,
    sex: pd.Series | None = None,
    age_in_months: bool = True,
    default_age_months: float = 30,
) -> pd.DataFrame:
    n = len(hb)
    if age is None:
        age_m = pd.Series(default_age_months, index=hb.index, dtype=float)
    else:
        age_m = pd.to_numeric(age, errors="coerce").astype(float) * (1 if age_in_months else 12)
        age_m = age_m.fillna(default_age_months)
    sex = sex if sex is not None else pd.Series([None] * n, index=hb.index)
    rows = [
        (is_anaemic(h, a, s), severity(h, a, s), who_cutoff(a, s))
        for h, a, s in zip(hb.astype(float), age_m, sex)
    ]
    return pd.DataFrame(rows, columns=["label", "severity", "hb_cutoff"], index=hb.index)
