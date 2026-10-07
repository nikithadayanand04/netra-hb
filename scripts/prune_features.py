import pandas as pd

import config
from netra.features import prune_redundant


def main() -> None:
    df = pd.read_csv(config.FEATURES_CSV)
    keep, dropped = prune_redundant(df[config.CANDIDATE_FEATURES], config.INTERPRETABILITY, config.REDUNDANCY_RHO)
    for loser, kept, r in dropped:
        print(f"drop {loser:22s} (|rho| = {r:.3f} with {kept})")
    keep = [f for f in keep if f not in config.COLLINEAR_DROP]
    print(f"drop {', '.join(config.COLLINEAR_DROP)} (config.COLLINEAR_DROP)")
    print(f"\n{len(config.CANDIDATE_FEATURES)} candidates -> {len(keep)} features:\n{keep}")
    if keep != config.MODEL_FEATURES:
        print("\nWARNING: config.MODEL_FEATURES is out of date; paste the list above into config.py")


if __name__ == "__main__":
    main()
