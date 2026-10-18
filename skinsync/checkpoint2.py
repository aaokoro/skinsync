# checkpoint 2 tests
# I kept the same scorer from checkpoint 1 and tried it on new products
# also looked at where the score and the yes/no flag don't agree

from __future__ import annotations

import json
from collections import defaultdict

from sklearn.metrics import precision_recall_fscore_support

from skinsync.baseline import baseline_score
from skinsync.catalog import (
    ALL_PRODUCTS,
    CANONICAL_PRODUCTS,
    COMPATIBILITY_LABELS,
    HOLDOUT_LABELS,
    HOLDOUT_PRODUCTS,
    PROFILES,
)
from skinsync.db import load_open_beauty_facts
from skinsync.evaluate import evaluate_irritant_detection, evaluate_user_matching, sample_prediction
from skinsync.parse import parse_ingredients
from skinsync.paths import RAW_PRODUCTS
from skinsync.scoring import SkinProfile, match_parsed, score_product


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


def _pmap(products):
    return {p["id"]: p for p in products}


def score_vs_gold_rows(products, labels):
    # if I just used the 0-100 score (recommend if score >= 70) vs my labels
    # this is where Maya + retinol falls apart
    pmap = _pmap(products)
    rows = []
    for profile_id, product_id, gold, why in labels:
        product = pmap[product_id]
        profile = _profile(profile_id)
        multi = score_product(product["ingredients_raw"], profile)
        base = baseline_score(product["ingredients_raw"])
        rows.append(
            {
                "profile": profile.name,
                "profile_id": profile_id,
                "product": product["name"],
                "product_id": product_id,
                "gold": gold,
                "baseline_ok": int(base["compatible"]),
                "multi_ok": int(multi["compatible"]),
                "score": multi["score"],
                "verdict": multi["verdict"],
                "avoid": sum(1 for f in multi["flags"] if f["severity"] == "avoid"),
                "caution": sum(1 for f in multi["flags"] if f["severity"] == "caution"),
                "flags": [f["matched"] for f in multi["flags"][:5]],
                "why": why,
            }
        )
    return rows


def pack_binary(y_true, y_pred, method):
    y_unsafe = [1 - y for y in y_true]
    p_unsafe = [1 - y for y in y_pred]
    p, r, f1, _ = precision_recall_fscore_support(
        y_unsafe, p_unsafe, average="binary", zero_division=0
    )
    acc = sum(int(a == b) for a, b in zip(y_true, y_pred)) / max(len(y_true), 1)
    return {
        "method": method,
        "unsafe_precision": round(float(p), 3),
        "unsafe_recall": round(float(r), 3),
        "unsafe_f1": round(float(f1), 3),
        "label_accuracy": round(float(acc), 3),
        "n": len(y_true),
        "n_correct": int(sum(int(a == b) for a, b in zip(y_true, y_pred))),
    }


def metrics_from_rows(rows, pred_key, method):
    y_true = [r["gold"] for r in rows]
    y_pred = [r[pred_key] for r in rows]
    return pack_binary(y_true, y_pred, method)


def threshold_sweep(rows):
    # recommend if score >= T, ignore the avoid flag
    out = []
    y_true = [r["gold"] for r in rows]
    for t in (40, 50, 55, 60, 70, 80, 90):
        y_pred = [int(r["score"] >= t) for r in rows]
        pack = pack_binary(y_true, y_pred, f"score>={t}")
        pack["threshold"] = t
        out.append(pack)
    return out


def weak_cases(rows):
    # gold says no, but score still looks friendly
    bad = []
    for r in rows:
        if r["gold"] == 0 and r["score"] >= 70:
            bad.append(r)
        elif r["gold"] == 1 and r["multi_ok"] == 0:
            bad.append(r)
    return bad


def leave_one_product_out(products, labels):
    # not a trained model, just "if I hide one product, do the rest still look ok"
    by_product = defaultdict(list)
    for i, row in enumerate(labels):
        by_product[row[1]].append(i)
    rows = score_vs_gold_rows(products, labels)
    accs = []
    for pid, idxs in sorted(by_product.items()):
        keep = [r for i, r in enumerate(rows) if i not in idxs]
        if not keep:
            continue
        y_true = [r["gold"] for r in keep]
        y_pred = [r["multi_ok"] for r in keep]
        acc = sum(int(a == b) for a, b in zip(y_true, y_pred)) / len(keep)
        accs.append(
            {
                "left_out": pid,
                "n_remaining": len(keep),
                "accuracy": round(acc, 3),
            }
        )
    mean = round(sum(a["accuracy"] for a in accs) / max(len(accs), 1), 3)
    return {"mean_accuracy": mean, "folds": accs}


