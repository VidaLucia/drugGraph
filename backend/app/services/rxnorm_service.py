import httpx

from app.schema.drug import (
    DrugConcept,
    RelatedDrugConcept,
)

from app.services.exceptions import (
    RxNormUnavailableError,
    RxNormResponseError,
)


class RxNormService:

    BASE_URL = "https://rxnav.nlm.nih.gov/REST"

    DEFAULT_RELATED_TYPES = [
        "IN",
        "BN",
        "SCD",
        "SBD",
    ]

    def __init__(
        self,
        client: httpx.AsyncClient,
    ):
        self.client = client

    async def _get_json(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict:

        try:
            response = await self.client.get(
                endpoint,
                params=params,
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise RxNormUnavailableError(
                "RxNorm request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RxNormUnavailableError(
                f"RxNorm returned HTTP "
                f"{exc.response.status_code}."
            ) from exc

        except httpx.RequestError as exc:
            raise RxNormUnavailableError(
                "Could not connect to RxNorm."
            ) from exc

        try:
            return response.json()

        except ValueError as exc:
            raise RxNormResponseError(
                "RxNorm returned invalid JSON."
            ) from exc

    async def search_drug(
        self,
        name: str,
    ) -> DrugConcept | None:

        if not name or not name.strip():
            return None

        rxcui = await self.find_rxcui(
            name.strip()
        )

        if rxcui is None:
            return None

        return await self.get_concept(rxcui)

    async def find_rxcui(
        self,
        name: str,
    ) -> str | None:

        data = await self._get_json(
            "/rxcui.json",
            params={
                "name": name,
                "search": 2,
            },
        )

        ids = (
            data
            .get("idGroup", {})
            .get("rxnormId")
        )

        if not ids:
            return None

        return ids[0]

    async def get_concept(
        self,
        rxcui: str,
    ) -> DrugConcept | None:

        data = await self._get_json(
            f"/rxcui/{rxcui}/properties.json"
        )

        properties = data.get("properties")

        if not properties:
            return None

        try:
            return DrugConcept(
                rxcui=properties["rxcui"],
                name=properties["name"],
                term_type=properties["tty"],
                synonym=properties.get("synonym") or None,
            )

        except KeyError as exc:
            raise RxNormResponseError(
                f"Missing required RxNorm field: "
                f"{exc.args[0]}"
            ) from exc

    async def get_related_concepts(
        self,
        rxcui: str,
        term_types: list[str] | None = None,
    ) -> list[RelatedDrugConcept]:

        if term_types is None:
            term_types = self.DEFAULT_RELATED_TYPES

        data = await self._get_json(
            f"/rxcui/{rxcui}/related.json",
            params={
                "tty": " ".join(term_types)
            },
        )

        concept_groups = (
            data
            .get("relatedGroup", {})
            .get("conceptGroup", [])
        )

        results: list[RelatedDrugConcept] = []

        for group in concept_groups:

            concepts = group.get(
                "conceptProperties",
                [],
            )

            for concept in concepts:

                try:
                    results.append(
                        RelatedDrugConcept(
                            rxcui=concept["rxcui"],
                            name=concept["name"],
                            term_type=concept["tty"],
                            synonym=(
                                concept.get("synonym")
                                or None
                            ),
                        )
                    )

                except KeyError as exc:
                    raise RxNormResponseError(
                        f"Missing required RxNorm field: "
                        f"{exc.args[0]}"
                    ) from exc

        return results