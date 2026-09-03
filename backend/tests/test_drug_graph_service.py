import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.drug_graph_service import DrugGraphService


@pytest.mark.asyncio
async def test_get_graph_success():
    repository = AsyncMock()

    root = MagicMock()
    root.rxcui = "TEST300"
    root.name = "Metoprolol"
    root.entity_type = "IN"
    root.synonym = None

    target = MagicMock()
    target.rxcui = "TEST301"
    target.name = "Metoprolol Tartrate"
    target.entity_type = "PIN"
    target.synonym = None

    relationship = MagicMock()
    relationship.source_rxcui = "TEST300"
    relationship.target_rxcui = "TEST301"
    relationship.relationship_type = "has_ingredient"

    repository.get_by_rxcui.return_value = root

    repository.get_relationships.return_value = [
        relationship
    ]

    repository.get_class_relationships.return_value = []

    repository.get_many_by_rxcui.return_value = [
        target
    ]

    repository.get_many_classes_by_id.return_value = []

    service = DrugGraphService(repository)

    graph = await service.get_graph("TEST300")

    assert graph is not None

    assert graph.root.id == "TEST300"
    assert graph.root.name == "Metoprolol"
    assert graph.root.node_type == "DRUG"
    assert graph.root.subtype == "IN"
    assert graph.root.source == "RXNORM"

    assert len(graph.nodes) == 1
    assert graph.nodes[0].id == "TEST301"
    assert graph.nodes[0].name == "Metoprolol Tartrate"

    assert len(graph.edges) == 1
    assert graph.edges[0].relationship_type == "has_ingredient"

@pytest.mark.asyncio
async def test_get_graph_includes_drug_classes():
    repository = AsyncMock()

    root = MagicMock()
    root.rxcui = "6918"
    root.name = "Metoprolol"
    root.entity_type = "IN"
    root.synonym = None

    drug_class = MagicMock()
    drug_class.class_id = "N0000009923"
    drug_class.name = "Adrenergic beta1-Antagonists"
    drug_class.class_type = "MOA"

    class_relationship = MagicMock()
    class_relationship.source_rxcui = "6918"
    class_relationship.target_class_id = "N0000009923"
    class_relationship.relationship_type = "has_moa"
    class_relationship.relationship_source = "MEDRT"

    repository.get_by_rxcui.return_value = root

    # No RxNorm drug relationships for this test.
    repository.get_relationships.return_value = []
    repository.get_many_by_rxcui.return_value = []

    # One RxClass relationship.
    repository.get_class_relationships.return_value = [
        class_relationship
    ]

    repository.get_many_classes_by_id.return_value = [
        drug_class
    ]

    service = DrugGraphService(repository)

    graph = await service.get_graph("6918")

    assert graph is not None

    assert graph.root.id == "6918"
    assert graph.root.node_type == "DRUG"

    assert len(graph.nodes) == 1

    class_node = graph.nodes[0]

    assert class_node.id == "N0000009923"
    assert class_node.name == "Adrenergic beta1-Antagonists"
    assert class_node.node_type == "CLASS"
    assert class_node.subtype == "MOA"
    assert class_node.source == "RXCLASS"

    assert len(graph.edges) == 1

    class_edge = graph.edges[0]

    assert class_edge.source_id == "6918"
    assert class_edge.target_id == "N0000009923"
    assert class_edge.relationship_type == "has_moa"
    assert class_edge.relationship_source == "MEDRT"