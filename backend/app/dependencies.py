import httpx

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.drug_repository import DrugRepository
from app.services.rxnorm_service import RxNormService
from app.services.drug_ingestion_service import DrugIngestionService


async def get_rxnorm_service():
    async with httpx.AsyncClient(
        base_url="https://rxnav.nlm.nih.gov/REST"
    ) as client:
        yield RxNormService(client)


def get_drug_repository(
    db: AsyncSession = Depends(get_db),
):
    return DrugRepository(db)


def get_drug_ingestion_service(
    rxnorm_service: RxNormService = Depends(get_rxnorm_service),
    drug_repository: DrugRepository = Depends(get_drug_repository),
):
    return DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=drug_repository,
    )