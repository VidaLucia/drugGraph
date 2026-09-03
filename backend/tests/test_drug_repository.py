import pytest

from app.repositories.drug_repository import DrugRepository
from app.schema.drug import DrugConcept, DrugRelationship
from app.schema.drug_class import DrugClassRelationship

@pytest.mark.asyncio
async def test_upsert_drug_creates_new_drug(db_session):
    repository = DrugRepository(db_session)

    drug = DrugConcept(
        rxcui="TEST001",
        name="Metoprolol",
        term_type="IN",
        synonym=None,
    )

    await repository.upsert_drug(drug)
    await repository.commit()

    saved = await repository.get_by_rxcui("TEST001")

    assert saved is not None
    assert saved.rxcui == "TEST001"
    assert saved.name == "Metoprolol"
    assert saved.entity_type == "IN"
    assert saved.synonym is None


@pytest.mark.asyncio
async def test_upsert_drug_updates_existing_drug(db_session):
    repository = DrugRepository(db_session)

    original = DrugConcept(
        rxcui="TEST002",
        name="Original Name",
        term_type="IN",
        synonym=None,
    )

    await repository.upsert_drug(original)
    await repository.commit()

    updated = DrugConcept(
        rxcui="TEST002",
        name="Updated Name",
        term_type="PIN",
        synonym="Updated Synonym",
    )

    await repository.upsert_drug(updated)
    await repository.commit()

    saved = await repository.get_by_rxcui("TEST002")

    assert saved is not None
    assert saved.name == "Updated Name"
    assert saved.entity_type == "PIN"
    assert saved.synonym == "Updated Synonym"


@pytest.mark.asyncio
async def test_add_relationship_prevents_duplicate(db_session):
    repository = DrugRepository(db_session)

    source = DrugConcept(
        rxcui="TEST003",
        name="Source Drug",
        term_type="IN",
        synonym=None,
    )

    target = DrugConcept(
        rxcui="TEST004",
        name="Target Drug",
        term_type="PIN",
        synonym=None,
    )

    await repository.upsert_drug(source)
    await repository.upsert_drug(target)

    relationship = DrugRelationship(
        source_rxcui="TEST003",
        target_rxcui="TEST004",
        target_name="Target Drug",
        target_term_type="PIN",
        relationship_type="has_ingredient",
        target_synonym=None,
    )

    first = await repository.add_relationship(relationship)

    await repository.commit()

    second = await repository.add_relationship(relationship)

    assert first is not None
    assert second is None
    
@pytest.mark.asyncio
async def test_get_relationships(db_session):
    repository = DrugRepository(db_session)

    source = DrugConcept(
        rxcui="TEST200",
        name="Source Drug",
        term_type="IN",
        synonym=None,
    )

    target = DrugConcept(
        rxcui="TEST201",
        name="Target Drug",
        term_type="PIN",
        synonym=None,
    )

    await repository.upsert_drug(source)
    await repository.upsert_drug(target)

    relationship = DrugRelationship(
        source_rxcui="TEST200",
        target_rxcui="TEST201",
        target_name="Target Drug",
        target_term_type="PIN",
        relationship_type="has_ingredient",
        target_synonym=None,
    )

    await repository.add_relationship(relationship)
    await repository.commit()

    relationships = await repository.get_relationships(
        "TEST200"
    )

    assert len(relationships) == 1

    assert relationships[0].source_rxcui == "TEST200"
    assert relationships[0].target_rxcui == "TEST201"
    assert relationships[0].relationship_type == "has_ingredient"
    
@pytest.mark.asyncio
async def test_upsert_drug_class_creates_new_class(db_session):
    repository = DrugRepository(db_session)

    drug_class = DrugClassRelationship(
        source_rxcui="TEST300",
        class_id="CLASS001",
        class_name="Beta Blockers",
        class_type="MOA",
        relationship_type="has_moa",
        relationship_source="MEDRT",
    )

    await repository.upsert_drug_class(drug_class)
    await repository.commit()

    saved = await repository.get_class_by_id("CLASS001")

    assert saved is not None
    assert saved.class_id == "CLASS001"
    assert saved.name == "Beta Blockers"
    assert saved.class_type == "MOA"
    assert saved.source == "MEDRT"


@pytest.mark.asyncio
async def test_add_class_relationship_prevents_duplicate(db_session):
    repository = DrugRepository(db_session)

    drug = DrugConcept(
        rxcui="TEST301",
        name="Metoprolol",
        term_type="IN",
        synonym=None,
    )

    drug_class = DrugClassRelationship(
        source_rxcui="TEST301",
        class_id="CLASS002",
        class_name="Adrenergic beta1-Antagonists",
        class_type="MOA",
        relationship_type="has_moa",
        relationship_source="MEDRT",
    )

    await repository.upsert_drug(drug)
    await repository.upsert_drug_class(drug_class)

    first = await repository.add_class_relationship(
        drug_class
    )

    await repository.commit()

    second = await repository.add_class_relationship(
        drug_class
    )

    assert first is not None
    assert second is None