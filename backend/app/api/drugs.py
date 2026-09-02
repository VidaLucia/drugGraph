from fastapi import APIRouter, HTTPException, Depends
from app.schema.drug import (
    DrugConcept, 
    RelatedDrugConcept, 
    DrugRelationship,
    )
from app.dependencies import get_drug_ingestion_service
from app.services.rxnorm_service import RxNormService
from app.dependencies import get_drug_ingestion_service
from app.services.drug_ingestion_service import DrugIngestionService
from app.schema.drug import DrugGraph
from app.services.drug_graph_service import DrugGraphService
from app.dependencies import get_drug_graph_service
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

@router.get("/{rxcui}/related",response_model = list[RelatedDrugConcept])
async def get_related_drug(rxcui:str):
    try:
        return await rxnorm_service.get_related_concepts(rxcui)
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
from fastapi import Query


@router.get(
    "/{rxcui}/relationships",
    response_model=list[DrugRelationship],
)
async def get_drug_relationships(
    rxcui: str,
    rela: list[str] = Query(...),
):
    try:
        return await rxnorm_service.get_related_by_relationship(
            rxcui,
            rela,
        )

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
    
@router.post("/ingest",response_model=DrugConcept)
async def ingest_drug(name: str,
    ingestion_service: DrugIngestionService = Depends(
        get_drug_ingestion_service
    ),
):
    try:
        drug = await ingestion_service.ingest_drug(name)

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
            detail=f"No drug found for '{name}'.",
        )

    return drug

@router.get("/{rxcui}/graph",response_model=DrugGraph)
async def get_drug_graph(
    rxcui: str,
    graph_service: DrugGraphService = Depends(
        get_drug_graph_service
    ),
):
    graph = await graph_service.get_graph(rxcui)

    if graph is None:
        raise HTTPException(
            status_code=404,
            detail=f"Drug with RxCUI '{rxcui}' not found.",
        )

    return graph

@router.post("/{rxcui}/expand",response_model = DrugConcept)
async def expand_drug(
    rxcui: str,
    ingestion_service: DrugIngestionService = Depends(get_drug_ingestion_service)
):
    try:
        drug = await ingestion_service.expand_drug(rxcui)

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
            detail=f"Drug with RxCUI '{rxcui}' not found.",
        )

    return drug