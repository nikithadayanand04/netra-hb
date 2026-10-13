import sys
from pathlib import Path

import numpy as np
import pytest

import config
from netra import screening
from netra.cleaning import photo_checks

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))


def _knots():
    return np.linspace(0.05, 0.95, 10), np.linspace(13.5, 8.5, 10) - 1e-3 * np.arange(10)


def test_strip_position_puts_threshold_on_training_cutoff() -> None:
    k = _knots()
    assert screening.strip_position(0.4, 0.4, k) == pytest.approx(11.0)
    assert screening.strip_position(0.6, 0.4, k) < 11.0 < screening.strip_position(0.2, 0.4, k)


def test_severity_bands() -> None:
    assert screening.severity(11.5, 11.0) == "none"
    assert screening.severity(10.4, 11.0) == "mild"
    assert screening.severity(8.0, 11.0) == "moderate"
    assert screening.severity(6.5, 11.0) == "severe"


def test_uncertainty_band_is_a_proportion_interval() -> None:
    rng = np.random.default_rng(0)
    p = rng.uniform(size=400)
    b = {"oof_p": p, "oof_y": (rng.uniform(size=400) < p).astype(int)}
    lo, hi = screening.uncertainty_band(b, 0.8)
    assert 0 <= lo < hi <= 1 and lo < 0.8 < hi + 0.1


def test_auto_tissue_from_alpha_and_black_background() -> None:
    rgb = np.full((40, 40, 3), 180, np.uint8)
    alpha = np.zeros((40, 40), np.uint8)
    alpha[10:30, 10:30] = 255
    assert screening.auto_tissue(rgb, alpha).sum() == 400
    black = rgb.copy()
    black[:, :20] = 0
    assert screening.auto_tissue(black, None).sum() == 800
    assert screening.auto_tissue(rgb, None) is None   # no background: the user clicks the tissue


def test_grow_region_stays_on_the_clicked_colour() -> None:
    rgb = np.zeros((100, 100, 3), np.uint8)
    rgb[:] = (120, 90, 70)
    rgb[30:70, 30:70] = (210, 110, 110)
    region = screening.grow_region(rgb, 50, 50)
    assert region[50, 50] and not region[5, 5] and region.sum() <= 40 * 40


def test_photo_checks_flag_dark_and_blurred_photos() -> None:
    rng = np.random.default_rng(0)
    sharp = rng.integers(120, 230, (80, 80, 3)).astype(np.uint8)
    tissue = np.ones((80, 80), bool)
    assert all(c["ok"] for c in photo_checks(sharp, tissue, 0.0).values())
    dark = (sharp * 0.2).astype(np.uint8)
    assert not photo_checks(dark, tissue, 0.0)["light"]["ok"]
    flat = np.full((80, 80, 3), 170, np.uint8)
    assert not photo_checks(flat, tissue, 0.0)["sharp"]["ok"]
    assert not photo_checks(sharp, tissue, config.GLARE_MAX_FRAC + 0.01)["glare"]["ok"]


def test_samples_cover_every_site_with_both_results() -> None:
    import json
    s = json.loads((config.ROOT / "app" / "samples" / "samples.json").read_text())["samples"]
    assert sorted((x["site"], x["label"]) for x in s) == sorted((site, y) for site in ("eye", "palm", "nail")
                                                               for y in (0, 1))
    assert all((config.ROOT / "app" / "samples" / x["file"]).exists() for x in s)


def test_makeup_filter_removes_kajal_and_flags_the_eye_photo() -> None:
    rng = np.random.default_rng(0)
    rgb = np.stack([rng.integers(170, 230, (60, 60)), rng.integers(80, 120, (60, 60)),
                    rng.integers(90, 130, (60, 60))], axis=2).astype(np.uint8)       # pink, textured
    rgb[45:, :] = (25, 22, 24)                                                       # kajal band: 25% of rows
    tissue = np.ones((60, 60), bool)
    photo = screening.analyse_photo(rgb, tissue, "eye")
    assert photo.makeup_frac == pytest.approx(0.25, abs=0.02)
    assert not photo.mask[50, 10] and photo.mask[10, 10]          # kajal is not measured, pink is
    assert not photo.checks["makeup"]["ok"]
    assert "makeup" not in screening.analyse_photo(rgb, tissue, "nail").checks   # warning is eye-only


def test_makeup_filter_keeps_pink_conjunctiva() -> None:
    pink = np.full((20, 20, 3), (200, 110, 120), np.uint8)
    dark_red = np.full((20, 20, 3), (90, 30, 40), np.uint8)       # dark but saturated: still tissue
    assert not screening.makeup_mask(pink).any() and not screening.makeup_mask(dark_red).any()


def test_box_region_is_order_free_and_clipped() -> None:
    r = screening.box_region((50, 80, 3), 70, 40, 10, 5)
    assert r.sum() == 61 * 36 and r[5, 10] and r[40, 70]
    assert screening.box_region((50, 80, 3), -5, -5, 200, 200).all()


def _nn_bundle(X: np.ndarray) -> dict:
    from sklearn.neighbors import NearestNeighbors
    mean, scale = X.mean(0), X.std(0)
    Z = (X - mean) / scale
    d, _ = NearestNeighbors(n_neighbors=config.NN_K + 1).fit(Z).kneighbors(Z)
    cols = [f"f{i}" for i in range(X.shape[1])]
    return {"input_columns": cols, "nn": {"mean": mean, "scale": scale, "X": Z,
                                          "threshold": float(np.percentile(d[:, 1:].mean(1), config.NN_PCT))}}


def test_familiarity_flags_far_photos_only() -> None:
    X = np.random.default_rng(0).normal(size=(300, 4))
    b = _nn_bundle(X)
    near = screening.familiarity(b, {c: 0.1 for c in b["input_columns"]})
    far = screening.familiarity(b, {c: 6.0 for c in b["input_columns"]})
    assert not near["unfamiliar"] and far["unfamiliar"] and far["distance"] > far["threshold"] > near["distance"]


def test_saved_eye_bundle_flags_a_cool_webcam_tint() -> None:
    """Measured behaviour (not a promise): a strong blue webcam cast is flagged, the sample itself is not.
    Warm indoor light, washed-out photos and palm or nail photos offered as an eye are NOT flagged."""
    import joblib
    from netra.masks import load_image
    path = config.OUT_DIR / "models" / "screen_eye.joblib"
    if not path.exists():
        pytest.skip("run python -m scripts.build_screen_models")
    eye = joblib.load(path)
    rgb, alpha = load_image(config.ROOT / "app" / "samples" / "eye_refer.png")
    own = screening.analyse_photo(rgb, alpha > 0, "eye")
    cool = np.clip(rgb.astype(float) * [0.8, 1.0, 1.25], 0, 255).astype(np.uint8)
    tinted = screening.analyse_photo(cool, alpha > 0, "eye")
    assert not screening.familiarity(eye, screening.features(own))["unfamiliar"]
    assert screening.familiarity(eye, screening.features(tinted))["unfamiliar"]
