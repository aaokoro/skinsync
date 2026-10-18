# products + fake people I scored by hand for checkpoint 1
# I typed the INCI lists from labels / brand sites
# Maya/Jordan/Priya/Alex are made up, not real users

from __future__ import annotations

# the 11 I actually labeled. messy-dupe-lotion is fake OCR on purpose
CANONICAL_PRODUCTS = [
    {
        "id": "cerave-moisturizing-cream",
        "name": "CeraVe Moisturizing Cream",  # copied off the tub
        "brand": "CeraVe",
        "category": "moisturizer",
        "source": "canonical_label",
        "ingredients_raw": (
            "Aqua/Water, Glycerin, Cetearyl Alcohol, Caprylic/Capric Triglyceride, "
            "Cetyl Alcohol, Ceteareth-20, Petrolatum, Potassium Phosphate, Ceramide NP, "
            "Ceramide AP, Ceramide EOP, Carbomer, Dimethicone, Behentrimonium Methosulfate, "
            "Sodium Lauroyl Lactylate, Sodium Hyaluronate, Cholesterol, Phenoxyethanol, "
            "Disodium EDTA, Dipotassium Phosphate, Tocopherol, Phytosphingosine, Xanthan Gum, "
            "Ethylhexylglycerin"
        ),
    },
    {
        "id": "vanicream-moisturizing-cream",
        "name": "Vanicream Moisturizing Cream",  # this one almost matched sorbic -> ascorbic oops
        "brand": "Vanicream",
        "category": "moisturizer",
        "source": "canonical_label",
        "ingredients_raw": (
            "Water, White Petrolatum, Sorbitol, Cetearyl Alcohol, Propylene Glycol, "
            "Ceteareth-20, Simethicone, Glyceryl Stearate, PEG-30 Stearate, Sorbic Acid, BHT"
        ),
    },
    {
        "id": "ordinary-niacinamide",
        "name": "Niacinamide 10% + Zinc 1%",
        "brand": "The Ordinary",
        "category": "serum",
        "source": "canonical_label",
        "ingredients_raw": (
            "Aqua (Water), Niacinamide, Pentylene Glycol, Zinc PCA, Dimethyl Isosorbide, "
            "Tamarindus Indica Seed Gum, Xanthan Gum, Isoceteth-20, Ethoxydiglycol, "
            "Phenoxyethanol, Chlorphenesin"
        ),
    },
    {
        "id": "ordinary-ha",
        "name": "Hyaluronic Acid 2% + B5",
        "brand": "The Ordinary",
        "category": "serum",
        "source": "canonical_label",
        "ingredients_raw": (
            "Aqua (Water), Sodium Hyaluronate, Sodium Hyaluronate Crosspolymer, "
            "Panthenol, Ahnfeltia Concinna Extract, Glycerin, Pentylene Glycol, "
            "Propanediol, PPG-26-Buteth-26, PEG-40 Hydrogenated Castor Oil, "
            "Polyacrylate Crosspolymer-6, Sodium Benzoate, Ethylhexylglycerin, "
            "Phenoxyethanol, Chlorphenesin"
        ),
    },
    {
        "id": "paulas-choice-bha",
        "name": "Skin Perfecting 2% BHA Liquid Exfoliant",
        "brand": "Paula's Choice",
        "category": "exfoliant",
        "source": "canonical_label",
        "ingredients_raw": (
            "Water, Methylpropanediol, Butylene Glycol, Salicylic Acid, Polysorbate 20, "
            "Camellia Oleifera Leaf Extract, Sodium Hydroxide, Tetrasodium EDTA"
        ),
    },
    {
        "id": "neutrogena-oil-free-acne-wash",
        "name": "Oil-Free Acne Wash",
        "brand": "Neutrogena",
        "category": "cleanser",
        "source": "canonical_label",
        "ingredients_raw": (
            "Water, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Sodium Chloride, "
            "Salicylic Acid, Fragrance, Linoleamide DEA, Menthol, Aloe Barbadensis Leaf Extract, "
            "Propylene Glycol, Sodium Benzoate, Sodium Hydroxide, Yellow 5, Red 40"
        ),
    },
    {
        "id": "coconut-oil-balm",
        "name": "Virgin Coconut Oil Skin Balm",
        "brand": "Generic",
        "category": "balm",
        "source": "canonical_label",
        "ingredients_raw": "Cocos Nucifera (Coconut) Oil, Tocopherol, Fragrance, Linalool, Limonene",
    },
    {
        "id": "almond-night-cream",
        "name": "Sweet Almond Night Cream",
        "brand": "Generic",
        "category": "moisturizer",
        "source": "canonical_label",
        "ingredients_raw": (
            "Aqua, Prunus Amygdalus Dulcis Oil / Sweet Almond Oil, Glycerin, Cetearyl Alcohol, "
            "Glyceryl Stearate, Parfum, Hexyl Cinnamal, Benzyl Salicylate, Phenoxyethanol"
        ),
    },
    {
        "id": "retinol-serum",
        "name": "0.5% Retinol Night Serum",
        "brand": "Generic",
        "category": "serum",
        "source": "canonical_label",
        "ingredients_raw": (
            "Water, Propanediol, Retinol, Squalane, Dimethicone, Glycerin, Phenoxyethanol, "
            "Tocopherol, Sodium Hyaluronate, Carbomer, Sodium Hydroxide"
        ),
    },
    {
        "id": "alcohol-toner",
        "name": "Clarifying Witch Hazel Toner",
        "brand": "Generic",
        "category": "toner",
        "source": "canonical_label",
        "ingredients_raw": (
            "Alcohol Denat., Hamamelis Virginiana (Witch Hazel) Water, Water, Menthol, "
            "Fragrance, Limonene, Citral, Blue 1"
        ),
    },
    {
        "id": "messy-dupe-lotion",
        "name": "Deep Moisture Body Lotion (messy OCR-style INCI)",  # I spelled MYRSTATE / PERFUME / SOYABEAN wrong on purpose
        "brand": "Generic",
        "category": "moisturizer",
        "source": "canonical_messy",
        "ingredients_raw": (
            "WATER, MINERAL OIL, GLYCERIN, PETROLATUM, ISOPROPYL MYRSTATE, "
            "AVENA SATIVA (OAT) STRAW EXTRACT, PERFUME, BENZYL SALICYLATE, "
            "CITRONELLOL, HEXYL CINNAMAL, LIMONENE, LINALOOL, AMYL CINNAMAL, "
            "GLYCINE SOJA (SOYABEAN) OIL, METHYL PARABEN"
        ),
    },
]


