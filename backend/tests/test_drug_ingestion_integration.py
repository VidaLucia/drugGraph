import pytest
from unittest.mock import AsyncMock

from app.repositories.drug_repository import DrugRepository
from app.schema.drug import DrugConcept, DrugRelationship
from app.services.drug_ingestion_service import DrugIngestionService
from unittest.mock import AsyncMock, MagicMock, call

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

@pytest.mark.asyncio
async def test_expand_scdg_uses_scdg_relationships():
    rxnorm_service = AsyncMock()
    drug_repository = AsyncMock()

    entity = MagicMock()
    entity.rxcui = "1162132"
    entity.name = "hydrochlorothiazide / metoprolol Oral Product"
    entity.entity_type = "SCDG"
    entity.synonym = None

    drug_repository.get_by_rxcui.return_value = entity

    rxnorm_service.get_related_by_relationship.side_effect = [
        [],
        [],
        [],
        [],
        [],
    ]

    service = DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=drug_repository,
    )

    result = await service.expand_drug("1162132")

    assert result is not None
    assert result.rxcui == "1162132"
    assert result.term_type == "SCDG"



    rxnorm_service.get_related_by_relationship.assert_has_awaits(
        [
            call("1162132", "has_ingredient"),
            call("1162132", "has_tradename"),
            call("1162132", "inverse_isa"),
            call("1162132", "has_doseformgroup"),
            call("1162132", "has_form"),
        ]
    )

    assert (
        rxnorm_service.get_related_by_relationship.await_count
        == 5
    )
    drug_repository.commit.assert_awaited_once()