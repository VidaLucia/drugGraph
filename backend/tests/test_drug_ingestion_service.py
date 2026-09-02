import pytest
from unittest.mock import AsyncMock, call

from app.schema.drug import DrugConcept, DrugRelationship
from app.services.drug_ingestion_service import DrugIngestionService


@pytest.mark.asyncio
async def test_ingest_drug_success():
    rxnorm_service = AsyncMock()
    drug_repository = AsyncMock()

    source_drug = DrugConcept(
        rxcui="12345",
        name="Metoprolol",
        term_type="IN",
        synonym=None,
    )

    relationship = DrugRelationship(
        source_rxcui="12345",
        target_rxcui="67890",
        target_name="Metoprolol Tartrate",
        target_term_type="PIN",
        relationship_type="has_ingredient",
        target_synonym=None,
    )

    target_drug = DrugConcept(
        rxcui="67890",
        name="Metoprolol Tartrate",
        term_type="PIN",
        synonym=None,
    )

    rxnorm_service.search_drug.return_value = source_drug

    # First call: has_ingredient
    # Second call: tradename_of
    rxnorm_service.get_related_by_relationship.side_effect = [
        [relationship],
        [],
    ]

    service = DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=drug_repository,
    )

    result = await service.ingest_drug("metoprolol")

    assert result == source_drug

    rxnorm_service.search_drug.assert_awaited_once_with(
        "metoprolol"
    )

    rxnorm_service.get_related_by_relationship.assert_has_awaits(
        [
            call("12345", "has_ingredient"),
            call("12345", "tradename_of"),
        ]
    )

    assert (
        rxnorm_service.get_related_by_relationship.await_count
        == 2
    )

    drug_repository.upsert_drug.assert_any_await(
        source_drug
    )

    drug_repository.upsert_drug.assert_any_await(
        target_drug
    )

    assert drug_repository.upsert_drug.await_count == 2

    drug_repository.add_relationship.assert_awaited_once_with(
        relationship
    )

    drug_repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingest_drug_returns_none_when_not_found():
    rxnorm_service = AsyncMock()
    drug_repository = AsyncMock()

    rxnorm_service.search_drug.return_value = None

    service = DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=drug_repository,
    )

    result = await service.ingest_drug(
        "not-a-real-drug"
    )

    assert result is None

    rxnorm_service.search_drug.assert_awaited_once_with(
        "not-a-real-drug"
    )

    rxnorm_service.get_related_by_relationship.assert_not_awaited()

    drug_repository.upsert_drug.assert_not_awaited()
    drug_repository.add_relationship.assert_not_awaited()
    drug_repository.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_ingest_drug_with_no_relationships():
    rxnorm_service = AsyncMock()
    drug_repository = AsyncMock()

    source_drug = DrugConcept(
        rxcui="12345",
        name="Metoprolol",
        term_type="IN",
        synonym=None,
    )

    rxnorm_service.search_drug.return_value = source_drug

    # Both relationship queries return nothing
    rxnorm_service.get_related_by_relationship.side_effect = [
        [],
        [],
    ]

    service = DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=drug_repository,
    )

    result = await service.ingest_drug("metoprolol")

    assert result == source_drug

    drug_repository.upsert_drug.assert_awaited_once_with(
        source_drug
    )

    rxnorm_service.get_related_by_relationship.assert_has_awaits(
        [
            call("12345", "has_ingredient"),
            call("12345", "tradename_of"),
        ]
    )

    assert (
        rxnorm_service.get_related_by_relationship.await_count
        == 2
    )

    drug_repository.add_relationship.assert_not_awaited()

    drug_repository.commit.assert_awaited_once()