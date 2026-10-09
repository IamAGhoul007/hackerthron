from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time
from contextlib import asynccontextmanager

from app.config import settings
from app.logging_setup import setup_logging
from app.api.routes_health import router as health_router
from app.api.routes_chat import router as chat_router
from app.api.routes_admin import router as admin_router
from app.ingestion.indexer import Indexer

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: auto-ingest if needed
    indexer = Indexer()
    try:
        indexer.rebuild(force=False)
    except Exception as e:
        print(f"Startup ingestion failed: {e}")
    yield
    # Shutdown

app = FastAPI(title="ReleaseIQ API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred.", "details": str(exc)},
    )
