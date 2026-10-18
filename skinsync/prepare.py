"""Build the local catalog, run checkpoint evaluation, and write figures."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from skinsync.db import fetch_products, rebuild
from skinsync.evaluate import run_evaluation
from skinsync.paths import (
    DB_PATH,
    FIGURES_DIR,
    PROCESSED_DIR,
    RAW_PRODUCTS,
    RESULTS_DIR,
    RESULTS_JSON,
)


def copy_raw_if_needed(source: Path | None = None) -> None:
    RAW_PRODUCTS.parent.mkdir(parents=True, exist_ok=True)
    if source and source.exists() and source.resolve() != RAW_PRODUCTS.resolve():
        shutil.copy(source, RAW_PRODUCTS)
    if not RAW_PRODUCTS.exists():
        raise FileNotFoundError(f"Missing raw catalog at {RAW_PRODUCTS}")


def plot_metrics(results: dict) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    irr = results["irritant_detection"]
    match = results["user_matching"]

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 2.15), dpi=170)
    fig.patch.set_facecolor("white")

    def grouped(ax, methods, labels, title, ylabel):
        x = range(len(labels))
        width = 0.35
        b = [methods[0][k] for k in labels]
        m = [methods[1][k] for k in labels]
        ax.bar([i - width / 2 for i in x], b, width, color="#8aa4b8", label="Keyword baseline")
        ax.bar([i + width / 2 for i in x], m, width, color="#2f6f4e", label="Multi-criteria / fuzzy")
        ax.set_xticks(list(x))
        ax.set_xticklabels([k.replace("_", "\n") for k in labels], fontsize=8)
        ax.set_ylim(0, 1.05)
        ax.set_title(title, fontsize=10, pad=8)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(fontsize=7, frameon=False)

    grouped(
        axes[0],
        [irr["baseline"], irr["multi_criteria_matcher"]],
        ["precision", "recall", "f1"],
        "Known-risk ingredient detection",
        "Score",
    )
    grouped(
        axes[1],
        [match["baseline"], match["multi_criteria"]],
        ["unsafe_precision", "unsafe_recall", "unsafe_f1", "label_accuracy"],
        "Personalized compatible / unsafe labels",
        "Score",
    )
    fig.tight_layout()
    out = FIGURES_DIR / "checkpoint1_metrics.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_ranking(results: dict) -> Path:
    ranking = results["user_matching"]["ranking"]
    fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=160)
    fig.patch.set_facecolor("white")
    names = [r["profile"] for r in ranking]
    x = range(len(names))
    width = 0.35
    ax.bar(
        [i - width / 2 for i in x],
        [r["baseline_top5_safe_rate"] for r in ranking],
        width,
        color="#8aa4b8",
        label="Baseline top-5 safe rate",
    )
    ax.bar(
        [i + width / 2 for i in x],
        [r["multi_top5_safe_rate"] for r in ranking],
        width,
        color="#2f6f4e",
        label="Multi-criteria top-5 safe rate",
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(names, fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Share of labeled-safe products in top 5")
    ax.set_title("User-matching satisfaction (ranking)", fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    out = FIGURES_DIR / "checkpoint1_ranking.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def main(raw_source: str | None = None) -> dict:
    copy_raw_if_needed(Path(raw_source) if raw_source else None)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stats = rebuild(DB_PATH, RAW_PRODUCTS)
    from skinsync.db import connect

    conn = connect(DB_PATH)
    products = fetch_products(conn)
    conn.close()
    evaluation = run_evaluation(products)
    payload = {"catalog": stats, "evaluation": evaluation}
    RESULTS_JSON.write_text(json.dumps(payload, indent=2))
    plot_metrics(evaluation)
    plot_ranking(evaluation)
    print(json.dumps({"catalog": stats, "irritant": evaluation["irritant_detection"]["baseline"] | {"vs": evaluation["irritant_detection"]["multi_criteria_matcher"]}, "matching": {"baseline": evaluation["user_matching"]["baseline"], "multi": evaluation["user_matching"]["multi_criteria"]}}, indent=2))
    return payload


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/obf/raw_products.json")
