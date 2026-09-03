# DrugGraph



Built with **React, TypeScript, FastAPI, PostgreSQL, SQLAlchemy, and Docker**.

DrugGraph integrates **RxNorm** and **RxClass**, normalizing their data into a unified graph model while preserving relationship provenance.

Users can search for medications, explore and expand related concepts, filter node types, and inspect relationships through an interactive React Flow visualization.

## Run

```bash
docker compose up --build

Frontend: localhost:3000 · API: localhost:8000/docs