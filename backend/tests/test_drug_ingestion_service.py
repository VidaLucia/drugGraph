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
        relationship_type="ingredient_of",
        target_synonym=None,
    )

    target_drug = DrugConcept(
        rxcui="67890",
        name="Metoprolol Tartrate",
        term_type="PIN",
        synonym=None,
    )

    rxnorm_service.search_drug.return_value = source_drug

    # IN relationships:
    # 1. has_tradename
    # 2. has_form
    # 3. ingredient_of
    #
    # Only ingredient_of returns a relationship for this test.
    rxnorm_service.get_related_by_relationship.side_effect = [
        [],
        [],
        [relationship],
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
            call("12345", "ingredient_of"),
            call("12345", "has_tradename"),
            call("12345", "has_form"),
        ]
    )

    assert (
        rxnorm_service.get_related_by_relationship.await_count
        == 3
    )

    # Source drug should be stored.
    drug_repository.upsert_drug.assert_any_await(
        source_drug
    )

    # Target drug discovered through the relationship
    # should also be stored.
    drug_repository.upsert_drug.assert_any_await(
        target_drug
    )

    assert drug_repository.upsert_drug.await_count == 2

    # Relationship should be stored.
    drug_repository.add_relationship.assert_awaited_once_with(
        relationship
    )

    # Transaction should be committed once.
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

    # If the root drug doesn't exist, nothing else
    # should happen.
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

    # All three IN relationship queries return nothing.
    rxnorm_service.get_related_by_relationship.side_effect = [
        [],
        [],
        [],
    ]

    service = DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=drug_repository,
    )

    result = await service.ingest_drug("metoprolol")

    assert result == source_drug

    # Root drug should still be stored even if
    # no relationships are found.
    drug_repository.upsert_drug.assert_awaited_once_with(
        source_drug
    )

    rxnorm_service.get_related_by_relationship.assert_has_awaits(
        [
            call("12345", "ingredient_of"),
            call("12345", "has_tradename"),
            call("12345", "has_form"),
        ]
    )

    assert (
        rxnorm_service.get_related_by_relationship.await_count
        == 3
    )

    # No relationships were returned, so none should
    # have been stored.
    drug_repository.add_relationship.assert_not_awaited()

    drug_repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingest_scd_uses_scd_relationships():
    rxnorm_service = AsyncMock()
    drug_repository = AsyncMock()

    source_drug = DrugConcept(
        rxcui="99999",
        name="Example Clinical Drug",
        term_type="SCD",
        synonym=None,
    )

    rxnorm_service.search_drug.return_value = source_drug

    # SCD currently has four configured relationship types.
    rxnorm_service.get_related_by_relationship.side_effect = [
        [],
        [],
        [],
    ]

    service = DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=drug_repository,
    )

    result = await service.ingest_drug(
        "Example Clinical Drug"
    )

    assert result == source_drug

    rxnorm_service.search_drug.assert_awaited_once_with(
        "Example Clinical Drug"
    )

    rxnorm_service.get_related_by_relationship.assert_has_awaits(
    [
        call("99999", "has_ingredient"),
        call("99999", "has_dose_form"),
        call("99999", "has_tradename"),
    ]
)

    assert (
        rxnorm_service.get_related_by_relationship.await_count
        == 3
    )

    drug_repository.upsert_drug.assert_awaited_once_with(
        source_drug
    )

    drug_repository.add_relationship.assert_not_awaited()

    drug_repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingest_unknown_tty_skips_relationships():
    rxnorm_service = AsyncMock()
    drug_repository = AsyncMock()

    source_drug = DrugConcept(
        rxcui="77777",
        name="Unknown Concept",
        term_type="XYZ",
        synonym=None,
    )

    rxnorm_service.search_drug.return_value = source_drug

    service = DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=drug_repository,
    )

    result = await service.ingest_drug(
        "Unknown Concept"
    )

    assert result == source_drug

    rxnorm_service.search_drug.assert_awaited_once_with(
        "Unknown Concept"
    )

    # XYZ isn't in RELATIONSHIPS_BY_TERM_TYPE,
    # so RxNorm relationship lookup should never run.
    rxnorm_service.get_related_by_relationship.assert_not_awaited()

    # The root concept itself should still be persisted.
    drug_repository.upsert_drug.assert_awaited_once_with(
        source_drug
    )

    drug_repository.add_relationship.assert_not_awaited()

    drug_repository.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_expand_drug_success():
    rxnorm_service = AsyncMock()
    drug_repository = AsyncMock()

    entity = AsyncMock()
    entity.rxcui = "12345"
    entity.name = "Metoprolol"
    entity.entity_type = "IN"
    entity.synonym = None

    drug_repository.get_by_rxcui.return_value = entity

    rxnorm_service.get_related_by_relationship.side_effect = [
        [],
        [],
        [],
    ]

    service = DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=drug_repository,
    )

    result = await service.expand_drug("12345")

    assert result == DrugConcept(
        rxcui="12345",
        name="Metoprolol",
        term_type="IN",
        synonym=None,
    )

    drug_repository.get_by_rxcui.assert_awaited_once_with(
        "12345"
    )

    # We should NOT search RxNorm by name during expansion.
    rxnorm_service.search_drug.assert_not_awaited()

    rxnorm_service.get_related_by_relationship.assert_has_awaits(
        [
            call("12345", "ingredient_of"),
            call("12345", "has_tradename"),
            call("12345", "has_form"),
        ]
    )

    drug_repository.commit.assert_awaited_once()
    
@pytest.mark.asyncio
async def test_expand_drug_returns_none_when_not_found():
    rxnorm_service = AsyncMock()
    drug_repository = AsyncMock()

    drug_repository.get_by_rxcui.return_value = None

    service = DrugIngestionService(
        rxnorm_service=rxnorm_service,
        drug_repository=drug_repository,
    )

    result = await service.expand_drug(
        "DOES_NOT_EXIST"
    )

    assert result is None

    drug_repository.get_by_rxcui.assert_awaited_once_with(
        "DOES_NOT_EXIST"
    )

    rxnorm_service.get_related_by_relationship.assert_not_awaited()
    drug_repository.commit.assert_not_awaited()