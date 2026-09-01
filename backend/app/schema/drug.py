from pydantic import BaseModel

class DrugConcept(BaseModel):
    rxcui: str
    name: str
    term_type: str
    synonym: str | None = None
    source: str = "RXNORM"
    
class RelatedDrugConcept(BaseModel):
    rxcui: str
    name: str
    term_type: str
    synonym: str | None = None
    source: str = "RXNORM"