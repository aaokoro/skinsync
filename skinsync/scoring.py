# profile-aware scorer
# start at 100, subtract for stuff that matters to THIS person, add a little for ceramides etc
# the penalty numbers are just what I landed on after looking at the labeled pairs
# TODO: actually tune these properly later, they're kinda vibes-based right now

from __future__ import annotations

from dataclasses import dataclass, field

from skinsync.lexicon import IngredientRecord, record_by_inci
from skinsync.parse import ParsedIngredient, build_alias_index, match_ingredient, parse_ingredients
from skinsync.lexicon import alias_map, all_alias_choices


# map my lexicon tags to the sensitivity names I put on the profiles
TAG_TO_SENSITIVITY = {
    "fragrance": "fragrance",
    "fragrance_allergen": "fragrance",
    "alcohol": "alcohol",
    "essential_oil": "essential_oils",
    "sulfate": "sulfates",
    "retinoid": "retinoids",
    "aha_bha": "acids",
    "tree_nut": "tree_nuts",
    "soy": "soy",
    "oat": "gluten",
    "gluten": "gluten",
    "sesame": "sesame",
    "paraben": "parabens",
}

# bumped alcohol and coconut because Jordan was still getting coconut oil as "ok"
PENALTY = {
    "fragrance_allergen": 16,
    "fragrance": 18,
    "irritant": 12,
    "alcohol": 22,
    "essential_oil": 12,
    "sulfate": 12,
    "retinoid": 14,
    "aha_bha": 10,
    "comedogenic": 12,
    "personal_allergen": 28,
}

BONUS = {
    "ceramide": 8,
    "niacinamide": 6,
    "soothing": 5,
    "humectant": 3,
    "occlusive": 3,
}


@dataclass
class SkinProfile:
    id: str
    name: str
    skin_type: str
    concerns: list[str] = field(default_factory=list)
    sensitivities: list[str] = field(default_factory=list)
    notes: str = ""

    def has(self, sensitivity: str) -> bool:
        return sensitivity in self.sensitivities


@dataclass
class Flag:
    ingredient: str
    matched: str | None
    tags: list[str]
    reason: str
    severity: str  # info / caution / avoid


def _index():
    amap = alias_map()
    return build_alias_index(amap), all_alias_choices(), record_by_inci()


# build once so I'm not doing this for every product
_ALIAS_INDEX, _CHOICES, _RECORDS = _index()


def match_parsed(
    token: ParsedIngredient, allow_fuzzy: bool = True
) -> tuple[IngredientRecord | None, float]:
    canonical, score = match_ingredient(
        token, _ALIAS_INDEX, _CHOICES, allow_fuzzy=allow_fuzzy
    )
    if canonical is None:
        return None, 0.0
    return _RECORDS.get(canonical), score


def profile_applies(rec: IngredientRecord, profile: SkinProfile) -> tuple[bool, str]:
    # should this ingredient actually count against this person?
    tags = set(rec.tags)
    for tag, sensitivity in TAG_TO_SENSITIVITY.items():
        if tag in tags and profile.has(sensitivity):
            return True, f"listed {sensitivity.replace('_', ' ')} sensitivity"
    if rec.comedogenic >= 2 and (profile.skin_type == "oily" or "acne" in profile.concerns):
        return True, "acne-prone / oily profile vs comedogenic ingredient"
    # alcohol denat is annoying even if they didn't list alcohol specifically
    if rec.inci in {"alcohol denat", "witch hazel"}:
        return True, "denatured alcohol / astringent is a general leave-on irritant"
    if "irritant" in tags or "alcohol" in tags or "fragrance" in tags:
        if profile.skin_type == "sensitive" or "irritation" in profile.concerns or "sensitivity" in profile.concerns:
            return True, "sensitive / irritation-prone profile"
    # retinol/BHA is fine for Alex (aging) but not Maya (reactive)
    if "retinoid" in tags or "aha_bha" in tags:
        if profile.skin_type in {"dry", "sensitive"} and "aging" not in profile.concerns:
            return True, "barrier-compromised skin vs active exfoliant/retinoid"
    return False, ""


