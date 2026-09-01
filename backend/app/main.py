from fastapi import FastAPI

from fastapi import FastAPI

from app.api.drugs import router as drugs_router


app = FastAPI(
    title="DrugGraph API",
    version="0.1.0",
)

app.include_router(drugs_router)


@app.get("/health")
async def health():
    return {"status": "ok"}