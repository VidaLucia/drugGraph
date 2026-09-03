import httpx
import pytest

from unittest.mock import AsyncMock, Mock
from app.services.rxclass_service import RxClassService


@pytest.mark.asyncio
async def test_get_classes_by_rxcui():
    mock_client = AsyncMock(spec=httpx.AsyncClient)

    mock_response = Mock()

    mock_response.json.return_value = {
        "rxclassDrugInfoList": {
            "rxclassDrugInfo": [
                {
                    "minConcept": {
                        "rxcui": "6918",
                        "name": "metoprolol",
                        "tty": "IN",
                    },
                    "rxclassMinConceptItem": {
                        "classId": "N0000175503",
                        "className": "Beta adrenergic receptor blocking activity",
                        "classType": "MOA",
                    },
                    "rela": "has_MoA",
                    "relaSource": "MED-RT",
                }
            ]
        }
    }

    mock_client.get.return_value = mock_response

    service = RxClassService(mock_client)

    results = await service.get_classes_by_rxcui("6918")

    assert len(results) == 1

    result = results[0]

    assert result.source_rxcui == "6918"
    assert result.class_id == "N0000175503"
    assert result.class_name == "Beta adrenergic receptor blocking activity"
    assert result.class_type == "MOA"
    assert result.relationship_type == "has_MoA"
    assert result.relationship_source == "MED-RT"

    mock_client.get.assert_awaited_once_with(
        "/class/byRxcui.json",
        params={
            "rxcui": "6918",
        },
    )

@pytest.mark.asyncio
async def test_get_classes_by_rxcui_filters_unwanted_results():
    mock_client = AsyncMock(spec=httpx.AsyncClient)

    mock_response = Mock()

    mock_response.json.return_value = {
        "rxclassDrugInfoList": {
            "rxclassDrugInfo": [
                {
                    "minConcept": {
                        "rxcui": "6918",
                        "name": "metoprolol",
                        "tty": "IN",
                    },
                    "rxclassMinConceptItem": {
                        "classId": "N0000009923",
                        "className": "Adrenergic beta1-Antagonists",
                        "classType": "MOA",
                    },
                    "rela": "has_moa",
                    "relaSource": "MEDRT",
                },
                {
                    "minConcept": {
                        "rxcui": "6918",
                        "name": "metoprolol",
                        "tty": "IN",
                    },
                    "rxclassMinConceptItem": {
                        "classId": "D006973",
                        "className": "Hypertension",
                        "classType": "DISEASE",
                    },
                    "rela": "may_treat",
                    "relaSource": "MEDRT",
                },
                {
                    "minConcept": {
                        "rxcui": "866514",
                        "name": "metoprolol tartrate 50 MG Oral Tablet",
                        "tty": "SCD",
                    },
                    "rxclassMinConceptItem": {
                        "classId": "C07AB",
                        "className": "Beta blocking agents, selective",
                        "classType": "ATC1-4",
                    },
                    "rela": "",
                    "relaSource": "ATCPROD",
                },
            ]
        }
    }

    mock_client.get.return_value = mock_response

    service = RxClassService(mock_client)

    results = await service.get_classes_by_rxcui("6918")

    assert len(results) == 1

    result = results[0]

    assert result.class_id == "N0000009923"
    assert result.class_type == "MOA"
    assert result.source_rxcui == "6918"