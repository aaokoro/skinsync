# eval for checkpoint 1
# I labeled the pairs in catalog.py myself so the 1.00 is not that impressive yet
# just needed actual numbers instead of "the code ran"

from __future__ import annotations

from collections import defaultdict

from sklearn.metrics import precision_recall_fscore_support

from skinsync.baseline import baseline_score
from skinsync.catalog import COMPATIBILITY_LABELS, IRRITANT_GOLD, PROFILES
from skinsync.lexicon import BASELINE_BLACKLIST, record_by_inci
from skinsync.parse import parse_ingredients
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


def _product_map(products: list[dict]) -> dict[str, dict]:
    return {p["id"]: p for p in products}


_RISK_TAGS = {
    "fragrance",
    "fragrance_allergen",
    "irritant",
    "alcohol",
    "essential_oil",
    "sulfate",
    "retinoid",
    "aha_bha",
    "comedogenic",
    "tree_nut",
    "soy",
    "oat",
    "gluten",
    "sesame",
    "allergen",
}


def _is_risk(rec) -> bool:
    return bool(set(rec.tags) & _RISK_TAGS) or rec.comedogenic >= 3


def _baseline_detects(inci: str, blob: str, rec) -> bool:
    aliases = [a.lower() for a in (rec.aliases if rec else [inci])]
    if inci == "parfum" or "parfum" in aliases:
        return any(k in blob for k in ("parfum", "fragrance", "perfume"))
    needles = [k for k in BASELINE_BLACKLIST if k in aliases or any(k in a for a in aliases)]
    if not needles:
        needles = [a for a in aliases if a in BASELINE_BLACKLIST]
    return any(n in blob for n in needles)


def evaluate_irritant_detection(products: list[dict]) -> dict:
    # did we find the risk ingredients I marked
    pmap = _product_map(products)
    y_true: list[int] = []
    y_base: list[int] = []
    y_fuzzy: list[int] = []
    examples = []

    gold_by_product: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for pid, inci, label in IRRITANT_GOLD:
        gold_by_product[pid].append((inci, label))

    records = record_by_inci()

    for pid, pairs in gold_by_product.items():
        product = pmap[pid]
        raw = product["ingredients_raw"]
        blob = raw.lower()
        tokens = parse_ingredients(raw)
        matched_canonical = set()
        for token in tokens:
            rec, score = match_parsed(token)
            if rec and score >= 90:
                matched_canonical.add(rec.inci)

        for inci, label in pairs:
            rec = records.get(inci)
            y_true.append(label)
            y_base.append(int(_baseline_detects(inci, blob, rec)))
            fuzzy_present = inci in matched_canonical
            fuzzy_risk = bool(rec and _is_risk(rec) and fuzzy_present)
            y_fuzzy.append(int(fuzzy_risk if label == 1 else (fuzzy_present and _is_risk(rec) if rec else 0)))
            if label == 1 and len(examples) < 14:
                examples.append(
                    {
                        "product": product["name"],
                        "gold": inci,
                        "baseline": bool(y_base[-1]),
                        "fuzzy": bool(y_fuzzy[-1]),
                    }
                )

    def pack(preds: list[int], method: str) -> dict:
        p, r, f1, _ = precision_recall_fscore_support(
            y_true, preds, average="binary", zero_division=0
        )
        return {
            "method": method,
            "precision": round(float(p), 3),
            "recall": round(float(r), 3),
            "f1": round(float(f1), 3),
            "n": len(y_true),
            "positives": int(sum(y_true)),
        }

    return {
        "baseline": pack(y_base, "keyword_baseline"),
        "multi_criteria_matcher": pack(y_fuzzy, "fuzzy_lexicon_match"),
        "examples": examples,
    }


