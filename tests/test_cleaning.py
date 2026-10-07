import pandas as pd

from netra.cleaning import add_flags


def _log(rows):
    cols = ["id", "hb", "label", "tissue_px", "glare_frac", "lap_var", "pixel_eq_frac", "dup_group", "dup_of"]
    return pd.DataFrame(rows, columns=cols)


def test_conflicting_duplicates_dropped_with_reason():
    log = add_flags(_log([
        ("a", 11.2, 0, 4000, 0.0, 10, 0.1, 0, ""),
        ("b", 6.3, 1, 4000, 0.0, 10, 0.1, 0, "a"),
        ("c", 12.0, 0, 4000, 0.0, 10, 0.1, 1, ""),
        ("d", 12.2, 0, 4000, 0.0, 10, 0.1, 1, "c"),
        ("e", 12.0, 0, 100, 0.0, 10, 0.1, -1, ""),
    ]))
    assert log["drop"].tolist() == [True, True, False, False, True]
    assert log["drop_reason"].tolist()[:2] == ["duplicate_conflicting_hb"] * 2
    assert log.loc[4, "drop_reason"] == "low_tissue"
    assert log.loc[3, "flag_duplicate"]


def test_quality_flags_exclude_from_primary_only():
    log = add_flags(_log([
        ("a", 12.0, 0, 4000, 0.20, 10, 0.1, -1, ""),
        ("b", 8.0, 1, 4000, 0.0, 1.0, 0.5, -1, ""),
        ("c", 12.0, 0, 4000, 0.0, 10, 0.1, -1, ""),
        ("d", 12.0, 0, 100, 0.0, 10, 0.1, -1, ""),
    ]))
    assert log["drop"].tolist() == [False, False, False, True]
    assert log["exclude"].tolist() == [True, True, False, True]
    assert log["exclude_reason"].tolist()[:3] == ["high_glare", "blur;upscaled", ""]
