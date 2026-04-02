"""
Fills the BNG PDF template with computed field values using pypdf.
"""
import io
import logging
import os

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject

logger = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "Biodiversity_gain_plan.pdf")
# Normalise path
TEMPLATE_PATH = os.path.normpath(TEMPLATE_PATH)

# Fields to skip entirely (signatures, unknown-type parent groups)
SKIP_FIELDS = {"signature", "signature3.7", "signature3", "date3", "4", "7"}


def fill_pdf(field_values: dict) -> bytes:
    """
    Write field_values into the BNG template PDF.
    Returns filled PDF as bytes.
    """
    reader = PdfReader(TEMPLATE_PATH)
    writer = PdfWriter()
    writer.append(reader)

    known_fields = set(reader.get_fields().keys()) if reader.get_fields() else set()
    # Filter to only fields that exist in the PDF and are not skipped
    filtered = {k: v for k, v in field_values.items()
                if k in known_fields and k not in SKIP_FIELDS}

    # Text fields: use update_page_form_field_values per page
    text_fields = {k: v for k, v in filtered.items()
                   if not (v.startswith("/") and len(v) <= 6)}

    for page in writer.pages:
        writer.update_page_form_field_values(page, text_fields)

    # Checkbox/radio fields: set /V and /AS directly on annotation objects
    btn_fields = {k: v for k, v in filtered.items()
                  if v.startswith("/") and len(v) <= 6}

    if btn_fields:
        for page in writer.pages:
            if "/Annots" not in page:
                continue
            for annot_ref in page["/Annots"]:
                annot = annot_ref.get_object()
                field_name = annot.get("/T")
                if field_name and str(field_name) in btn_fields:
                    val = NameObject(btn_fields[str(field_name)])
                    annot.update({
                        NameObject("/V"): val,
                        NameObject("/AS"): val,
                    })

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()
