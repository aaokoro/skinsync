"""FastAPI scoring service and checkpoint demo UI."""

from __future__ import annotations

import json
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from skinsync.baseline import baseline_score
from skinsync.db import connect, fetch_product, fetch_products, fetch_profiles
from skinsync.paths import DB_PATH, REPORTS_DIR, RESULTS_JSON, STATIC_DIR
from skinsync.scoring import SkinProfile, profile_blind_score, score_product

app = FastAPI(
    title="SkinSync",
    description="Personalized skincare ingredient compatibility scoring (COMP365 Checkpoint 1).",
    version="0.1.0",
)


class ProfileIn(BaseModel):
    id: str = "custom"
    name: str = "Custom"
    skin_type: str = "normal"
    concerns: list[str] = Field(default_factory=list)
    sensitivities: list[str] = Field(default_factory=list)
    notes: str = ""


class ScoreIn(BaseModel):
    product_id: str | None = None
    ingredients: str | None = None
    profile: ProfileIn
    method: str = "multi"


class RankIn(BaseModel):
    profile: ProfileIn
    method: str = "multi"
    limit: int = 12
    source: str | None = None


def _conn():
    if not DB_PATH.exists():
        raise HTTPException(
            503,
            "Catalog is not built yet. Run: python -m skinsync.prepare",
        )
    return connect(DB_PATH)


def _to_profile(p: ProfileIn | dict) -> SkinProfile:
    if isinstance(p, dict):
        return SkinProfile(
            id=p["id"],
            name=p.get("name") or p.get("display_name") or p["id"],
            skin_type=p["skin_type"],
            concerns=p.get("concerns") or [],
            sensitivities=p.get("sensitivities") or [],
            notes=p.get("notes") or "",
        )
    return SkinProfile(
        id=p.id,
        name=p.name,
        skin_type=p.skin_type,
        concerns=p.concerns,
        sensitivities=p.sensitivities,
        notes=p.notes,
    )


def _score(raw: str, profile: SkinProfile, method: str) -> dict:
    base = baseline_score(raw)
    blind = profile_blind_score(raw)
    multi = score_product(raw, profile)
    extras = {"baseline": base, "profile_blind": blind, "multi_criteria": multi}
    if method == "baseline":
        return {**base, **extras}
    if method in {"blind", "profile_blind"}:
        return {**blind, **extras}
    return {**multi, **extras}


@app.get("/api/health")
def health():
    return {"ok": True, "service": "skinsync", "checkpoint": 1}


@app.get("/api/profiles")
def profiles():
    conn = _conn()
    try:
        return fetch_profiles(conn)
    finally:
        conn.close()


@app.get("/api/products")
def products(limit: int = 40, q: str = ""):
    conn = _conn()
    try:
        rows = fetch_products(conn)
    finally:
        conn.close()
    if q:
        needle = q.lower()
        rows = [
            r
            for r in rows
            if needle in r["name"].lower()
            or needle in (r.get("brand") or "").lower()
        ]
    return rows[:limit]


@app.get("/api/products/{product_id}")
def product(product_id: str):
    conn = _conn()
    try:
        row = fetch_product(conn, product_id)
    finally:
        conn.close()
    if not row:
        raise HTTPException(404, "Unknown product")
    return row


@app.post("/api/score")
def score(body: ScoreIn):
    raw = body.ingredients
    meta = None
    if body.product_id:
        conn = _conn()
        try:
            meta = fetch_product(conn, body.product_id)
        finally:
            conn.close()
        if not meta:
            raise HTTPException(404, "Unknown product")
        raw = meta["ingredients_raw"]
    if not raw:
        raise HTTPException(400, "Provide product_id or ingredients")
    profile = _to_profile(body.profile)
    result = _score(raw, profile, body.method)
    return {"product": meta, "profile": body.profile.model_dump(), "result": result}


@app.post("/api/rank")
def rank(body: RankIn):
    conn = _conn()
    try:
        rows = fetch_products(conn)
        profiles = {p["id"]: p for p in fetch_profiles(conn)}
    finally:
        conn.close()
    profile = _to_profile(body.profile)
    if body.profile.id in profiles and body.profile.skin_type == "normal" and not body.profile.sensitivities:
        # Keep explicit posted profile; only hydrate when client sent an id-only request.
        pass
    scored = []
    for row in rows:
        if body.source and row["source"] != body.source:
            continue
        result = _score(row["ingredients_raw"], profile, body.method)
        scored.append(
            {
                "id": row["id"],
                "name": row["name"],
                "brand": row["brand"],
                "category": row["category"],
                "source": row["source"],
                "score": result["score"],
                "verdict": result["verdict"],
                "compatible": result["compatible"],
                "flags": result.get("flags") or [{"ingredient": h} for h in result.get("hits", [])],
            }
        )
    scored.sort(
        key=lambda r: (
            0 if str(r["source"]).startswith("canonical") else 1,
            -r["score"],
        )
    )
    return {
        "profile": profile.__dict__,
        "method": body.method,
        "results": scored[: max(1, min(body.limit, 40))],
        "catalog_size": len(rows),
    }


@lru_cache(maxsize=1)
def _results_payload() -> dict:
    if not RESULTS_JSON.exists():
        return {}
    return json.loads(RESULTS_JSON.read_text())


@app.get("/api/results")
def results():
    payload = _results_payload()
    if not payload:
        raise HTTPException(503, "Run python -m skinsync.prepare first")
    return payload


@app.get("/Okoro_Amaka_COMP365_Final.pdf")
def final_paper():
    path = REPORTS_DIR / "Okoro_Amaka_COMP365_Final.pdf"
    alt = REPORTS_DIR.parent / "paper" / "skinsync_southeastcon.pdf"
    if not path.exists():
        path = alt
    if not path.exists():
        raise HTTPException(404, "Final paper PDF is missing")
    return FileResponse(path, media_type="application/pdf", filename="Okoro_Amaka_COMP365_Final.pdf")


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        return {"message": "UI missing", "docs": "/docs"}
    return FileResponse(index_path)
