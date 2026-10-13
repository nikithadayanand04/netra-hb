import numpy as np
import pandas as pd
import pytest

import config
from netra.ghana import dihedral_hashes, group_and_clean, match_matrix, parse_name


@pytest.mark.parametrize("name, label, num, series, original", [
    ("Anemic-001.png", 1, 1, "main", True),
    ("Anemic-001 (2).png", 1, 1, "main", False),
    ("Anemic-001FV (3).png", 1, 1, "main", False),
    ("Anemic-200 - Copy.png", 1, 200, "main", False),
    ("Anemic-145png.png", 1, 145, "main", True),
    ("AnemicP271.png", 1, 271, "main", True),
    ("Non-Anrmic-FN-015.png", 0, 15, "main", True),
    ("Non-anemic-Pa-018.png", 0, 18, "small", True),
    ("Anemic-Conj-N-001R.png", 1, 1, "extra", False),
    ("Anmeic-fn-0001 1.png", 1, 1, "extra", False),
])
def test_parse_name(name, label, num, series, original):
    p = parse_name(name)
    assert (p["label"], p["num"], p["series"], p["original"]) == (label, num, series, original)


def _blob(seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    rgb = np.clip(rng.normal(150, 40, (60, 40, 3)), 0, 255).astype(np.uint8)
    tissue = np.zeros((60, 40), bool)
    tissue[5:55, 4:36] = True
    return rgb, tissue


def _row(rgb, tissue, file, label):
    return {"file": file, "label": label, "tissue_px": int(tissue.sum()),
            "hashes": dihedral_hashes(rgb, tissue), "median_rgb": np.median(rgb[tissue], axis=0)}


def test_rotated_and_mirrored_copies_match_but_other_images_do_not():
    rgb, t = _blob(0)
    other, t2 = _blob(1)
    df = pd.DataFrame([_row(rgb, t, "a.png", 1), _row(np.rot90(rgb), np.rot90(t), "b.png", 1),
                       _row(rgb[:, ::-1], t[:, ::-1], "c.png", 1), _row(other, t2, "d.png", 1)])
    m = match_matrix(df, df)
    assert m[0, 1] and m[0, 2] and not m[0, 3]


def test_duplicates_share_a_group_and_label_conflicts_are_dropped():
    rgb, t = _blob(0)
    other, t2 = _blob(1)
    df = pd.DataFrame([_row(rgb, t, "a.png", 1), _row(np.rot90(rgb, 2), np.rot90(t, 2), "b.png", 1),
                       _row(other, t2, "c.png", 1), _row(other[::-1], t2[::-1], "d.png", 0)])
    out = group_and_clean(df, "palm")
    assert out["cv_group"][0] == out["cv_group"][1] == "palm:a"
    assert list(out["drop_reason"]) == ["", "", "duplicate_conflicting_label", "duplicate_conflicting_label"]


def test_ghana_csvs_have_no_cp_images_and_unique_ids():
    if not all(s["csv"].exists() for s in config.GHANA_SITES.values()):
        pytest.skip("run scripts.extract_ghana first")
    eye = pd.read_csv(config.GHANA_SITES["eye_extra"]["csv"])
    cw = pd.read_csv(config.OUT_DIR / "ghana_cp_crosswalk.csv")
    assert not set(eye["file"]) & set(cw["ghana_file"])
    for s in config.GHANA_SITES.values():
        d = pd.read_csv(s["csv"])
        assert d["patient_id"].is_unique and (d["label_source"] == "folder").all()
        assert (d.groupby("cv_group")["label"].nunique() == 1).all()
