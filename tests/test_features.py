import numpy as np
from skimage.color import rgb2lab

import pandas as pd

from netra.features import feature_names, image_features, prune_redundant
from netra.normalise import grey_world, sclera_normalise


def uniform(colour, n=20):
    rgb = np.zeros((n, n, 3), np.uint8)
    rgb[:] = colour
    return rgb, np.ones((n, n), bool)


def test_uniform_colour_values():
    rgb, mask = uniform((200, 100, 50))
    f = image_features(rgb, mask, 0.0)
    assert set(feature_names()) <= set(f)
    assert (f["R_med"], f["G_med"], f["B_med"]) == (200, 100, 50)
    assert np.isclose(f["chrom_r_med"], 200 / 350, atol=1e-5)
    assert np.isclose(f["chrom_r_med"] + f["chrom_g_med"] + f["chrom_b_med"], 1, atol=1e-5)
    lab = rgb2lab(np.array([[[200, 100, 50]]]) / 255)[0, 0]
    assert np.allclose([f["lab_L_med"], f["lab_a_med"], f["lab_b_med"]], lab)
    assert np.isclose(f["a_over_L_med"], lab[1] / lab[0])
    assert np.isclose(f["hsv_h_med"], 20.0)
    assert np.isclose(f["hsv_s_med"], 0.75) and np.isclose(f["hsv_v_med"], 200 / 255)
    assert np.isclose(f["erythema_index_med"], np.log10(201 / 101))
    assert f["lab_a_p10"] == f["lab_a_p90"] == f["lab_a_med"]
    assert f["tissue_px"] == 400


def test_mask_excludes_pixels_and_hue_wraps():
    rgb, mask = uniform((200, 100, 120))
    rgb[0] = (0, 255, 0)
    mask[0] = False
    f = image_features(rgb, mask, 0.1)
    assert f["G_med"] == 100 and f["glare_frac"] == 0.1
    assert -20 < f["hsv_h_med"] < 0  # magenta-red hue sits just below 0, not near 360


def test_empty_mask_gives_nan():
    rgb, mask = uniform((200, 100, 50))
    f = image_features(rgb, np.zeros_like(mask), 0.0)
    assert np.isnan(f["R_med"]) and f["tissue_px"] == 0


def test_pallor_ordering():
    red = image_features(*uniform((180, 60, 70)), 0.0)
    pale = image_features(*uniform((210, 160, 160)), 0.0)
    for k in ("lab_a_med", "a_over_L_med", "erythema_index_med", "chrom_r_med", "hsv_s_med"):
        assert red[k] > pale[k], k


def test_grey_world_balances_channels():
    rgb, mask = uniform((200, 100, 50))
    rgb[:10] = (100, 50, 25)
    out = grey_world(rgb, mask)
    means = out[mask].mean(axis=0)
    assert np.allclose(means, means.mean(), rtol=1e-6)


def test_sclera_normalise_neutralises_reference():
    rgb, _ = uniform((180, 120, 90))
    sclera = np.array([[220, 200, 180]] * 5)
    out = sclera_normalise(rgb, sclera)
    ref = sclera_normalise(sclera[None].astype(np.uint8), sclera)[0]
    assert np.allclose(ref, ref.mean())
    assert np.allclose(out[0, 0], np.array([180, 120, 90]) * 200 / np.array([220, 200, 180]))


def test_model_features_match_extracted_and_exclude_confounders():
    import config
    assert set(config.MODEL_FEATURES) <= set(config.CANDIDATE_FEATURES) <= set(feature_names())
    assert "hsv_v_med" not in config.CANDIDATE_FEATURES
    assert len(config.MODEL_FEATURES) <= 15
    assert not set(config.MODEL_FEATURES) & {"glare_frac", "tissue_px", "rg_ratio_med"}
    assert not any(f.startswith(("gw_", "flag_")) for f in config.MODEL_FEATURES)


def test_prune_redundant_keeps_preferred_and_ignores_labels():
    rng = np.random.default_rng(0)
    x = rng.normal(size=200)
    X = pd.DataFrame({"hsv_s_med": x, "lab_a_med": 2 * x + 1, "lab_b_med": rng.normal(size=200)})
    keep, dropped = prune_redundant(X, ["lab_a", "lab_b", "hsv_s"], 0.95)
    assert keep == ["lab_a_med", "lab_b_med"]
    assert dropped[0][:2] == ("hsv_s_med", "lab_a_med")


def test_model_features_reproduce_pruning():
    import config
    df = pd.read_csv(config.FEATURES_CSV) if config.FEATURES_CSV.exists() else None
    if df is None:
        return
    keep, _ = prune_redundant(df[config.CANDIDATE_FEATURES], config.INTERPRETABILITY, config.REDUNDANCY_RHO)
    assert keep == config.MODEL_FEATURES