# checkpoint 2 holdout — I typed these AFTER I set the penalty numbers
# so I wouldn't just be scoring the same 11 products I already tuned on
HOLDOUT_PRODUCTS = [
    {
        "id": "cosrx-snail",
        "name": "Advanced Snail 96 Mucin Power Essence",
        "brand": "COSRX",
        "category": "serum",
        "source": "holdout_label",
        "ingredients_raw": (
            "Snail Secretion Filtrate, Betaine, Butylene Glycol, 1,2-Hexanediol, "
            "Sodium Hyaluronate, Panthenol, Arginine, Allantoin, Ethyl Hexanediol, "
            "Sodium EDTA, Phenoxyethanol, Sodium Benzoate"
        ),
    },
    {
        "id": "lrp-toleriane",
        "name": "Toleriane Hydrating Gentle Cleanser",
        "brand": "La Roche-Posay",
        "category": "cleanser",
        "source": "holdout_label",
        "ingredients_raw": (
            "Water, Glycerin, Niacinamide, Coco-Betaine, Sodium Chloride, "
            "Sodium Hydroxide, Citric Acid, Caprylyl Glycol, "
            "Trisodium Ethylenediamine Disuccinate, Sodium Benzoate"
        ),
    },
    {
        "id": "ordinary-aha-peel",
        "name": "AHA 30% + BHA 2% Peeling Solution",
        "brand": "The Ordinary",
        "category": "exfoliant",
        "source": "holdout_label",
        "ingredients_raw": (
            "Glycolic Acid, Aqua, Aloe Barbadensis Leaf Water, Sodium Hydroxide, "
            "Daucus Carota Sativa Root Extract, Propanediol, Cocamidopropyl Dimethylamine, "
            "Salicylic Acid, Lactic Acid, Tartaric Acid, Citric Acid, "
            "Sodium Hyaluronate Crosspolymer, Pentylene Glycol, Xanthan Gum, "
            "Polysorbate 20, Potassium Sorbate, Sodium Benzoate, Ethylhexylglycerin, "
            "1,2-Hexanediol, Caprylyl Glycol"
        ),
    },
    {
        "id": "aveeno-daily",
        "name": "Daily Moisturizing Lotion",
        "brand": "Aveeno",
        "category": "moisturizer",
        "source": "holdout_label",
        "ingredients_raw": (
            "Water, Glycerin, Distearyldimonium Chloride, Petrolatum, "
            "Isopropyl Palmitate, Cetyl Alcohol, Dimethicone, "
            "Avena Sativa (Oat) Kernel Flour, Benzyl Alcohol, Steareth-20, "
            "Stearyl Alcohol, Avena Sativa (Oat) Kernel Oil"
        ),
    },
    {
        "id": "olay-regenerist",
        "name": "Regenerist Micro-Sculpting Cream",
        "brand": "Olay",
        "category": "moisturizer",
        "source": "holdout_label",
        "ingredients_raw": (
            "Water, Glycerin, Niacinamide, Isohexadecane, Dimethicone, "
            "Isopropyl Isostearate, Palmitoyl Pentapeptide-4, Panthenol, "
            "Tocopheryl Acetate, Cetyl Alcohol, PEG-100 Stearate, "
            "Methylparaben, Ethylparaben, Propylparaben, Fragrance, "
            "Disodium EDTA, Citric Acid"
        ),
    },
    {
        "id": "cerave-foaming",
        "name": "Foaming Facial Cleanser",
        "brand": "CeraVe",
        "category": "cleanser",
        "source": "holdout_label",
        "ingredients_raw": (
            "Aqua/Water, Cocamidopropyl Hydroxysultaine, Glycerin, "
            "Sodium Lauroyl Sarcosinate, Niacinamide, Sodium Methyl Cocoyl Taurate, "
            "Ceramide NP, Ceramide AP, Ceramide EOP, Carbomer, Methylparaben, "
            "Sodium Lauroyl Lactylate, Cholesterol, Disodium EDTA, Propylparaben, "
            "Citric Acid, Phytosphingosine, Xanthan Gum, Sodium Hydroxide"
        ),
    },
]

