import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.drugs import router as drugs_router


app = FastAPI(
    title="DrugGraph API",
    version="0.1.0",
)

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

frontend_url = os.getenv("FRONTEND_URL")

if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drugs_router)


@app.get("/health")
async def health():
    return {"status": "ok"}