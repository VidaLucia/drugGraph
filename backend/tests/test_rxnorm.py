import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.rxnorm_service import RxNormService

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