ALL_PRODUCTS = CANONICAL_PRODUCTS + HOLDOUT_PRODUCTS

# fake profiles so I can test different sensitivities
PROFILES = [
    {
        "id": "maya",
        "name": "Maya",
        "skin_type": "dry",
        "concerns": ["irritation", "dryness", "sensitivity"],
        "sensitivities": ["fragrance", "alcohol", "essential_oils"],
        "notes": "Reactive dry skin. Fragrance and denatured alcohol are hard no's.",
    },
    {
        "id": "jordan",
        "name": "Jordan",
        "skin_type": "oily",
        "concerns": ["acne"],
        "sensitivities": [],
        "notes": "Oily, acne-prone. Avoid comedogenic oils; BHA/niacinamide are welcome.",
    },
    {
        "id": "priya",
        "name": "Priya",
        "skin_type": "combination",
        "concerns": ["hyperpigmentation"],
        "sensitivities": ["tree_nuts", "soy"],
        "notes": "Nut and soy allergy. Otherwise tolerates most actives.",
    },
    {
        "id": "alex",
        "name": "Alex",
        "skin_type": "normal",
        "concerns": ["aging"],
        "sensitivities": [],
        "notes": "Normal skin, anti-aging. Retinol is desired, not a risk.",
    },
]


# labels I made myself. 1 = I'd say this is ok for them, 0 = no
# small set so the F1 looking perfect is a little sus, I know
COMPATIBILITY_LABELS = [
    # Maya: dry + fragrance/alcohol issues. ceramides yes, perfume/retinol/BHA no
    ("maya", "cerave-moisturizing-cream", 1, "Fragrance-free ceramides and petrolatum for dry barrier"),
    ("maya", "vanicream-moisturizing-cream", 1, "Minimal, fragrance-free moisturizer"),
    ("maya", "ordinary-ha", 1, "Simple hydrating serum without perfume or alcohol"),
    ("maya", "ordinary-niacinamide", 1, "No fragrance; niacinamide is usually tolerated"),
    ("maya", "coconut-oil-balm", 0, "Fragrance plus coconut oil"),
    ("maya", "almond-night-cream", 0, "Parfum and EU allergens"),
    ("maya", "alcohol-toner", 0, "Alcohol denat and fragrance"),
    ("maya", "neutrogena-oil-free-acne-wash", 0, "SLES, fragrance, menthol, BHA"),
    ("maya", "retinol-serum", 0, "Retinol too aggressive for currently reactive skin"),
    ("maya", "paulas-choice-bha", 0, "Leave-on BHA stings a compromised barrier"),
    ("maya", "messy-dupe-lotion", 0, "Perfume and six EU fragrance allergens"),
    # Jordan: acne-prone — skip coconut/IPM/heavy butters; BHA and niacinamide good
    ("jordan", "ordinary-niacinamide", 1, "Niacinamide + zinc, no heavy oils"),
    ("jordan", "paulas-choice-bha", 1, "2% BHA is a standard acne leave-on"),
    ("jordan", "cerave-moisturizing-cream", 1, "Non-fragranced, widely used with acne routines"),
    ("jordan", "ordinary-ha", 1, "Light hydrator"),
    ("jordan", "coconut-oil-balm", 0, "Coconut oil is highly comedogenic"),
    ("jordan", "almond-night-cream", 0, "Almond oil plus fragrance"),
    ("jordan", "messy-dupe-lotion", 0, "Mineral oil, IPM, fragrance"),
    ("jordan", "neutrogena-oil-free-acne-wash", 1, "Acne wash; stripping but on-label for this profile"),
    ("jordan", "alcohol-toner", 0, "Harsh alcohol toner, poor long-term acne care"),
    ("jordan", "vanicream-moisturizing-cream", 1, "Simple cream, not a comedogenic oil blend"),
    # Priya: nut + soy allergy
    ("priya", "cerave-moisturizing-cream", 1, "No nut or soy oils"),
    ("priya", "vanicream-moisturizing-cream", 1, "No nut or soy oils"),
    ("priya", "ordinary-niacinamide", 1, "No nut or soy oils"),
    ("priya", "almond-night-cream", 0, "Sweet almond oil"),
    ("priya", "messy-dupe-lotion", 0, "Soybean oil"),
    ("priya", "coconut-oil-balm", 1, "Coconut is not a tree nut; no soy"),
    ("priya", "ordinary-ha", 1, "No nut or soy oils"),
    ("priya", "paulas-choice-bha", 1, "No nut or soy oils"),
    # Alex: aging, can use retinol; fragrance is not a blocker
    ("alex", "retinol-serum", 1, "On-target anti-aging active"),
    ("alex", "cerave-moisturizing-cream", 1, "Barrier support under retinol"),
    ("alex", "ordinary-niacinamide", 1, "Supportive serum"),
    ("alex", "alcohol-toner", 0, "Drying toner fights an aging barrier"),
    ("alex", "ordinary-ha", 1, "Hydration support"),
    ("alex", "paulas-choice-bha", 1, "Exfoliant compatible with aging goals"),
]


