from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="WSJF Excel Generator API",
    description="API for managing WSJF prioritization and Excel generation",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "WSJF Excel Generator API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}