# ingredient tags I put together for checkpoint 1
# fragrance allergens: EU Annex III "26" list (the common ones)
# comedogenic: those 0-5 charts (Fulton etc), not super scientific but people use them
# also alcohols, sulfates, essential oils
# this is just for the project, not medical advice


from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IngredientRecord:
    inci: str
    aliases: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    comedogenic: int = 0  # 0-5, I treat 3+ as acne risk
    notes: str = ""


def _rec(
    inci: str,
    aliases: list[str] | None = None,
    tags: list[str] | None = None,
    comedogenic: int = 0,
    notes: str = "",
) -> IngredientRecord:
    alias_tuple = tuple(dict.fromkeys([inci, *(aliases or [])]))
    return IngredientRecord(
        inci=inci,
        aliases=alias_tuple,
        tags=tuple(tags or ()),
        comedogenic=comedogenic,
        notes=notes,
    )


LEXICON: list[IngredientRecord] = [
    # --- EU fragrance allergens (the "26" list, I didn't put every expansion) ---
    _rec("parfum", ["fragrance", "perfume", "aroma"], ["fragrance"], notes="Undisclosed fragrance mixture"),
    _rec("linalool", tags=["fragrance_allergen", "fragrance"], notes="EU 26 allergen"),
    _rec("limonene", tags=["fragrance_allergen", "fragrance"], notes="EU 26 allergen"),
    _rec("citronellol", tags=["fragrance_allergen", "fragrance"], notes="EU 26 allergen"),
    _rec("geraniol", tags=["fragrance_allergen", "fragrance"], notes="EU 26 allergen"),
    _rec("citral", tags=["fragrance_allergen", "fragrance"], notes="EU 26 allergen"),
    _rec("eugenol", tags=["fragrance_allergen", "fragrance"], notes="EU 26 allergen"),
    _rec("isoeugenol", tags=["fragrance_allergen", "fragrance"], notes="EU 26 allergen"),
    _rec("coumarin", tags=["fragrance_allergen", "fragrance"], notes="EU 26 allergen"),
    _rec("cinnamal", ["cinnamaldehyde"], ["fragrance_allergen", "fragrance"], notes="EU 26 allergen"),
    _rec("cinnamyl alcohol", tags=["fragrance_allergen", "fragrance"]),
    _rec("benzyl alcohol", tags=["fragrance_allergen"], notes="Also a preservative; tagged as allergen when listed"),
    _rec("benzyl benzoate", tags=["fragrance_allergen", "fragrance"]),
    _rec("benzyl salicylate", tags=["fragrance_allergen", "fragrance"]),
    _rec("benzyl cinnamate", tags=["fragrance_allergen", "fragrance"]),
    _rec("hexyl cinnamal", ["hexyl cinnamaldehyde"], ["fragrance_allergen", "fragrance"]),
    _rec("amyl cinnamal", ["amyl cinnamaldehyde"], ["fragrance_allergen", "fragrance"]),
    _rec("alpha-isomethyl ionone", ["alpha isomethyl ionone"], ["fragrance_allergen", "fragrance"]),
    _rec("hydroxycitronellal", tags=["fragrance_allergen", "fragrance"]),
    _rec("farnesol", tags=["fragrance_allergen", "fragrance"]),
    _rec("anise alcohol", ["anisyl alcohol"], ["fragrance_allergen", "fragrance"]),
    _rec("methyl 2-octynoate", tags=["fragrance_allergen", "fragrance"]),
    _rec("evernia prunastri extract", ["oakmoss"], ["fragrance_allergen", "fragrance"]),
    _rec("evernia furfuracea extract", ["treemoss"], ["fragrance_allergen", "fragrance"]),
    _rec("linalyl acetate", tags=["fragrance"], notes="Lavender-related aroma compound"),
    _rec("acetyl cedrene", tags=["fragrance"]),
    _rec("terpineol", tags=["fragrance"]),
    # --- alcohols that sting if your barrier is messed up ---
    _rec(
        "alcohol denat",
        ["alcohol denat.", "alcohol", "ethanol", "sd alcohol", "alcohol denatured"],
        ["alcohol", "irritant"],
        notes="Denatured alcohol; drying/stinging on compromised barriers",
    ),
    # --- Surfactants ---
    _rec("sodium lauryl sulfate", ["sls", "sodium dodecyl sulfate"], ["sulfate", "irritant"]),
    _rec("sodium laureth sulfate", ["sles"], ["sulfate", "irritant"]),
    _rec("ammonium lauryl sulfate", tags=["sulfate", "irritant"]),
    # --- Essential oils / menthols ---
    _rec("melaleuca alternifolia leaf oil", ["tea tree oil", "tea tree"], ["essential_oil", "irritant"]),
    _rec("mentha piperita oil", ["peppermint oil"], ["essential_oil", "irritant"]),
    _rec("eucalyptus globulus leaf oil", ["eucalyptus oil"], ["essential_oil", "irritant"]),
    _rec("lavandula oil", ["lavandula oil/extract", "lavender oil", "lavandula angustifolia oil"], ["essential_oil", "fragrance"]),
    _rec("citrus aurantium peel oil", ["orange peel oil"], ["essential_oil", "fragrance", "fragrance_allergen"]),
    _rec("menthol", tags=["irritant"]),
    _rec("camphor", tags=["irritant"]),
    # --- actives that can irritate sensitive skin (ok for Alex, not Maya) ---
    _rec("retinol", tags=["retinoid", "irritant"]),
    _rec("retinal", ["retinaldehyde"], ["retinoid", "irritant"]),
    _rec("retinyl palmitate", tags=["retinoid"]),
    _rec("tretinoin", tags=["retinoid", "irritant"]),
    _rec("salicylic acid", tags=["aha_bha", "irritant"]),
    _rec("glycolic acid", tags=["aha_bha", "irritant"]),
    _rec("lactic acid", tags=["aha_bha"]),
    _rec("mandelic acid", tags=["aha_bha"]),
    _rec("ascorbic acid", ["vitamin c", "l-ascorbic acid"], ["irritant"], notes="Low-pH vitamin C can sting"),
    _rec("benzoyl peroxide", tags=["irritant"]),
    _rec(
        "witch hazel",
        [
            "hamamelis virginiana extract",
            "hamamelis virginiana water",
            "hamamelis virginiana (witch hazel) water",
            "hamamelis virginiana (witch hazel) extract",
        ],
        ["irritant", "alcohol"],
    ),
    # --- comedogenic stuff (Jordan hates these) ---
    # coconut oil is like a 4 on those charts
    _rec("cocos nucifera oil", ["coconut oil", "cocos nucifera (coconut) oil"], ["comedogenic"], 4),
    _rec("isopropyl myristate", ["isopropyl myrstate"], ["comedogenic"], 5),
    _rec("isopropyl palmitate", tags=["comedogenic"], comedogenic=4),
    _rec("theobroma cacao seed butter", ["cocoa butter", "theobroma cacao (cocoa) seed butter"], ["comedogenic"], 4),
    _rec("lauric acid", tags=["comedogenic"], comedogenic=4),
    _rec("myristyl myristate", tags=["comedogenic"], comedogenic=5),
    _rec("oleic acid", tags=["comedogenic"], comedogenic=3),
    _rec("stearic acid", tags=["comedogenic"], comedogenic=3),
    _rec("paraffinum liquidum", ["mineral oil", "paraffinum liquidium", "paraffin oil"], ["comedogenic"], 2),
    _rec("algal extract", ["algae extract"], ["comedogenic"], 5),
    _rec("lanolin", ["lanolin alcohol"], ["comedogenic", "allergen"], 2),
    _rec("sesamum indicum seed oil", ["sesame oil", "sesamum indicum (sesame) seed oil"], ["comedogenic", "sesame"], 3),
    # --- Food / plant allergens ---
    _rec(
        "avena sativa kernel flour",
        [
            "oat kernel flour",
            "colloidal oatmeal",
            "avena sativa (oat) kernel flour",
            "avena sativa kernel oil",
            "avena sativa (oat) kernel oil",
        ],
        ["oat", "gluten"],
        notes="Oat; relevant for oat/gluten-sensitive users",
    ),
    _rec("avena sativa straw extract", ["oat straw extract", "avena sativa (oat) straw extract"], ["oat", "gluten"]),
    _rec(
        "prunus amygdalus dulcis oil",
        ["sweet almond oil", "prunus amygdalus dulcis (sweet almond) oil", "almond oil"],
        ["tree_nut", "allergen", "comedogenic"],
        2,
    ),
    _rec(
        "glycine soja oil",
        [
            "soybean oil",
            "glycine soja (soybean) oil",
            "glycine soja (soyabean) oil",
            "soy oil",
            "glycine soya oil",
        ],
        ["soy"],
    ),
    _rec("butyrospermum parkii butter", ["shea butter", "butyrospermum parkii (shea) butter"], notes="Usually well tolerated; not tagged as risk"),
    # --- stuff that's usually fine / helpful ---
    _rec("ceramide np", ["ceramide 3"], ["ceramide", "soothing"]),
    _rec("ceramide ap", ["ceramide 6 ii"], ["ceramide", "soothing"]),
    _rec("ceramide eop", ["ceramide 1"], ["ceramide", "soothing"]),
    _rec("cholesterol", tags=["ceramide", "soothing"]),
    _rec("phytosphingosine", tags=["ceramide", "soothing"]),
    _rec("niacinamide", tags=["niacinamide", "soothing"]),
    _rec("sodium hyaluronate", ["hyaluronic acid", "hydrolyzed hyaluronic acid"], ["humectant"]),
    _rec("glycerin", ["glycerol"], ["humectant"]),
    _rec("panthenol", ["provitamin b5"], ["soothing", "humectant"]),
    _rec("allantoin", tags=["soothing"]),
    _rec("centella asiatica extract", ["cica", "madecassoside"], ["soothing"]),
    _rec("squalane", tags=["humectant"]),
    _rec("petrolatum", ["white petrolatum", "petroleum jelly"], ["occlusive"]),
    _rec("dimethicone", tags=["occlusive"]),
    _rec("tocopherol", ["vitamin e"], ["antioxidant"]),
    _rec("tocopheryl acetate", tags=["antioxidant"]),
    _rec("zinc pca", tags=["soothing"]),
    _rec("zinc oxide", tags=["soothing"]),
    # --- Preservatives flagged by some sensitive users ---
    _rec("methylparaben", tags=["paraben"]),
    _rec("propylparaben", tags=["paraben"]),
    _rec("ethylparaben", tags=["paraben"]),
    _rec("phenoxyethanol", notes="Common preservative; not scored as an irritant by default"),
    _rec("formaldehyde", tags=["irritant"]),
    _rec("dmdm hydantoin", tags=["irritant"], notes="Formaldehyde releaser"),
    _rec("diazolidinyl urea", tags=["irritant"], notes="Formaldehyde releaser"),
    _rec("imidazolidinyl urea", tags=["irritant"], notes="Formaldehyde releaser"),
    _rec("methylisothiazolinone", ["mi"], ["irritant", "allergen"]),
    _rec("methylchloroisothiazolinone", ["mci"], ["irritant", "allergen"]),
]