# labeled AFTER checkpoint 1. I did not change PENALTY / BONUS to fit these.
HOLDOUT_LABELS = [
    ("maya", "cosrx-snail", 1, "simple hydrating essence, no perfume"),
    ("maya", "lrp-toleriane", 1, "fragrance-free cleanser"),
    ("maya", "ordinary-aha-peel", 0, "30% AHA is way too much for reactive skin"),
    ("maya", "aveeno-daily", 1, "classic drugstore lotion for dry skin, I'd still try it"),
    ("maya", "olay-regenerist", 0, "has fragrance"),
    ("maya", "cerave-foaming", 1, "fragrance-free CeraVe cleanser"),
    ("jordan", "cosrx-snail", 1, "light, not an oil bomb"),
    ("jordan", "ordinary-aha-peel", 1, "acids are kind of the point for acne"),
    ("jordan", "aveeno-daily", 0, "isopropyl palmitate is comedogenic"),
    ("jordan", "olay-regenerist", 1, "fragrance isn't his issue"),
    ("jordan", "cerave-foaming", 1, "fine daily cleanser"),
    ("priya", "cosrx-snail", 1, "no nut or soy"),
    ("priya", "aveeno-daily", 1, "oat is not her allergy"),
    ("priya", "olay-regenerist", 1, "no nut or soy"),
    ("priya", "lrp-toleriane", 1, "no nut or soy"),
    ("alex", "cosrx-snail", 1, "hydration under retinol"),
    ("alex", "ordinary-aha-peel", 1, "he can handle acids"),
    ("alex", "olay-regenerist", 1, "anti-aging cream, fragrance isn't a dealbreaker"),
    ("alex", "lrp-toleriane", 1, "gentle cleanser"),
]


