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
    repository.get_many_by_rxcui.return_value = [
        target
    ]

    service = DrugGraphService(repository)

    graph = await service.get_graph("TEST300")

    assert graph is not None

    assert graph.root.rxcui == "TEST300"
    assert graph.root.name == "Metoprolol"

    assert len(graph.nodes) == 1
    assert graph.nodes[0].rxcui == "TEST301"

    assert len(graph.edges) == 1
    assert graph.edges[0].relationship_type == "has_ingredient"
    
