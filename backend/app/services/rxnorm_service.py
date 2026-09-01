# RXNorm service
import httpx
from app.schema.drug import DrugConcept
from app.services.exceptions import (
    RxNormUnavailableError,
    RxNormResponseError,
)

# https://lhncbc.nlm.nih.gov/MOR/RxTerms/
# https://www.nlm.nih.gov/research/umls/rxnorm/docs/techdoc.html
# https://www.nlm.nih.gov/research/umls/rxnorm/docs/appendix5.html
class RxNormService:
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
    async def get_json(self,endpoint: str,params: dict | None = None,) -> dict:

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
                f"RxNorm returned HTTP {exc.response.status_code}."
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
            
    async def search_drug(self, name: str) -> DrugConcept | None:
        rxcui = await self.find_rxcui(name)
        if rxcui is None:
            return None
        return await self.get_concept(rxcui)
    
    async def find_rxcui(self, name:str) -> str | None:
        data = await self.get_json("/rxcui.json",params={"name": name,"search": 2,},)
        ids = data.get("idGroup", {}).get("rxnormId")

        if not ids:
            return None

        return ids[0]
    async def get_concept(self,rxcui: str,) -> DrugConcept | None:

        data = await self.get_json(f"/rxcui/{rxcui}/properties.json")
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
                f"Missing required RxNorm field: {exc.args[0]}"
            ) from exc
    async def close(self):
        await self.client.aclose()
        