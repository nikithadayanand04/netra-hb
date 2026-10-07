import numpy as np
from PIL import Image

import config
from netra.masks import glare_mask, load_image, make_mask, tissue_mask


def test_alpha_mask(tmp_path):
    arr = np.zeros((10, 10, 4), np.uint8)
    arr[2:8, 2:8] = (200, 100, 100, 255)
    p = tmp_path / "a.png"
    Image.fromarray(arr, "RGBA").save(p)
    rgb, alpha = load_image(p)
    assert alpha is not None
    m = make_mask(rgb, alpha)
    assert m.mask.sum() == 36 and m.glare_frac == 0


def test_black_fallback_without_alpha():
    rgb = np.zeros((4, 4, 3), np.uint8)
    rgb[:2] = (180, 90, 90)
    rgb[2, 0] = (config.BLACK_THRESH - 1,) * 3
    m = tissue_mask(rgb, None)
    assert m.sum() == 8


def test_opaque_alpha_uses_black_fallback():
    rgb = np.zeros((4, 4, 3), np.uint8)
    rgb[:2] = (180, 90, 90)
    assert tissue_mask(rgb, np.full((4, 4), 255, np.uint8)).sum() == 8


def test_glare_removed_and_fraction():
    rgb = np.full((10, 10, 3), (200, 100, 100), np.uint8)
    rgb[0, :5] = (250, 248, 245)
    assert glare_mask(rgb).sum() == 5
    m = make_mask(rgb, np.full((10, 10), 128, np.uint8))
    assert m.mask.sum() == 95
    assert np.isclose(m.glare_frac, 0.05)
