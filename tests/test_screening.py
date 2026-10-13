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


def test_referral_slip_is_a_pdf() -> None:
    from datetime import datetime
    import slip
    r = {"site": "eye", "p": 0.7, "refer": True, "position": 9.5, "swatch": (200, 120, 120)}
    pdf = slip.referral_slip({"name": "", "age_key": "age_6_59m", "cutoff": 11.0, "refer": True,
                              "time": datetime(2026, 1, 1), "results": [r], "combined": None})
    assert pdf[:4] == b"%PDF" and len(pdf) > 5000


def test_samples_cover_every_site_with_both_results() -> None:
    import json
    s = json.loads((config.ROOT / "app" / "samples" / "samples.json").read_text())["samples"]
    assert sorted((x["site"], x["label"]) for x in s) == sorted((site, y) for site in ("eye", "palm", "nail")
                                                               for y in (0, 1))
    assert all((config.ROOT / "app" / "samples" / x["file"]).exists() for x in s)
