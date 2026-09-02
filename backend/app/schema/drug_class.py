from pydantic import BaseModel

class DrugClassRelationship(BaseModel):
    source_rxcui: str
    class_id: str
    class_name: str
    class_type: str
    relationship_type: str | None = None
    relationship_source: str
    source: str = "RXCLASS"