def score_product(
    ingredient_text: str, profile: SkinProfile, allow_fuzzy: bool = True
) -> dict:
    tokens = parse_ingredients(ingredient_text)
    flags = []
    matched_helpful = []
    penalties = 0
    bonuses = 0
    matched_count = 0

    for token in tokens:
        rec, match_score = match_parsed(token, allow_fuzzy=allow_fuzzy)
        if rec is None:
            continue
        matched_count += 1
        applies, why = profile_applies(rec, profile)
        tags = list(rec.tags)
        if applies:
            local = 0
            # personal allergen hits harder (Priya + almond, Maya + perfume)
            if any(t in TAG_TO_SENSITIVITY and profile.has(TAG_TO_SENSITIVITY[t]) for t in tags):
                local += PENALTY["personal_allergen"]
            if "fragrance" in tags or "fragrance_allergen" in tags:
                local += PENALTY["fragrance"] if "fragrance" in tags else 0
                local += PENALTY["fragrance_allergen"] if "fragrance_allergen" in tags else 0
            if "alcohol" in tags:
                local += PENALTY["alcohol"]
            if "irritant" in tags:
                local += PENALTY["irritant"]
            if "essential_oil" in tags:
                local += PENALTY["essential_oil"]
            if "sulfate" in tags:
                local += PENALTY["sulfate"]
            if "retinoid" in tags:
                local += PENALTY["retinoid"]
            if "aha_bha" in tags:
                local += PENALTY["aha_bha"]
            if rec.comedogenic >= 2:
                # extra for higher ratings (coconut is 4)
                local += PENALTY["comedogenic"] + 6 * rec.comedogenic
            local = min(local, 45)  # cap so one ingredient doesn't go crazy
            penalties += local
            severity = "avoid" if local >= 20 else "caution"
            flags.append(
                Flag(
                    ingredient=token.raw,
                    matched=rec.inci,
                    tags=tags,
                    reason=why or rec.notes,
                    severity=severity,
                )
            )
        else:
            gained = 0
            for tag, pts in BONUS.items():
                if tag in tags:
                    gained += pts
            if gained:
                bonuses += min(gained, 12)
                matched_helpful.append(rec.inci)

    # 60 felt like a reasonable "would I tell them to try this" cutoff
    score = max(0, min(100, 100 - penalties + min(bonuses, 18)))
    avoid_n = sum(1 for f in flags if f.severity == "avoid")
    if score >= 85 and avoid_n == 0:
        verdict = "excellent match"
    elif score >= 70:
        verdict = "good match"
    elif score >= 55:
        verdict = "use with caution"
    else:
        verdict = "poor match"

    return {
        "method": "fuzzy_profile" if allow_fuzzy else "exact_profile",
        "score": int(round(score)),
        "compatible": score >= 60 and avoid_n == 0,
        "verdict": verdict,
        "parsed_count": len(tokens),
        "matched_lexicon": matched_count,
        "penalties": penalties,
        "bonuses": min(bonuses, 18),
        "helpful": sorted(set(matched_helpful)),
        "flags": [
            {
                "ingredient": f.ingredient,
                "matched": f.matched,
                "tags": f.tags,
                "reason": f.reason,
                "severity": f.severity,
            }
            for f in flags
        ],
        "tokens": [t.normalized for t in tokens[:40]],
    }


def profile_blind_score(ingredient_text: str, allow_fuzzy: bool = True) -> dict:
    # same lexicon as the scorer, but it ignores the person
    # any risk-tagged ingredient = not compatible
    risk_tags = {
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
        "allergen",
    }
    tokens = parse_ingredients(ingredient_text)
    hits = []
    for token in tokens:
        rec, _ = match_parsed(token, allow_fuzzy=allow_fuzzy)
        if rec is None:
            continue
        if set(rec.tags) & risk_tags or rec.comedogenic >= 3:
            hits.append(rec.inci)
    ok = len(hits) == 0
    return {
        "method": "profile_blind_lexicon",
        "score": 100 if ok else 0,
        "compatible": ok,
        "hits": hits,
        "verdict": "compatible" if ok else "flagged",
    }