def evaluate_user_matching(products: list[dict], labels=None) -> dict:
    if labels is None:
        labels = COMPATIBILITY_LABELS
    pmap = _product_map(products)
    y_true: list[int] = []
    y_base: list[int] = []
    y_multi: list[int] = []
    rows = []

    for profile_id, product_id, compatible, rationale in labels:
        product = pmap[product_id]
        profile = _profile(profile_id)
        base = baseline_score(product["ingredients_raw"])
        multi = score_product(product["ingredients_raw"], profile)
        y_true.append(int(compatible))
        y_base.append(int(base["compatible"]))
        y_multi.append(int(multi["compatible"]))
        rows.append(
            {
                "profile": profile.name,
                "product": product["name"],
                "gold": "compatible" if compatible else "not compatible",
                "baseline": base["verdict"],
                "baseline_score": base["score"],
                "multi_score": multi["score"],
                "multi_verdict": multi["verdict"],
                "multi_compatible": multi["compatible"],
                "flags": [f["matched"] for f in multi["flags"][:4]],
                "rationale": rationale,
            }
        )

    def pack(preds: list[int], method: str) -> dict:
        # looking at the unsafe class (products they shouldn't use)
        # plus overall accuracy
        y_unsafe = [1 - y for y in y_true]
        p_unsafe = [1 - y for y in preds]
        p, r, f1, _ = precision_recall_fscore_support(
            y_unsafe, p_unsafe, average="binary", zero_division=0
        )
        acc = sum(int(a == b) for a, b in zip(y_true, preds)) / len(y_true)
        return {
            "method": method,
            "unsafe_precision": round(float(p), 3),
            "unsafe_recall": round(float(r), 3),
            "unsafe_f1": round(float(f1), 3),
            "label_accuracy": round(float(acc), 3),
            "n": len(y_true),
        }

    # for each person, how many of the top 5 scored products did I label as ok
    by_profile: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
    for row, (profile_id, product_id, compatible, _) in zip(rows, labels):
        by_profile[profile_id].append((row["multi_score"], row["baseline_score"], compatible))

    ranking = []
    for pid, triples in by_profile.items():
        multi_sorted = sorted(triples, key=lambda t: t[0], reverse=True)
        base_sorted = sorted(triples, key=lambda t: t[1], reverse=True)
        k = min(5, len(triples))
        ranking.append(
            {
                "profile": _profile(pid).name,
                "n_labeled": len(triples),
                "multi_top5_safe_rate": round(
                    sum(t[2] for t in multi_sorted[:k]) / k, 3
                ),
                "baseline_top5_safe_rate": round(
                    sum(t[2] for t in base_sorted[:k]) / k, 3
                ),
            }
        )

    return {
        "baseline": pack(y_base, "keyword_baseline"),
        "multi_criteria": pack(y_multi, "multi_criteria"),
        "ranking": ranking,
        "sample_rows": rows[:12],
        "all_rows": rows,
    }


def sample_prediction(products: list[dict], profile_id: str, product_id: str) -> dict:
    pmap = _product_map(products)
    product = pmap[product_id]
    profile = _profile(profile_id)
    return {
        "profile": {
            "id": profile.id,
            "name": profile.name,
            "skin_type": profile.skin_type,
            "concerns": profile.concerns,
            "sensitivities": profile.sensitivities,
        },
        "product": {
            "id": product["id"],
            "name": product["name"],
            "brand": product.get("brand"),
        },
        "baseline": baseline_score(product["ingredients_raw"]),
        "multi_criteria": score_product(product["ingredients_raw"], profile),
    }


def run_evaluation(products: list[dict]) -> dict:
    return {
        "irritant_detection": evaluate_irritant_detection(products),
        "user_matching": evaluate_user_matching(products),
        "sample_maya_cerave": sample_prediction(products, "maya", "cerave-moisturizing-cream"),
        "sample_maya_messy": sample_prediction(products, "maya", "messy-dupe-lotion"),
        "sample_jordan_coconut": sample_prediction(products, "jordan", "coconut-oil-balm"),
        "sample_priya_almond": sample_prediction(products, "priya", "almond-night-cream"),
        "sample_alex_retinol": sample_prediction(products, "alex", "retinol-serum"),
    }
