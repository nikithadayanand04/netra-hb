"""Measures the Screen-page safeguards on the training data -> outputs/results/safeguards.json.

1. Makeup/lash filter: share of real CP-AnemiC conjunctiva pixels it wrongly removes, and the share of images over
   the warning line. Also the best rejected skin-tone rule (Lab a* < 15) for comparison.
2. KNN unfamiliar-photo check: per-site thresholds, and the distance for simple variations of the eye refer sample
   (colour casts, washed out, half skin) and for palm / nail samples offered as an eye."""
import json

import joblib
import numpy as np
import pandas as pd
from skimage.color import rgb2lab

import config
from netra import screening
from netra.masks import load_image, make_mask

SAMPLES = config.ROOT / "app" / "samples"


def makeup_check() -> dict:
    df = pd.read_csv(config.FEATURES_CSV)
    removed = total = skin = 0
    per_image = []
    for pid in df.patient_id:
        rgb, alpha = load_image(config.DATA_DIR / f"{pid}.png")
        mask = make_mask(rgb, alpha).mask
        m = screening.makeup_mask(rgb) & mask
        removed, total = removed + int(m.sum()), total + int(mask.sum())
        per_image.append(m.sum() / max(mask.sum(), 1))
        skin += int((rgb2lab(rgb[mask][None] / 255.0)[0][:, 1] < 15).sum())
    return {"images": len(df), "pixels_wrongly_removed": removed / total, "max_per_image": float(max(per_image)),
            "images_over_warning": int(sum(f > config.MAKEUP_WARN_FRAC for f in per_image)),
            "rule": f"V < {config.MAKEUP_V_MAX} and S < {config.MAKEUP_S_MAX}; warning above {config.MAKEUP_WARN_FRAC:.0%}",
            "rejected_skin_rule_lab_a_lt_15_wrongly_removed": skin / total}


def familiarity_check() -> dict:
    b = {s: joblib.load(config.OUT_DIR / "models" / f"screen_{s}.joblib") for s in ("eye", "palm", "nail")}
    out = {"thresholds": {s: v["nn"]["threshold"] for s, v in b.items()}, "k": config.NN_K, "percentile": config.NN_PCT,
           "eye_variations": {}}
    rgb, alpha = load_image(SAMPLES / "eye_refer.png")
    t, x = alpha > 0, rgb.astype(float)
    skin = np.where((np.indices(t.shape)[0] % 2 == 0)[..., None], x, np.array([176.0, 124, 100]))
    variants = {"original": x, "cool webcam cast (R x0.8, B x1.25)": x * [0.8, 1.0, 1.25],
                "warm indoor light (R x1.1, B x0.6)": x * [1.1, 0.95, 0.6], "washed out": x * 0.5 + 100,
                "box half skin": skin}
    for name, img in variants.items():
        photo = screening.analyse_photo(np.clip(img, 0, 255).astype(np.uint8), t, "eye")
        out["eye_variations"][name] = screening.familiarity(b["eye"], screening.features(photo))
    for f in ("palm_refer", "palm_normal", "nail_refer", "nail_normal"):
        rgb, alpha = load_image(SAMPLES / f"{f}.png")
        tissue = screening.auto_tissue(rgb, alpha)
        photo = screening.analyse_photo(rgb, np.ones(rgb.shape[:2], bool) if tissue is None else tissue, "eye")
        out["eye_variations"][f"{f} sample offered as an eye"] = screening.familiarity(b["eye"], screening.features(photo))
    return out


def main() -> None:
    res = {"meta": __doc__, "makeup": makeup_check(), "unfamiliar": familiarity_check()}
    (config.OUT_DIR / "results" / "safeguards.json").write_text(json.dumps(res, indent=2))
    m = res["makeup"]
    print(f"makeup filter: {m['pixels_wrongly_removed']:.2%} of CP pixels removed (max {m['max_per_image']:.1%}), "
          f"{m['images_over_warning']} images over the warning; skin rule would remove "
          f"{m['rejected_skin_rule_lab_a_lt_15_wrongly_removed']:.1%}")
    for k, v in res["unfamiliar"]["eye_variations"].items():
        print(f"  {k:<40} distance {v['distance']:.2f}  unfamiliar={v['unfamiliar']}")


if __name__ == "__main__":
    main()
