from app.repositories.drug_repository import DrugRepository
from app.schema.drug import (
    DrugGraph,
    DrugGraphNode,
    DrugGraphEdge,
)

class DrugGraphService:
    def __init__(self,drug_repository: DrugRepository):
        self.drug_repository = drug_repository
        
    async def get_graph(self,rxcui:str)-> DrugGraph | None:
        root = await self.drug_repository.get_by_rxcui(rxcui)
        if root is None:
            return None
        relationships = await self.drug_repository.get_relationships(rxcui)
        target_rxcuis = [relationship.target_rxcui for relationship in relationships]        
        target_entities = await self.drug_repository.get_many_by_rxcui(target_rxcuis)

        root_node = DrugGraphNode(
            rxcui = root.rxcui,
            name = root.name,
            term_type = root.entity_type,
            synonym = root.synonym
        )
        
        nodes = [
            DrugGraphNode(
                rxcui=entity.rxcui,
                name=entity.name,
                term_type=entity.entity_type,
                synonym=entity.synonym,
            )
            for entity in target_entities
        ]
        edges = [
            DrugGraphEdge(
                source_rxcui=relationship.source_rxcui,
                target_rxcui=relationship.target_rxcui,
                relationship_type=relationship.relationship_type,
            )
            for relationship in relationships
        ]

        return DrugGraph(root=root_node,nodes=nodes,edges=edges)