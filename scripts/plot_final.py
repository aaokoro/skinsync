import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from skinsync.evaluate_final import run_final
from skinsync.paths import FIGURES_DIR, RESULTS_DIR


def main():
    payload = run_final()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    slim = {
        "n_dev": payload["n_dev"],
        "n_holdout": payload["n_holdout"],
        "n_all": payload["n_all"],
        "dev": {k: payload["dev"][k] for k in ("baseline", "blind", "fuzzy")},
        "holdout": {k: payload["holdout"][k] for k in ("baseline", "blind", "fuzzy")},
        "all": {k: payload["all"][k] for k in ("baseline", "blind", "fuzzy")},
        "holdout_errors": payload["holdout_errors"],
        "high_score_unsafe": payload["high_score_unsafe"],
    }
    (RESULTS_DIR / "final_results.json").write_text(json.dumps(slim, indent=2))

    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.85), dpi=170)
    fig.patch.set_facecolor("white")
    labels = ["Dev (n=35)", "Holdout (n=19)", "All (n=54)"]
    methods = [
        ("baseline", "M1 keyword baseline", "#8aa4b8"),
        ("blind", "M2 profile-blind lexicon", "#c47b4a"),
        ("fuzzy", "M3 profile-aware scorer", "#2f6f4e"),
    ]
    splits = ["dev", "holdout", "all"]
    x = range(len(labels))
    w = 0.25
    handles = []

    for ax, metric, title, ylab in (
        (axes[0], "accuracy", "Label Accuracy", "Accuracy"),
        (axes[1], "unsafe_f1", "Unsafe Class F1", "F1"),
    ):
        for i, (key, name, color) in enumerate(methods):
            vals = [slim[s][key][metric] for s in splits]
            bars = ax.bar([j + (i - 1) * w for j in x], vals, w, color=color, label=name)
            if ax is axes[0]:
                handles.append(bars)
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_xlabel("Evaluation set", fontsize=8)
        ax.set_ylim(0, 1.15)
        ax.set_ylabel(ylab, fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.legend(
        handles,
        [m[1] for m in methods],
        loc="lower center",
        ncol=3,
        frameon=False,
        fontsize=7,
        bbox_to_anchor=(0.5, -0.02),
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    out = FIGURES_DIR / "final_three_models.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
