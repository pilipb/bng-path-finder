from pydantic import BaseModel


class DeveloperDetails(BaseModel):
    applicant_name: str = ""
    company_name: str = ""
    site_address: str = ""
    lpa: str = ""
    planning_app_ref: str = ""
    development_description: str = ""
    email: str = ""
    telephone: str = ""


class BNGFormInput(BaseModel):
    route_result: dict
    bgp_document: dict
    developer: DeveloperDetails = DeveloperDetails()
