import pytest
from unittest.mock import AsyncMock

from app.repositories.drug_repository import DrugRepository
from app.schema.drug import DrugConcept, DrugRelationship
from app.services.drug_ingestion_service import DrugIngestionService


@pytest.mark.asyncio
async def test_ingest_drug_persists_drug_and_relationships(
    db_session,
):
    rxnorm_service = AsyncMock()

    source_drug = DrugConcept(
        rxcui="TEST100",
        name="Metoprolol",
        term_type="IN",
        synonym=None,
    )

    relationship = DrugRelationship(
        source_rxcui="TEST100",
        target_rxcui="TEST101",
        target_name="Metoprolol Tartrate",
        target_term_type="PIN",
        relationship_type="has_ingredient",
        target_synonym=None,
    )

    rxnorm_service.search_drug.return_value = source_drug

    rxnorm_service.get_related_by_relationship.side_effect = [
        [relationship],
        [],
    ]

    repository = DrugRepository(db_session)

    service = DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=repository,
    )

    result = await service.ingest_drug(
        "metoprolol"
    )

    assert result == source_drug

    saved_source = await repository.get_by_rxcui(
        "TEST100"
    )

    saved_target = await repository.get_by_rxcui(
        "TEST101"
    )

    assert saved_source is not None
    assert saved_source.name == "Metoprolol"

    assert saved_target is not None
    assert saved_target.name == "Metoprolol Tartrate"

    relationship_exists = await repository.relationship_exists(
        source_rxcui="TEST100",
        target_rxcui="TEST101",
        relationship_type="has_ingredient",
    )

    assert relationship_exists is True