def obf_parse_stats():
    if not RAW_PRODUCTS.exists():
        return {"ok": False, "reason": "no OBF file in this zip"}
    products = load_open_beauty_facts(RAW_PRODUCTS)
    n_tok = []
    n_match = []
    for p in products:
        tokens = parse_ingredients(p["ingredients_raw"])
        n_tok.append(len(tokens))
        hits = 0
        for t in tokens:
            rec, score = match_parsed(t)
            if rec and score >= 90:
                hits += 1
        n_match.append(hits)
    return {
        "ok": True,
        "products": len(products),
        "mean_parsed": round(sum(n_tok) / max(len(n_tok), 1), 1),
        "mean_lexicon_hits": round(sum(n_match) / max(len(n_match), 1), 1),
        "pct_with_5plus_tokens": round(
            sum(1 for n in n_tok if n >= 5) / max(len(n_tok), 1), 3
        ),
    }


def example_obf_scores(n=4):
    if not RAW_PRODUCTS.exists():
        return []
    products = load_open_beauty_facts(RAW_PRODUCTS)[:n]
    maya = _profile("maya")
    out = []
    for p in products:
        multi = score_product(p["ingredients_raw"], maya)
        base = baseline_score(p["ingredients_raw"])
        out.append(
            {
                "product": p["name"][:60],
                "brand": p.get("brand"),
                "baseline": base["score"],
                "maya_score": multi["score"],
                "maya_verdict": multi["verdict"],
                "flags": [f["matched"] for f in multi["flags"][:3]],
            }
        )
    return out


def run_checkpoint2():
    products = ALL_PRODUCTS
    dev_rows = score_vs_gold_rows(products, COMPATIBILITY_LABELS)
    hold_rows = score_vs_gold_rows(products, HOLDOUT_LABELS)

    irr = evaluate_irritant_detection(CANONICAL_PRODUCTS)
    dev_match = evaluate_user_matching(products, COMPATIBILITY_LABELS)
    hold_match = evaluate_user_matching(products, HOLDOUT_LABELS)

    return {
        "n_dev": len(COMPATIBILITY_LABELS),
        "n_holdout": len(HOLDOUT_LABELS),
        "n_holdout_products": len(HOLDOUT_PRODUCTS),
        "irritant_detection": irr,
        "dev": {
            "baseline": metrics_from_rows(dev_rows, "baseline_ok", "keyword_baseline"),
            "multi": metrics_from_rows(dev_rows, "multi_ok", "multi_criteria"),
            "score_ge_70": pack_binary(
                [r["gold"] for r in dev_rows],
                [int(r["score"] >= 70) for r in dev_rows],
                "score>=70",
            ),
            "ranking": dev_match["ranking"],
            "threshold_sweep": threshold_sweep(dev_rows),
            "weak": weak_cases(dev_rows),
            "rows": dev_rows,
        },
        "holdout": {
            "baseline": metrics_from_rows(hold_rows, "baseline_ok", "keyword_baseline"),
            "multi": metrics_from_rows(hold_rows, "multi_ok", "multi_criteria"),
            "score_ge_70": pack_binary(
                [r["gold"] for r in hold_rows],
                [int(r["score"] >= 70) for r in hold_rows],
                "score>=70",
            ),
            "ranking": hold_match["ranking"],
            "threshold_sweep": threshold_sweep(hold_rows),
            "weak": weak_cases(hold_rows),
            "rows": hold_rows,
        },
        "leave_one_product_out": leave_one_product_out(products, COMPATIBILITY_LABELS),
        "obf": obf_parse_stats(),
        "obf_maya_examples": example_obf_scores(),
        "samples": {
            "maya_cerave": sample_prediction(products, "maya", "cerave-moisturizing-cream"),
            "maya_retinol": sample_prediction(products, "maya", "retinol-serum"),
            "maya_aveeno": sample_prediction(products, "maya", "aveeno-daily"),
            "maya_olay": sample_prediction(products, "maya", "olay-regenerist"),
            "alex_retinol": sample_prediction(products, "alex", "retinol-serum"),
        },
    }


def dump_results(path):
    payload = run_checkpoint2()
    # json-friendly
    path.write_text(json.dumps(payload, indent=2))
    return payload
