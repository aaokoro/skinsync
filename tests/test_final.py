from skinsync.catalog import HOLDOUT_LABELS
from skinsync.evaluate_final import run_final
from skinsync.scoring import SkinProfile, profile_blind_score, score_product


def test_three_methods_match_the_paper_holdout():
    out = run_final()
    hold = out["holdout"]
    assert hold["baseline"]["n"] == 19
    assert hold["baseline"]["n_correct"] == 13
    assert hold["blind"]["n_correct"] == 12
    assert hold["fuzzy"]["n_correct"] == 18
    assert hold["fuzzy"]["accuracy"] == 0.947
    assert len(HOLDOUT_LABELS) == 19
    assert sum(1 for row in hold["rows"] if row["gold"] == 0) == 3


def test_profile_blind_rejects_retinol_for_everyone():
    raw = "Water, Glycerin, Retinol, Caprylic/Capric Triglyceride"
    blind = profile_blind_score(raw)
    assert blind["compatible"] is False
    alex = SkinProfile(
        id="alex", name="Alex", skin_type="normal", concerns=["aging"], sensitivities=[]
    )
    fuzzy = score_product(raw, alex)
    assert fuzzy["compatible"] is True
