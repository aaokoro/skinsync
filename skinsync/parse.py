# INCI parser
# the lists from Open Beauty Facts are messy so I had to do more than split(",")
# 1,2-hexanediol kept breaking things because of the comma in the name

from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz, process

# swap the comma in 1,2-diol names for a placeholder then put it back
_COMMA_IN_NAME = re.compile(r"(\d),(\d-)")
_COMMA_PLACEHOLDER = "\u2063"  # invisible-ish char, hopefully never in a real INCI list
_PERCENT = re.compile(r"\b\d+(?:\.\d+)?\s*%")
_MULTISPACE = re.compile(r"\s+")
_PREFIXES = re.compile(
    r"(?is)(?:active|inactive)\s+ingredients?\s*:\s*"
)
# some labels put (sunscreen) after the name
_FUNCTION_LABEL = re.compile(
    r"\((?:sunscreen|preservative|emollient|humectant|fragrance)\)",
    re.I,
)

# Aqua/Water is the same thing. Caprylic/Capric is NOT, don't split those.
_SYNONYM_SLASH = {
    "aqua": "water",
    "water": "aqua",
    "parfum": "fragrance",
    "fragrance": "parfum",
    "perfume": "parfum",
    "ci 77891": "titanium dioxide",
}

_TRAILING_PUNCT = re.compile(r"[\s.;:*]+$")


@dataclass(frozen=True)
class ParsedIngredient:
    raw: str
    normalized: str
    aliases: tuple[str, ...]


def split_inci(text: str) -> list[str]:
    if not text:
        return []
    text = _PREFIXES.sub("", text)
    text = _COMMA_IN_NAME.sub(rf"\1{_COMMA_PLACEHOLDER}\2", text)
    parts = []
    buf = []
    depth = 0  # for parentheses so I don't split inside them
    for ch in text:
        if ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch == "," and depth == 0:
            token = "".join(buf).replace(_COMMA_PLACEHOLDER, ",").strip()
            if token:
                parts.append(token)
            buf = []
        else:
            buf.append(ch)
    token = "".join(buf).replace(_COMMA_PLACEHOLDER, ",").strip()
    if token:
        parts.append(token)
    return parts


def _clean_token(token: str) -> str:
    token = _PERCENT.sub("", token)
    token = _FUNCTION_LABEL.sub("", token)
    token = token.replace("\n", " ")
    token = token.replace("’", "'").replace("“", '"').replace("”", '"')
    token = _MULTISPACE.sub(" ", token)
    token = _TRAILING_PUNCT.sub("", token)
    return token.strip(" -/").lower()


def _slash_aliases(name: str) -> list[str]:
    if "/" not in name:
        return [name]
    left, right = [p.strip() for p in name.split("/", 1)]
    if not left or not right:
        return [name]
    if _SYNONYM_SLASH.get(left) == right or _SYNONYM_SLASH.get(right) == left:
        return [left, right]
    # "prunus amygdalus dulcis oil / sweet almond oil" -> keep both names
    if len(right.split()) <= 4 and len(right) < 40:
        return [name, left, right]
    return [name]


def parse_ingredients(text: str) -> list[ParsedIngredient]:
    parsed = []
    seen = set()
    for raw in split_inci(text):
        cleaned = _clean_token(raw)
        if len(cleaned) < 3:
            continue
        aliases = tuple(dict.fromkeys(_slash_aliases(cleaned)))
        key = aliases[0]
        if key in seen:
            continue
        seen.add(key)
        parsed.append(ParsedIngredient(raw=raw.strip(), normalized=key, aliases=aliases))
    return parsed


def build_alias_index(canonical_to_aliases: dict[str, list[str]]) -> dict[str, str]:
    index = {}
    for canonical, aliases in canonical_to_aliases.items():
        index[canonical] = canonical
        for alias in aliases:
            index[alias.lower()] = canonical
    return index


def match_ingredient(
    token: ParsedIngredient,
    alias_index: dict[str, str],
    choices: list[str],
    cutoff: int = 94,
    allow_fuzzy: bool = True,
) -> tuple[str | None, float]:
    # try exact first, then fuzzy
    # cutoff used to be 90 and it matched sorbic acid -> ascorbic acid
    # which made Vanicream look irritating for no reason. 94 + the length check below fixed it.
    for alias in token.aliases:
        if alias in alias_index:
            return alias_index[alias], 100.0
        compact = alias.replace(" ", "")
        for key, canonical in alias_index.items():
            if key.replace(" ", "") == compact:
                return canonical, 99.0

    if not allow_fuzzy:
        return None, 0.0

    # short tokens fuzzy-match too easily
    if len(token.normalized) < 5:
        return None, 0.0

    result = process.extractOne(
        token.normalized,
        choices,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=cutoff,
    )
    if result is None:
        for alias in token.aliases[1:]:
            result = process.extractOne(
                alias,
                choices,
                scorer=fuzz.token_sort_ratio,
                score_cutoff=cutoff,
            )
            if result is not None:
                break
    if result is None:
        return None, 0.0
    match, score, _ = result
    # simethicone vs dimethicone was another near miss
    if abs(len(token.normalized) - len(match)) >= 3 and score < 96:
        return None, 0.0
    return alias_index.get(match, match), float(score)
