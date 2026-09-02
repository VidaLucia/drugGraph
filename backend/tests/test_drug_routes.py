import pytest

from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from app.main import app
from app.schema.drug import (
    DrugConcept,
    DrugGraph,
    DrugGraphNode,
    DrugGraphEdge,
)
from app.dependencies import (
    get_drug_ingestion_service,
    get_drug_graph_service,
)


@pytest.mark.asyncio
async def test_ingest_drug_success():
    ingestion_service = AsyncMock()

    ingestion_service.ingest_drug.return_value = DrugConcept(
        rxcui="6918",
        name="metoprolol",
        term_type="IN",
        synonym=None,
    )

    app.dependency_overrides[
        get_drug_ingestion_service
    ] = lambda: ingestion_service

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.post(
            "/drugs/ingest",
            params={"name": "metoprolol"},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["rxcui"] == "6918"
    assert data["name"] == "metoprolol"
    assert data["term_type"] == "IN"

    ingestion_service.ingest_drug.assert_awaited_once_with(
        "metoprolol"
    )

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ingest_drug_not_found():
    ingestion_service = AsyncMock()

    ingestion_service.ingest_drug.return_value = None

    app.dependency_overrides[
        get_drug_ingestion_service
    ] = lambda: ingestion_service

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.post(
            "/drugs/ingest",
            params={"name": "not-a-real-drug"},
        )

    assert response.status_code == 404

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_drug_graph_success():
    graph_service = AsyncMock()

    graph_service.get_graph.return_value = DrugGraph(
        root=DrugGraphNode(
            rxcui="6918",
            name="metoprolol",
            term_type="IN",
            synonym=None,
        ),
        nodes=[
            DrugGraphNode(
                rxcui="1162132",
                name="hydrochlorothiazide / metoprolol Oral Product",
                term_type="SCDG",
                synonym=None,
            )
        ],
        edges=[
            DrugGraphEdge(
                source_rxcui="6918",
                target_rxcui="1162132",
                relationship_type="ingredient_of",
            )
        ],
    )

    app.dependency_overrides[
        get_drug_graph_service
    ] = lambda: graph_service

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.get(
            "/drugs/6918/graph"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["root"]["rxcui"] == "6918"
    assert len(data["nodes"]) == 1
    assert len(data["edges"]) == 1

    graph_service.get_graph.assert_awaited_once_with(
        "6918"
    )

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_drug_graph_not_found():
    graph_service = AsyncMock()

    graph_service.get_graph.return_value = None

    app.dependency_overrides[
        get_drug_graph_service
    ] = lambda: graph_service

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.get(
            "/drugs/DOES_NOT_EXIST/graph"
        )

    assert response.status_code == 404

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_expand_drug_success():
    ingestion_service = AsyncMock()

    ingestion_service.expand_drug.return_value = DrugConcept(
        rxcui="1162132",
        name="hydrochlorothiazide / metoprolol Oral Product",
        term_type="SCDG",
        synonym=None,
    )

    app.dependency_overrides[
        get_drug_ingestion_service
    ] = lambda: ingestion_service

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.post(
            "/drugs/1162132/expand"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["rxcui"] == "1162132"
    assert data["term_type"] == "SCDG"

    ingestion_service.expand_drug.assert_awaited_once_with(
        "1162132"
    )

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_expand_drug_not_found():
    ingestion_service = AsyncMock()

    ingestion_service.expand_drug.return_value = None

    app.dependency_overrides[
        get_drug_ingestion_service
    ] = lambda: ingestion_service

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.post(
            "/drugs/DOES_NOT_EXIST/expand"
        )

    assert response.status_code == 404

    app.dependency_overrides.clear()