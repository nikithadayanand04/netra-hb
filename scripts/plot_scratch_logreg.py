import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression as SkLogisticRegression
from sklearn.preprocessing import StandardScaler

import config
from netra.scratch import LogisticRegression

OUT = config.OUT_DIR / "figures" / "scratch_logreg_loss.png"
SURFACE, INK, INK_2, GRID, SERIES = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"


def sklearn_loss(X: np.ndarray, y: np.ndarray, C: float) -> float:
    ref = SkLogisticRegression(C=C, tol=1e-12, max_iter=10000).fit(X, y)
    p = ref.predict_proba(X)[:, 1]
    w = ref.coef_[0]
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)) + w @ w / (2 * C * len(X)))


def main() -> None:
    df = pd.read_csv(config.FEATURES_CSV)
    X = StandardScaler().fit_transform(df[config.MODEL_FEATURES])
    y = df["label"].to_numpy()
    model = LogisticRegression(C=1.0).fit(X, y)
    model.summary(config.MODEL_FEATURES)
    ref = sklearn_loss(X, y, model.C)
    print(f"sklearn optimum loss = {ref:.6f}  scratch final = {model.loss_history_[-1]:.6f}")

    loss = np.array(model.loss_history_)
    it = np.arange(1, len(loss) + 1)
    plt.rcParams.update({"font.size": 10, "text.color": INK, "axes.labelcolor": INK_2,
                         "xtick.color": INK_2, "ytick.color": INK_2})
    fig, ax = plt.subplots(figsize=(7, 4), dpi=200, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.plot(it, loss, color=SERIES, lw=2, solid_capstyle="round")
    ax.axhline(ref, color=INK_2, lw=1, ls=(0, (4, 3)))
    ax.annotate("sklearn optimum", (it[-1], ref), xytext=(0, 6), textcoords="offset points",
                ha="right", va="bottom", color=INK_2)
    ax.annotate(f"converged at iter {model.n_iter_}\nloss {loss[-1]:.4f}", (it[-1], loss[-1]),
                xytext=(-8, 24), textcoords="offset points", ha="right", va="bottom", color=INK)
    ax.set_xscale("log")
    ax.set_xlabel("Gradient-descent iteration (log scale)")
    ax.set_ylabel("Training loss (log-loss + L2)")
    ax.set_title(f"From-scratch logistic regression, full-batch GD (lr = 1/L = {model.lr_:.3f}, C = {model.C})",
                 loc="left", fontsize=11, color=INK)
    ax.grid(axis="y", color=GRID, lw=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=SURFACE)
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
