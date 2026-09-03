from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drug_entity import (DrugEntity,DrugRelationshipEntity,DrugClassEntity,DrugClassRelationshipEntity,)
from app.schema.drug import DrugConcept, DrugRelationship
from app.schema.drug_class import DrugClassRelationship

class DrugRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_rxcui(self,rxcui:str)-> DrugEntity | None:
        result = await self.session.execute(select(DrugEntity).where(DrugEntity.rxcui == rxcui))
        return result.scalar_one_or_none()
    
    async def upsert_drug(self, drug:DrugConcept)-> DrugEntity:
        existing = await self.get_by_rxcui(drug.rxcui)
        if existing:
            existing.name = drug.name
            existing.entity_type = drug.term_type
            existing.synonym = drug.synonym
            return existing
        entity = DrugEntity(
            rxcui = drug.rxcui,
            name = drug.name,
            entity_type = drug.term_type,
            synonym = drug.synonym
        )
        self.session.add(entity)
        return entity
    
    async def relationship_exists(self,source_rxcui:str,target_rxcui:str,relationship_type:str) -> bool:
        result = await self.session.execute(select(DrugRelationshipEntity).where(
            DrugRelationshipEntity.source_rxcui == source_rxcui,
            DrugRelationshipEntity.target_rxcui == target_rxcui,
            DrugRelationshipEntity.relationship_type == relationship_type,
        ))
        
        return result.scalar_one_or_none() is not None
    
    async def add_relationship(self,relationship:DrugRelationship) ->DrugRelationshipEntity | None:
        exists = await self.relationship_exists(
            relationship.source_rxcui,
            relationship.target_rxcui,
            relationship.relationship_type
        )
        
        if exists:
            return None
        
        entity = DrugRelationshipEntity(
            source_rxcui=relationship.source_rxcui,
            target_rxcui=relationship.target_rxcui,
            relationship_type=relationship.relationship_type,
        )
        
        self.session.add(entity)
        return entity
    async def get_relationships(self,rxcui: str) -> list[DrugRelationshipEntity]:
        result = await self.session.execute(select(DrugRelationshipEntity).where(DrugRelationshipEntity.source_rxcui == rxcui))
        return list(result.scalars().all())
    async def get_class_by_id(self,class_id:str) ->DrugClassEntity | None:
        result = await self.session.execute(
            select(DrugClassEntity).where(DrugClassEntity.class_id == class_id)
        )
        return result.scalar_one_or_none()
    async def get_class_relationships(self,rxcui: str) -> list[DrugClassRelationshipEntity]:
        result = await self.session.execute(select(DrugClassRelationshipEntity).where(DrugClassRelationshipEntity.source_rxcui == rxcui))
        return list(result.scalars().all())
    async def get_many_classes_by_id(self,class_ids: list[str]) -> list[DrugClassEntity]:
        if not class_ids:
            return []
        result = await self.session.execute(select(DrugClassEntity).where(DrugClassEntity.class_id.in_(class_ids)))
        return list(result.scalars().all())
    async def upsert_drug_class(self,drug_class:DrugClassRelationship)-> DrugClassRelationship | None:
        existing = await self.get_class_by_id(
        drug_class.class_id
    )
        if existing:
            existing.name = drug_class.class_name
            existing.class_type = drug_class.class_type
            existing.source = drug_class.relationship_source
            return existing

        entity = DrugClassEntity(
            class_id=drug_class.class_id,
            name=drug_class.class_name,
            class_type=drug_class.class_type,
            source=drug_class.relationship_source,
        )
        self.session.add(entity)
        return entity
    async def class_relationship_exists(self,source_rxcui: str,target_class_id: str,relationship_type: str | None,relationship_source: str) -> bool:
        result = await self.session.execute(
            select(DrugClassRelationshipEntity).where(
                DrugClassRelationshipEntity.source_rxcui== source_rxcui,
                DrugClassRelationshipEntity.target_class_id== target_class_id,
                DrugClassRelationshipEntity.relationship_type== relationship_type,
                DrugClassRelationshipEntity.relationship_source== relationship_source,
            )
        )
        return result.scalar_one_or_none() is not None
    async def add_class_relationship(self,relationship: DrugClassRelationship,) -> DrugClassRelationshipEntity | None:
        exists = await self.class_relationship_exists(
            relationship.source_rxcui,
            relationship.class_id,
            relationship.relationship_type,
            relationship.relationship_source,
        )

        if exists:
            return None

        entity = DrugClassRelationshipEntity(
            source_rxcui=relationship.source_rxcui,
            target_class_id=relationship.class_id,
            relationship_type=relationship.relationship_type,
            relationship_source=relationship.relationship_source,
        )
        self.session.add(entity)
        return entity
    
    async def commit(self):
        await self.session.commit()
    
    async def get_many_by_rxcui(self,rxcuis: list[str]) -> list[DrugEntity]:
        if not rxcuis:
            return []
        result = await self.session.execute(select(DrugEntity).where(DrugEntity.rxcui.in_(rxcuis)))
        return list(result.scalars().all())