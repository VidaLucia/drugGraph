import httpx

from app.schema.drug_class import DrugClassRelationship

class RxClassService:
    BASE_URL = "https://rxnav.nlm.nih.gov/REST/rxclass"
    
    def __init__(self,client: httpx.AsyncClient):
        self.client = client
    
    async def get_classes_by_rxcui(self,rxcui: str) -> list[DrugClassRelationship]:
        ALLOWED_CLASS_TYPES = {
                "ATC1-4",
                "MOA",
                "EPC",
                "PE",
            }
        response = await self.client.get("/class/byRxcui.json",params={"rxcui": rxcui,})
        response.raise_for_status()
        data = response.json()
        class_info = (data.get("rxclassDrugInfoList", {}).get("rxclassDrugInfo", []))
        results: list[DrugClassRelationship] = []

        for item in class_info:
            min_concept = item.get("minConcept", {})
            if min_concept.get("rxcui") != rxcui:
                continue
            class_concept = item.get("rxclassMinConceptItem",{})
            if not class_concept:
                continue
            class_type = class_concept.get("classType")

            if class_type not in ALLOWED_CLASS_TYPES:
                continue

            results.append(
                DrugClassRelationship(
                    source_rxcui=rxcui,
                    class_id=class_concept["classId"],
                    class_name=class_concept["className"],
                    class_type=class_type,
                    relationship_type=item.get("rela") or None,
                    relationship_source=item["relaSource"],
                )
            )

        return results