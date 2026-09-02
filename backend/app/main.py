from fastapi import FastAPI

from fastapi import FastAPI

from app.api.drugs import router as drugs_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="DrugGraph API",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(drugs_router)


@app.get("/health")
async def health():
    return {"status": "ok"}