# words the keyword baseline looks for. no profile, just substring match.
# I probably missed some but it's enough to be a baseline.
BASELINE_BLACKLIST = (
    "parfum",
    "fragrance",
    "perfume",
    "linalool",
    "limonene",
    "citronellol",
    "geraniol",
    "citral",
    "eugenol",
    "coumarin",
    "cinnamal",
    "benzyl salicylate",
    "hexyl cinnamal",
    "amyl cinnamal",
    "alpha-isomethyl ionone",
    "alcohol denat",
    "sodium lauryl sulfate",
    "sodium laureth sulfate",
    "tea tree",
    "peppermint",
    "retinol",
    "salicylic acid",
    "glycolic acid",
    "benzoyl peroxide",
    "isopropyl myristate",
    "coconut oil",
    "cocos nucifera",
    "methylisothiazolinone",
    "diazolidinyl urea",
)


def alias_map() -> dict[str, list[str]]:
    return {rec.inci: list(rec.aliases) for rec in LEXICON}


def record_by_inci() -> dict[str, IngredientRecord]:
    return {rec.inci: rec for rec in LEXICON}


def all_alias_choices() -> list[str]:
    choices: list[str] = []
    seen: set[str] = set()
    for rec in LEXICON:
        for alias in rec.aliases:
            if alias not in seen:
                seen.add(alias)
                choices.append(alias)
    return choices