# did this ingredient get caught as a risk? 1/0, not personalized
# (product_id, inci name as I have it in lexicon.py, is_risk)
IRRITANT_GOLD = [
    ("coconut-oil-balm", "parfum", 1),
    ("coconut-oil-balm", "linalool", 1),
    ("coconut-oil-balm", "limonene", 1),
    ("coconut-oil-balm", "cocos nucifera oil", 1),
    ("coconut-oil-balm", "tocopherol", 0),
    ("almond-night-cream", "parfum", 1),
    ("almond-night-cream", "hexyl cinnamal", 1),
    ("almond-night-cream", "benzyl salicylate", 1),
    ("almond-night-cream", "prunus amygdalus dulcis oil", 1),
    ("almond-night-cream", "glycerin", 0),
    ("almond-night-cream", "phenoxyethanol", 0),
    ("alcohol-toner", "alcohol denat", 1),
    ("alcohol-toner", "parfum", 1),
    ("alcohol-toner", "limonene", 1),
    ("alcohol-toner", "citral", 1),
    ("alcohol-toner", "menthol", 1),
    ("alcohol-toner", "witch hazel", 1),
    ("neutrogena-oil-free-acne-wash", "sodium laureth sulfate", 1),
    ("neutrogena-oil-free-acne-wash", "parfum", 1),
    ("neutrogena-oil-free-acne-wash", "salicylic acid", 1),
    ("neutrogena-oil-free-acne-wash", "menthol", 1),
    ("neutrogena-oil-free-acne-wash", "water", 0),
    ("retinol-serum", "retinol", 1),
    ("retinol-serum", "squalane", 0),
    ("retinol-serum", "glycerin", 0),
    ("paulas-choice-bha", "salicylic acid", 1),
    ("paulas-choice-bha", "water", 0),
    ("cerave-moisturizing-cream", "ceramide np", 0),
    ("cerave-moisturizing-cream", "glycerin", 0),
    ("cerave-moisturizing-cream", "petrolatum", 0),
    ("vanicream-moisturizing-cream", "petrolatum", 0),
    ("ordinary-niacinamide", "niacinamide", 0),
    ("ordinary-niacinamide", "zinc pca", 0),
    ("messy-dupe-lotion", "parfum", 1),
    ("messy-dupe-lotion", "benzyl salicylate", 1),
    ("messy-dupe-lotion", "citronellol", 1),
    ("messy-dupe-lotion", "hexyl cinnamal", 1),
    ("messy-dupe-lotion", "limonene", 1),
    ("messy-dupe-lotion", "linalool", 1),
    ("messy-dupe-lotion", "amyl cinnamal", 1),
    ("messy-dupe-lotion", "isopropyl myristate", 1),
    ("messy-dupe-lotion", "avena sativa straw extract", 1),
    ("messy-dupe-lotion", "glycine soja oil", 1),
    ("messy-dupe-lotion", "glycerin", 0),
]
