from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DrugEntity(Base):
    __tablename__ = "drug_entities"
    id: Mapped[int] = mapped_column(primary_key=True)
    rxcui: Mapped[str] = mapped_column(String(20),unique=True,nullable=False,index=True,)
    name: Mapped[str] = mapped_column(String(255),nullable=False,)
    entity_type: Mapped[str] = mapped_column(String(50),nullable=False,)
    synonym: Mapped[str | None] = mapped_column(String(255),nullable=True,)
    
class DrugRelationshipEntity(Base):
    __tablename__ = "drug_relationships"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_rxcui: Mapped[str] = mapped_column(ForeignKey("drug_entities.rxcui"),nullable=False,index=True,)
    target_rxcui: Mapped[str] = mapped_column(ForeignKey("drug_entities.rxcui"),nullable=False,index=True,)
    relationship_type: Mapped[str] = mapped_column(String(100),nullable=False,)
    __table_args__ = (UniqueConstraint("source_rxcui","target_rxcui","relationship_type",name="uq_drug_relationship",),)