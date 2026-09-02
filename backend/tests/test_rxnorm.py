import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.rxnorm_service import RxNormService
from app.services.exceptions import (
    RxNormUnavailableError,
    RxNormResponseError,
)
import httpx

@pytest.mark.asyncio
async def test_search_drug():
    client = AsyncMock()
    search_response = MagicMock()
    search_response.json.return_value = {
        "idGroup": {
            "rxnormId": ["12345"]
        }
    }
    search_response.raise_for_status.return_value = None
    
    properties_response = MagicMock()
    properties_response.json.return_value = {
        "properties": {
            "rxcui": "12345",
            "name": "Metoprolol",
            "tty": "IN",
            "synonym": ""
        }
    }
    properties_response.raise_for_status.return_value = None

    client.get.side_effect = [
        search_response,
        properties_response,
    ]

    service = RxNormService(client)

    result = await service.search_drug("metoprolol")

    assert result is not None
    assert result.rxcui == "12345"
    assert result.name == "Metoprolol"
    assert result.term_type == "IN"
    
@pytest.mark.asyncio
async def test_search_drug_returns_none_when_not_found():
    client = AsyncMock()

    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "idGroup": {}
    }

    client.get.return_value = response

    service = RxNormService(client)

    result = await service.search_drug("definitely-not-a-real-drug")

    assert result is None
    
@pytest.mark.asyncio
async def test_search_drug_timeout():
    client = AsyncMock()

    client.get.side_effect = httpx.TimeoutException(
        "timeout"
    )

    service = RxNormService(client)

    with pytest.raises(RxNormUnavailableError):
        await service.search_drug("metoprolol")
        
@pytest.mark.asyncio
async def test_search_drug_invalid_json():
    client = AsyncMock()

    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.side_effect = ValueError()

    client.get.return_value = response

    service = RxNormService(client)

    with pytest.raises(RxNormResponseError):
        await service.search_drug("metoprolol")

@pytest.mark.asyncio
async def test_get_related_concept():

    client = AsyncMock()

    response = MagicMock()
    response.raise_for_status.return_value = None

    response.json.return_value = {
        "relatedGroup": {
            "conceptGroup": [
                {
                    "tty": "BN",
                    "conceptProperties": [
                        {
                            "rxcui": "111111",
                            "name": "Example Brand",
                            "synonym": "",
                            "tty": "BN",
                        }
                    ]
                },
                {
                    "tty": "SCD",
                    "conceptProperties": [
                        {
                            "rxcui": "222222",
                            "name": "Example 50 MG Oral Tablet",
                            "synonym": "",
                            "tty": "SCD",
                        }
                    ]
                }
            ]
        }
    }

    client.get.return_value = response

    service = RxNormService(client)

    results = await service.get_related_concepts(
        "12345"
    )

    assert len(results) == 2

    assert results[0].rxcui == "111111"
    assert results[0].term_type == "BN"

    assert results[1].rxcui == "222222"
    assert results[1].term_type == "SCD"

@pytest.mark.asyncio
async def test_get_related_concepts_empty():

    client = AsyncMock()

    response = MagicMock()
    response.raise_for_status.return_value = None

    response.json.return_value = {
        "relatedGroup": {}
    }

    client.get.return_value = response

    service = RxNormService(client)

    results = await service.get_related_concepts(
        "12345"
    )

    assert results == []
    
@pytest.mark.asyncio
async def test_get_related_concepts_timeout():
    client = AsyncMock()

    client.get.side_effect = httpx.TimeoutException(
        "timeout"
    )

    service = RxNormService(client)

    with pytest.raises(RxNormUnavailableError):
        await service.get_related_concepts("12345")

@pytest.mark.asyncio
async def test_get_related_concepts_invalid_json():
    client = AsyncMock()

    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.side_effect = ValueError()

    client.get.return_value = response

    service = RxNormService(client)

    with pytest.raises(RxNormResponseError):
        await service.get_related_concepts("12345")

@pytest.mark.asyncio
async def test_get_related_by_relationship():

    client = AsyncMock()

    response = MagicMock()
    response.raise_for_status.return_value = None

    response.json.return_value = {
        "relatedGroup": {
            "conceptGroup": [
                {
                    "tty": "IN",
                    "conceptProperties": [
                        {
                            "rxcui": "111111",
                            "name": "Example Ingredient",
                            "synonym": "",
                            "tty": "IN",
                            "rela": "has_ingredient",
                        }
                    ],
                }
            ]
        }
    }

    client.get.return_value = response

    service = RxNormService(client)

    results = await service.get_related_by_relationship(
        "12345",
        "has_ingredient",
    )

    assert len(results) == 1

    relationship = results[0]

    assert relationship.source_rxcui == "12345"
    assert relationship.target_rxcui == "111111"
    assert relationship.relationship_type == "has_ingredient"

@pytest.mark.asyncio
async def test_get_json_raises_response_error_on_400():
    client = AsyncMock()

    request = httpx.Request(
        "GET",
        "https://rxnav.nlm.nih.gov/REST/test"
    )

    response = httpx.Response(
        400,
        request=request,
    )

    client.get.return_value = response

    service = RxNormService(client)

    with pytest.raises(RxNormResponseError):
        await service._get_json("/test")

@pytest.mark.asyncio
async def test_get_json_raises_unavailable_error_on_500():
    client = AsyncMock()

    request = httpx.Request(
        "GET",
        "https://rxnav.nlm.nih.gov/REST/test"
    )

    response = httpx.Response(
        500,
        request=request,
    )

    client.get.return_value = response

    service = RxNormService(client)

    with pytest.raises(RxNormUnavailableError):
        await service._get_json("/test")