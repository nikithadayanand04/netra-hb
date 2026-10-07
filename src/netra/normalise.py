import numpy as np


def _apply_gains(rgb: np.ndarray, gains: np.ndarray) -> np.ndarray:
    return np.clip(rgb.astype(float) * gains, 0, 255)


def grey_world(rgb: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    px = rgb[mask] if mask is not None else rgb.reshape(-1, 3)
    means = px.astype(float).mean(axis=0)
    gains = means.mean() / np.maximum(means, 1e-6)
    return _apply_gains(rgb, gains)


def sclera_normalise(rgb: np.ndarray, sclera_patch: np.ndarray, target: float | np.ndarray | None = None) -> np.ndarray:
    ref = np.median(np.asarray(sclera_patch, dtype=float).reshape(-1, 3), axis=0)
    tgt = ref.mean() if target is None else np.asarray(target, dtype=float)
    gains = tgt / np.maximum(ref, 1e-6)
    return _apply_gains(rgb, gains)
