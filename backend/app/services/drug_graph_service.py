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
        drug_relationships = await self.drug_repository.get_relationships(rxcui)
        class_relationships = await self.drug_repository.get_class_relationships(rxcui)
        target_rxcuis = [relationship.target_rxcui for relationship in drug_relationships]
        target_class_ids = [relationship.target_class_id for relationship in class_relationships]        
        target_drugs = await self.drug_repository.get_many_by_rxcui(target_rxcuis)
        target_classes = await self.drug_repository.get_many_classes_by_id(target_class_ids)
        root_node = DrugGraphNode(
            id=root.rxcui,
            name=root.name,
            node_type="DRUG",
            subtype=root.entity_type,
            synonym=root.synonym,
            source="RXNORM",
        )
        
        drug_nodes = [
            DrugGraphNode(
                id=entity.rxcui,
                name=entity.name,
                node_type="DRUG",
                subtype=entity.entity_type,
                synonym=entity.synonym,
                source="RXNORM",
            )
            for entity in target_drugs
        ]

        class_nodes = [
            DrugGraphNode(
                id=entity.class_id,
                name=entity.name,
                node_type="CLASS",
                subtype=entity.class_type,
                synonym=None,
                source="RXCLASS",
            )
            for entity in target_classes
        ]

        drug_edges = [
            DrugGraphEdge(
                source_id=relationship.source_rxcui,
                target_id=relationship.target_rxcui,
                relationship_type=relationship.relationship_type,
                relationship_source="RXNORM",
            )
            for relationship in drug_relationships
        ]

        class_edges = [
            DrugGraphEdge(
                source_id=relationship.source_rxcui,
                target_id=relationship.target_class_id,
                relationship_type=relationship.relationship_type,
                relationship_source=relationship.relationship_source,
            )
            for relationship in class_relationships
        ]

        return DrugGraph(
            root=root_node,
            nodes=[*drug_nodes,*class_nodes],
            edges=[*drug_edges,*class_edges],
        )