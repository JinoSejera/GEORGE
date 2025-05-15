import time
import logging
import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from .utils.get_client_ip import get_client_ip
from .utils.limiter import limiter
from .endpoints.v1.ask import router as george_router
from .endpoints.v1.ingest_tanscript import router as ingest_router
from .repository.kernel_repository import KernelRepository
from .repository.knowledge_base_repository import KnowledgeBaseRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True
    )

logger = logging.getLogger(__name__)
load_dotenv()

# Parse CORS_ORIGINS from environment variable as a list
cors_origins = os.getenv("CORS_ORIGINS", "")
allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app = FastAPI(title="GEORGE API", version="0.1.0")

# Rate limiting setup using SlowAPI limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware configuration to allow all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize singleton instances for repositories
KernelRepository()
KnowledgeBaseRepository()

@app.middleware("http")
async def log_request(request: Request, call_next):
    """
    Middleware to log each HTTP request with client IP and processing time.

    Args:
        request (Request): The incoming HTTP request.
        call_next (function): The next middleware or route handler.

    Returns:
        Response: The HTTP response.
    """
    start_time = time.time()
    client_ip = get_client_ip(request)
    logger.info(f"Request from {client_ip} to {request.url}")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error processing request from {client_ip}: {e}")
        response = JSONResponse(content={"message":"Internal Server Error"}, status_code=500)

    process_time = time.time() - start_time
    logger.info(f"Request from {client_ip} processed in {process_time:.4f} seconds")
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch unhandled exceptions and return a 500 response.

    Args:
        request (Request): The incoming HTTP request.
        exc (Exception): The exception that was raised.

    Returns:
        JSONResponse: The error response.
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal Server Error: {exc}"},
    )
    
app.include_router(george_router)
app.include_router(ingest_router)
