# sqlite for the bigger catalog (OBF + the 11 I typed)
# notebook in the zip doesn't really need this, I mostly use catalog.py there

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from skinsync.catalog import CANONICAL_PRODUCTS, COMPATIBILITY_LABELS, PROFILES
from skinsync.parse import parse_ingredients
from skinsync.scoring import match_parsed

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_code TEXT,
    name TEXT NOT NULL,
    brand TEXT,
    category TEXT,
    ingredients_raw TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS product_ingredients (
    product_id TEXT NOT NULL,
    position INTEGER NOT NULL,
    raw_token TEXT NOT NULL,
    normalized TEXT NOT NULL,
    matched_inci TEXT,
    match_score REAL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    skin_type TEXT NOT NULL,
    concerns_json TEXT NOT NULL,
    sensitivities_json TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS compatibility_labels (
    profile_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    compatible INTEGER NOT NULL,
    rationale TEXT,
    PRIMARY KEY (profile_id, product_id)
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _slug(brand: str, name: str, code: str | None, idx: int) -> str:
    base = f"{brand}-{name}".lower()
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in base)
    cleaned = "-".join(part for part in cleaned.split("-") if part)[:60]
    suffix = code or str(idx)
    return f"{cleaned}-{suffix}"


def load_open_beauty_facts(raw_path: Path) -> list[dict]:
    products = json.loads(raw_path.read_text())
    cleaned: list[dict] = []
    seen: set[str] = set()
    for i, row in enumerate(products):
        raw = (row.get("ingredients_raw") or "").strip()
        name = (row.get("name") or "").strip()
        if not name or len(raw) < 40:
            continue
        tokens = parse_ingredients(raw)
        if len(tokens) < 5:
            continue
        # some OBF rows are just packaging text / MRP, skip those
        if "mrp" in raw.lower() and "glycerin" not in raw.lower():
            continue
        pid = _slug(row.get("brand") or "unknown", name, row.get("code"), i)
        if pid in seen:
            continue
        seen.add(pid)
        cleaned.append(
            {
                "id": pid,
                "source": "open_beauty_facts",
                "source_code": row.get("code"),
                "name": name[:140],
                "brand": (row.get("brand") or "Unknown")[:80],
                "category": (row.get("query") or row.get("categories") or "")[:80],
                "ingredients_raw": raw,
            }
        )
    return cleaned


def rebuild(db_path: Path, raw_path: Path) -> dict:
    if db_path.exists():
        db_path.unlink()
    conn = connect(db_path)
    obf = load_open_beauty_facts(raw_path)
    all_products = list(CANONICAL_PRODUCTS) + obf

    conn.executemany(
        """
        INSERT INTO products (id, source, source_code, name, brand, category, ingredients_raw)
        VALUES (:id, :source, :source_code, :name, :brand, :category, :ingredients_raw)
        """,
        [
            {
                "id": p["id"],
                "source": p["source"],
                "source_code": p.get("source_code"),
                "name": p["name"],
                "brand": p.get("brand"),
                "category": p.get("category"),
                "ingredients_raw": p["ingredients_raw"],
            }
            for p in all_products
        ],
    )

    ingredient_rows = []
    parse_counts = []
    for p in all_products:
        tokens = parse_ingredients(p["ingredients_raw"])
        parse_counts.append(len(tokens))
        for pos, token in enumerate(tokens):
            rec, score = match_parsed(token)
            ingredient_rows.append(
                (
                    p["id"],
                    pos,
                    token.raw,
                    token.normalized,
                    rec.inci if rec else None,
                    score if rec else None,
                )
            )
    conn.executemany(
        """
        INSERT INTO product_ingredients
        (product_id, position, raw_token, normalized, matched_inci, match_score)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ingredient_rows,
    )

    conn.executemany(
        """
        INSERT INTO profiles (id, display_name, skin_type, concerns_json, sensitivities_json, notes)
        VALUES (:id, :name, :skin_type, :concerns, :sensitivities, :notes)
        """,
        [
            {
                "id": p["id"],
                "name": p["name"],
                "skin_type": p["skin_type"],
                "concerns": json.dumps(p["concerns"]),
                "sensitivities": json.dumps(p["sensitivities"]),
                "notes": p["notes"],
            }
            for p in PROFILES
        ],
    )
    conn.executemany(
        """
        INSERT INTO compatibility_labels (profile_id, product_id, compatible, rationale)
        VALUES (?, ?, ?, ?)
        """,
        COMPATIBILITY_LABELS,
    )
    conn.commit()
    stats = {
        "products": len(all_products),
        "open_beauty_facts": len(obf),
        "canonical": len(CANONICAL_PRODUCTS),
        "ingredient_rows": len(ingredient_rows),
        "profiles": len(PROFILES),
        "labels": len(COMPATIBILITY_LABELS),
        "mean_ingredients": round(sum(parse_counts) / max(len(parse_counts), 1), 1),
        "lexicon_matched_rows": sum(1 for r in ingredient_rows if r[4]),
    }
    conn.close()
    return stats


def fetch_products(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT id, source, name, brand, category, ingredients_raw FROM products ORDER BY brand, name"
    ).fetchall()
    return [dict(r) for r in rows]


def fetch_product(conn: sqlite3.Connection, product_id: str) -> dict | None:
    row = conn.execute(
        "SELECT id, source, name, brand, category, ingredients_raw FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    return dict(row) if row else None


def fetch_profiles(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT id, display_name, skin_type, concerns_json, sensitivities_json, notes FROM profiles"
    ).fetchall()
    out = []
    for r in rows:
        out.append(
            {
                "id": r["id"],
                "name": r["display_name"],
                "skin_type": r["skin_type"],
                "concerns": json.loads(r["concerns_json"]),
                "sensitivities": json.loads(r["sensitivities_json"]),
                "notes": r["notes"],
            }
        )
    return out
