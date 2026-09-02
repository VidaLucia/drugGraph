from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drug_entity import DrugEntity, DrugRelationshipEntity
from app.schema.drug import DrugConcept, DrugRelationship

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
    async def commit(self):
        await self.session.commit()
    
    async def get_many_by_rxcui(self,rxcuis: list[str]) -> list[DrugEntity]:
        if not rxcuis:
            return []
        result = await self.session.execute(select(DrugEntity).where(DrugEntity.rxcui.in_(rxcuis)))
        return list(result.scalars().all())