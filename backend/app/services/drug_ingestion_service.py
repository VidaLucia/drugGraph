from app.schema.drug import DrugConcept
from app.repositories.drug_repository import DrugRepository
from app.services.rxnorm_service import RxNormService


class DrugIngestionService:
    DEFAULT_RELATIONSHIPS = [
        "has_ingredient",
        "tradename_of",
    ]

    def __init__(self,rxnorm_service: RxNormService,drug_repository: DrugRepository):
        self.rxnorm_service = rxnorm_service
        self.drug_repository = drug_repository

    async def ingest_drug(self,name: str) -> DrugConcept | None:

        drug = await self.rxnorm_service.search_drug(name)

        if drug is None:
            return None

        await self.drug_repository.upsert_drug(drug)

        for relationship_type in self.DEFAULT_RELATIONSHIPS:

            relationships = (
                await self.rxnorm_service.get_related_by_relationship(
                    drug.rxcui,
                    relationship_type,
                )
            )
            for relationship in relationships:

                target_drug = DrugConcept(
                    rxcui=relationship.target_rxcui,
                    name=relationship.target_name,
                    term_type=relationship.target_term_type,
                    synonym=relationship.target_synonym,
                )
                await self.drug_repository.upsert_drug(target_drug)
                await self.drug_repository.add_relationship(relationship)

        await self.drug_repository.commit()

        return drug