# three-way comparison for the final paper
# 1) keyword baseline (no profile)
# 2) exact-match profile scorer (no RapidFuzz)
# 3) fuzzy profile scorer (the one from checkpoint 1/2)

from __future__ import annotations

from sklearn.metrics import precision_recall_fscore_support

from skinsync.baseline import baseline_score
from skinsync.catalog import ALL_PRODUCTS, COMPATIBILITY_LABELS, HOLDOUT_LABELS, PROFILES
from skinsync.scoring import SkinProfile, profile_blind_score, score_product


def _profile(pid: str) -> SkinProfile:
    row = next(p for p in PROFILES if p["id"] == pid)
    return SkinProfile(
        id=row["id"],
        name=row["name"],
        skin_type=row["skin_type"],
        concerns=row["concerns"],
        sensitivities=row["sensitivities"],
        notes=row["notes"],
    )


def _pmap():
    return {p["id"]: p for p in ALL_PRODUCTS}


def pack(y_true, y_pred, method):
    y_unsafe = [1 - y for y in y_true]
    p_unsafe = [1 - y for y in y_pred]
    p, r, f1, _ = precision_recall_fscore_support(
        y_unsafe, p_unsafe, average="binary", zero_division=0
    )
    acc = sum(int(a == b) for a, b in zip(y_true, y_pred)) / max(len(y_true), 1)
    return {
        "method": method,
        "accuracy": round(float(acc), 3),
        "n_correct": int(sum(int(a == b) for a, b in zip(y_true, y_pred))),
        "unsafe_precision": round(float(p), 3),
        "unsafe_recall": round(float(r), 3),
        "unsafe_f1": round(float(f1), 3),
        "n": len(y_true),
    }


def evaluate_labels(labels, name):
    pmap = _pmap()
    y_true = []
    y_base = []
    y_blind = []
    y_fuzzy = []
    rows = []
    for profile_id, product_id, gold, why in labels:
        product = pmap[product_id]
        profile = _profile(profile_id)
        raw = product["ingredients_raw"]
        base = baseline_score(raw)
        blind = profile_blind_score(raw)
        fuzzy = score_product(raw, profile, allow_fuzzy=True)
        y_true.append(int(gold))
        y_base.append(int(base["compatible"]))
        y_blind.append(int(blind["compatible"]))
        y_fuzzy.append(int(fuzzy["compatible"]))
        rows.append(
            {
                "split": name,
                "profile": profile.name,
                "product": product["name"],
                "gold": gold,
                "baseline": int(base["compatible"]),
                "blind": int(blind["compatible"]),
                "fuzzy": int(fuzzy["compatible"]),
                "fuzzy_score": fuzzy["score"],
                "fuzzy_verdict": fuzzy["verdict"],
                "fuzzy_flags": [f["matched"] for f in fuzzy["flags"][:4]],
                "blind_hits": blind["hits"][:4],
                "why": why,
            }
        )
    return {
        "split": name,
        "baseline": pack(y_true, y_base, "keyword_baseline"),
        "blind": pack(y_true, y_blind, "profile_blind_lexicon"),
        "fuzzy": pack(y_true, y_fuzzy, "fuzzy_profile"),
        "rows": rows,
    }


def disagreements(rows):
    out = []
    for r in rows:
        if r["gold"] != r["fuzzy"] or r["blind"] != r["fuzzy"] or r["baseline"] != r["fuzzy"]:
            out.append(r)
    return out


def run_final():
    dev = evaluate_labels(COMPATIBILITY_LABELS, "dev")
    hold = evaluate_labels(HOLDOUT_LABELS, "holdout")
    both = evaluate_labels(COMPATIBILITY_LABELS + HOLDOUT_LABELS, "all")
    return {
        "dev": dev,
        "holdout": hold,
        "all": both,
        "n_dev": len(COMPATIBILITY_LABELS),
        "n_holdout": len(HOLDOUT_LABELS),
        "n_all": len(COMPATIBILITY_LABELS) + len(HOLDOUT_LABELS),
        "holdout_errors": [
            r for r in hold["rows"] if r["gold"] != r["fuzzy"]
        ],
        "high_score_unsafe": [
            r
            for r in both["rows"]
            if r["gold"] == 0 and r["fuzzy_score"] >= 70
        ],
    }


if __name__ == "__main__":
    import json
    from skinsync.paths import RESULTS_DIR

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = run_final()
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
    out = RESULTS_DIR / "final_results.json"
    out.write_text(json.dumps(slim, indent=2))
    print("Table I  accuracy / unsafe F1")
    for split in ("dev", "holdout", "all"):
        print(split, {k: slim[split][k] for k in ("baseline", "blind", "fuzzy")})
    print()
    print("Table II  holdout unsafe precision / recall / F1  (n=19, 3 unsafe)")
    h = slim["holdout"]
    for key, name in (
        ("baseline", "M1 Keyword"),
        ("blind", "M2 Blind lexicon"),
        ("fuzzy", "M3 Profile-aware"),
    ):
        row = h[key]
        print(
            f"{name:22} P={row['unsafe_precision']:.3f}  "
            f"R={row['unsafe_recall']:.3f}  F1={row['unsafe_f1']:.3f}  "
            f"acc={row['accuracy']:.3f}  correct={row['n_correct']}/{row['n']}"
        )
