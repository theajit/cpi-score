from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()


def _store():
    from app.main import cpi_store
    return cpi_store


@router.get("/")
def root():
    return {
        "name": "CPI Score API",
        "version": "1.0.0",
        "status": "active",
        "description": "Public API providing country and regional corruption perception scores based on Transparency International CPI 2025 dataset.",
        "source": {
            "organization": "Transparency International",
            "dataset": "Corruption Perceptions Index 2025",
            "coverage": len(_store()["data"]),
        },
        "base_url": "/",
        "routes": {
            "countries": {
            "endpoint": "/countries",
            "method": "GET",
            "description": "Retrieve corruption scores for all countries.",
            "filters": {
                "region": "Filter countries by region name",
                "min_score": "Return countries with score greater than or equal to value",
                "max_score": "Return countries with score less than or equal to value"
            },
            "example": "/countries?region=Asia-Pacific&min_score=50"
            },
            "country_lookup": {
            "endpoint": "/countries/{code}",
            "method": "GET",
            "description": "Retrieve CPI data for a specific country using ISO2 or ISO3 code.",
            "example": "/countries/IND"
            },
            "regions": {
            "endpoint": "/regions",
            "method": "GET",
            "description": "Retrieve CPI score summaries grouped by regions."
            },
            "region_lookup": {
            "endpoint": "/regions/{region}",
            "method": "GET",
            "description": "Retrieve CPI data for all countries within a region.",
            "example": "/regions/Europe"
            },
            "rankings": {
            "endpoint": "/rankings",
            "method": "GET",
            "description": "Retrieve global CPI rankings.",
            "filters": {
                "order": "Sort order: asc or desc",
                "limit": "Number of records to return"
            },
            "example": "/rankings?order=desc&limit=10"
            },
            "health": {
            "endpoint": "/health",
            "method": "GET",
            "description": "Check API availability and service health."
            }
        },
        "meta": {
            "default_format": "application/json",
            "authentication": "Not required (public dataset)",
            "rate_limit": "Standard public usage limits apply",
            "last_updated": "2025 CPI Release"
        }
    }



@router.get("/health")
def health():
    return {"status": "ok", "countries_loaded": len(_store()["data"])}


@router.get("/countries")
def list_countries(
    region: Optional[str] = Query(None, description="Filter: AP, SSA, MENA, AME, ECA, WE/EU"),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
):
    results = _store()["data"]
    if region:
        results = [c for c in results if c["region"].upper() == region.upper()]
    if min_score is not None:
        results = [c for c in results if c["cpi_score"] >= min_score]
    if max_score is not None:
        results = [c for c in results if c["cpi_score"] <= max_score]
    return {"count": len(results), "data": results}


@router.get("/countries/{code}")
def get_country(code: str):
    store = _store()
    up = code.upper()
    country = store["by_iso2"].get(up) or store["by_iso3"].get(up)
    if not country:
        raise HTTPException(404, detail=f"Country not found: {code}")
    return country


@router.get("/regions")
def list_regions():
    regions = {}
    for c in _store()["data"]:
        r = c["region"]
        if r not in regions:
            regions[r] = {"count": 0, "total": 0}
        regions[r]["count"] += 1
        regions[r]["total"] += c["cpi_score"]
    return {
        r: {"count": v["count"], "avg_score": round(v["total"] / v["count"], 1)}
        for r, v in regions.items()
    }


@router.get("/regions/{region}")
def get_region(region: str):
    results = [c for c in _store()["data"] if c["region"].upper() == region.upper()]
    if not results:
        raise HTTPException(404, detail=f"Region not found: {region}")
    results.sort(key=lambda x: x["cpi_score"], reverse=True)
    avg = round(sum(c["cpi_score"] for c in results) / len(results), 1)
    return {"region": region.upper(), "count": len(results), "avg_score": avg, "data": results}


@router.get("/rankings")
def rankings(
    order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: Optional[int] = Query(None, ge=1, le=180),
):
    ranked = sorted(_store()["data"], key=lambda x: x["cpi_score"], reverse=(order == "desc"))
    ranked = [{**c, "rank": i + 1} for i, c in enumerate(ranked)]
    if limit:
        ranked = ranked[:limit]
    return {"count": len(ranked), "order": order, "data": ranked}
