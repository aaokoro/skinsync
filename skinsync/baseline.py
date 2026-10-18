# Keyword baseline for checkpoint 1
# just searches the ingredient string for bad words. no profile, no weights.
# this is supposed to be the "dumb" version I compare against.

from __future__ import annotations

from skinsync.lexicon import BASELINE_BLACKLIST


def baseline_hits(ingredient_text: str) -> list[str]:
    blob = (ingredient_text or "").lower()
    hits = []
    for needle in BASELINE_BLACKLIST:
        if needle in blob:
            hits.append(needle)
    return hits


def baseline_score(ingredient_text: str) -> dict:
    # 100 if nothing on the list shows up, otherwise 0
    # yeah it's harsh but that's the point of a baseline
    hits = baseline_hits(ingredient_text)
    ok = len(hits) == 0
    return {
        "method": "keyword_baseline",
        "score": 100 if ok else 0,
        "compatible": ok,
        "hits": hits,
        "verdict": "compatible" if ok else "flagged",
    }
