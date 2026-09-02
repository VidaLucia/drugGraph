from app.schema.drug import DrugConcept
from app.repositories.drug_repository import DrugRepository
from app.services.rxnorm_service import RxNormService


class DrugIngestionService:

    RELATIONSHIPS_BY_TERM_TYPE = {
    "IN": [
        "ingredient_of",
        "has_tradename",
        "has_form",
    ],

    "PIN": [
        "form_of",
        "precise_ingredient_of",
    ],

    "SCD": [
        "has_ingredient",
        "has_dose_form",
        "has_tradename",
    ],

    "SBD": [
        "tradename_of",
        "has_ingredient",
        "has_dose_form",
    ],

    "SCDG": [
        "has_ingredient",
        "has_tradename",
        "inverse_isa",
        "has_doseformgroup",
        "has_form",
    ]
}

    def __init__(self,rxnorm_service: RxNormService,drug_repository: DrugRepository):
        self.rxnorm_service = rxnorm_service
        self.drug_repository = drug_repository

    async def ingest_relationships(self,drug: DrugConcept) -> None:
        relationship_types = self.RELATIONSHIPS_BY_TERM_TYPE.get(drug.term_type,[])
        for relationship_type in relationship_types:
            relationships = await self.rxnorm_service.get_related_by_relationship(drug.rxcui,relationship_type,)
            for relationship in relationships:
                target_drug = DrugConcept(
                    rxcui=relationship.target_rxcui,
                    name=relationship.target_name,
                    term_type=relationship.target_term_type,
                    synonym=relationship.target_synonym,
                )
                await self.drug_repository.upsert_drug(target_drug)
                await self.drug_repository.add_relationship(relationship)

    async def ingest_drug(self,name: str) -> DrugConcept | None:
        drug = await self.rxnorm_service.search_drug(name)

        if drug is None:
            return None
        await self.drug_repository.upsert_drug(drug)
        await self.ingest_relationships(drug)
        await self.drug_repository.commit()

        return drug
    
    async def expand_drug(self,rxcui:str) -> DrugConcept |None:
        entity = await self.drug_repository.get_by_rxcui(rxcui)
        if entity is None:
            return None
        drug = DrugConcept(
            rxcui=entity.rxcui,
            name=entity.name,
            term_type=entity.entity_type,
            synonym=entity.synonym,
        )
        await self.ingest_relationships(drug)
        await self.drug_repository.commit()

        return drug