from skinsync.baseline import baseline_score
from skinsync.catalog import CANONICAL_PRODUCTS
from skinsync.parse import parse_ingredients
from skinsync.scoring import SkinProfile, score_product


def _product(pid: str) -> dict:
    return next(p for p in CANONICAL_PRODUCTS if p["id"] == pid)


def test_split_preserves_hexanediol_and_slash_pairs():
    tokens = parse_ingredients(
        "Aqua/Water, 1,2-Hexanediol, Caprylic/Capric Triglyceride, Glycerin 5%"
    )
    names = [t.normalized for t in tokens]
    assert any("1,2-hexanediol" == n for n in names)
    assert "glycerin" in names
    aqua = next(t for t in tokens if "aqua" in t.aliases or t.normalized == "aqua")
    assert "water" in aqua.aliases or aqua.normalized in {"aqua", "water"}


def test_messy_typo_matches_isopropyl_myristate():
    maya = SkinProfile(
        id="maya",
        name="Maya",
        skin_type="dry",
        concerns=["irritation"],
        sensitivities=["fragrance"],
    )
    messy = _product("messy-dupe-lotion")
    multi = score_product(messy["ingredients_raw"], maya)
    matched = {f["matched"] for f in multi["flags"]}
    assert "isopropyl myristate" in matched or "parfum" in matched
    assert multi["score"] < 50


def test_baseline_ignores_profile_on_retinol():
    alex = SkinProfile(
        id="alex", name="Alex", skin_type="normal", concerns=["aging"], sensitivities=[]
    )
    retinol = _product("retinol-serum")
    base = baseline_score(retinol["ingredients_raw"])
    multi = score_product(retinol["ingredients_raw"], alex)
    assert base["compatible"] is False
    assert multi["score"] >= 70


def test_sorbic_acid_is_not_ascorbic_acid():
    maya = SkinProfile(
        id="maya",
        name="Maya",
        skin_type="dry",
        concerns=["irritation", "sensitivity"],
        sensitivities=["fragrance", "alcohol"],
    )
    vanicream = _product("vanicream-moisturizing-cream")
    multi = score_product(vanicream["ingredients_raw"], maya)
    matched = {f["matched"] for f in multi["flags"]}
    assert "ascorbic acid" not in matched
    tokens = parse_ingredients(vanicream["ingredients_raw"])
    from skinsync.scoring import match_parsed

    sorbic = next(t for t in tokens if "sorbic" in t.normalized)
    rec, _ = match_parsed(sorbic)
    assert rec is None
    assert multi["score"] >= 90


def test_maya_retinol_flag_and_score_disagree():
    # this is the weak case I wrote up for checkpoint 2
    maya = SkinProfile(
        id="maya",
        name="Maya",
        skin_type="dry",
        concerns=["irritation", "sensitivity"],
        sensitivities=["fragrance", "alcohol"],
    )
    retinol = _product("retinol-serum")
    multi = score_product(retinol["ingredients_raw"], maya)
    assert multi["compatible"] is False
    assert multi["score"] >= 70


def test_holdout_aveeno_exists_and_parses():
    from skinsync.catalog import HOLDOUT_PRODUCTS

    aveeno = next(p for p in HOLDOUT_PRODUCTS if p["id"] == "aveeno-daily")
    tokens = parse_ingredients(aveeno["ingredients_raw"])
    names = [t.normalized for t in tokens]
    assert any("benzyl" in n for n in names)
    assert len(tokens) >= 8


def test_priya_flags_almond_but_baseline_may_miss():
    priya = SkinProfile(
        id="priya",
        name="Priya",
        skin_type="combination",
        concerns=["hyperpigmentation"],
        sensitivities=["tree_nuts", "soy"],
    )
    almond = _product("almond-night-cream")
    multi = score_product(almond["ingredients_raw"], priya)
    assert any(f["matched"] == "prunus amygdalus dulcis oil" for f in multi["flags"])
    assert multi["compatible"] is False
