from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router
from app.api.pi_endpoints import router as pi_router
from app.core.config import settings
from app.core.database import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    db_manager.connect()
    yield
    # Shutdown: Close database connection
    db_manager.close()


app = FastAPI(
    title="WSJF Excel Generator API",
    description="""
    ## WSJF (Weighted Shortest Job First) Excel Generator API

    This API provides functionality for managing WSJF prioritization and generating Excel reports.
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "WSJF API Support",
        "url": "https://github.com/Wyoc/bsd-wsjf",
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
app.include_router(pi_router)


@app.get("/")
async def root():
    return {
        "message": "WSJF Excel Generator API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }
