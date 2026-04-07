import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from report.researcher import research_recommendations

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["recommendations"])


class ResearchRequest(BaseModel):
    bgp_document: dict[str, Any]
    route_result: dict[str, Any]


@router.post("/recommendations/research")
async def research_next_steps(req: ResearchRequest):
    """
    Enrich high-priority BGP recommendations with web-searched guidance,
    official form links, and timeline information.
    """
    logger.info("Recommendation research request received")
    try:
        recommendations = req.bgp_document.get("recommendations", [])
        if not recommendations:
            return {"recommendations": []}

        sections = req.bgp_document.get("sections", {})
        dev_details = sections.get("development_details", {})
        bbox = dev_details.get("coordinates", {}).get("bbox_wgs84", [])

        # Build location hint from bbox midpoint
        location_hint = None
        if len(bbox) == 4:
            mid_lat = (bbox[1] + bbox[3]) / 2
            mid_lng = (bbox[0] + bbox[2]) / 2
            lng_dir = "E" if mid_lng >= 0 else "W"
            location_hint = f"{mid_lat:.3f}°N, {abs(mid_lng):.3f}°{lng_dir}"

        context = {
            "developer": {
                "lpa": sections.get("development_details", {}).get("lpa", ""),
            },
            "location_hint": location_hint,
            "notes": sections.get("notes", ""),
        }

        enriched = await research_recommendations(recommendations, context)
        logger.info(
            "Research complete: %d recs, %d enriched",
            len(enriched),
            sum(1 for r in enriched if r.get("researched")),
        )
        return {"recommendations": enriched}

    except Exception as e:
        logger.exception("Recommendation research failed")
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")
