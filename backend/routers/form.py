from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from bng.form_models import BNGFormInput
from bng.form_mapper import build_field_values
from bng.pdf_filler import fill_pdf

router = APIRouter(prefix="/api/form", tags=["form"])


@router.post("/pdf")
async def generate_pdf(inp: BNGFormInput):
    """
    Generate a pre-filled official BNG gain plan PDF.
    Accepts route_result + bgp_document + optional developer details.
    Returns a filled PDF as a file download.
    """
    try:
        if not inp.route_result or not inp.bgp_document:
            raise HTTPException(status_code=422, detail="route_result and bgp_document are required")

        field_values = build_field_values(inp)
        pdf_bytes = fill_pdf(field_values)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=bng_gain_plan_filled.pdf"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
