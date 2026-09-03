import pytest_asyncio

from sqlalchemy import delete
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.models.drug_entity import (
    DrugEntity,
    DrugRelationshipEntity,
    DrugClassEntity,
    DrugClassRelationshipEntity,
)

TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/druggraph_test"
)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:

        await session.execute(
            delete(DrugClassRelationshipEntity)
        )

        await session.execute(
            delete(DrugRelationshipEntity)
        )

        await session.execute(
            delete(DrugClassEntity)
        )

        await session.execute(
            delete(DrugEntity)
        )

        await session.commit()

        yield session