import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from report.builder import build_gain_plan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["report"])


class ReportRequest(BaseModel):
    route_result: dict[str, Any]


@router.post("/report")
async def generate_report(req: ReportRequest):
    """
    Generate a Biodiversity Gain Plan document from a route calculation result.
    """
    logger.info("Report request received")
    try:
        if not req.route_result:
            logger.warning("Report request missing route_result")
            raise HTTPException(status_code=422, detail="route_result is required")

        doc = build_gain_plan(req.route_result)
        logger.info("Report generated successfully")
        return doc

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Report generation failed")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
