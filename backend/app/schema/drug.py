from pydantic import BaseModel

class DrugConcept(BaseModel):
    rxcui: str
    name: str
    term_type: str
    synonym: str | None = None
    source: str = "RXNORM"
    
# Need up to update later
class RelatedDrugConcept(BaseModel):
    rxcui: str
    name: str
    term_type: str
    synonym: str | None = None
    source: str = "RXNORM"
    
# our graph edge
class DrugRelationship(BaseModel):
    source_rxcui:str
    target_rxcui: str
    target_name: str
    target_term_type: str
    relationship_type: str
    target_synonym: str | None = None
    source: str = "RXNORM"
    