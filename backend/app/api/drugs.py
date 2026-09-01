from fastapi import APIRouter, HTTPException
from app.schema.drug import DrugConcept
from app.services.rxnorm_service import RxNormService
import httpx
from app.services.exceptions import (
    RxNormUnavailableError,
    RxNormResponseError,
)
router = APIRouter(
    prefix = "/drugs",
    tags = ["drugs"],
)
client = httpx.AsyncClient(
    base_url="https://rxnav.nlm.nih.gov/REST"
)

rxnorm_service = RxNormService(client)

@router.get("/search", response_model=DrugConcept)
async def search_drug(q: str):
    try:
        drug = await rxnorm_service.search_drug(q)

    except RxNormUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="Drug data service is temporarily unavailable.",
        )

    except RxNormResponseError:
        raise HTTPException(
            status_code=502,
            detail="Received an invalid response from the drug data service.",
        )

    if drug is None:
        raise HTTPException(
            status_code=404,
            detail=f"No drug found for '{q}'.",
        )
    return drug