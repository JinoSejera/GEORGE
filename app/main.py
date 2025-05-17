import os
import time
import logging
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

# -------------------- Logging & Environment Setup --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True
)
logger = logging.getLogger(__name__)

load_dotenv()
environment = os.getenv("ENVIRONMENT", "production")
cors_origins = os.getenv("CORS_ORIGINS", "")
logger.info(f"Environment: {environment}")

# -------------------- FastAPI App Initialization --------------------
app = FastAPI(title="GEORGE API", version="0.1.0")

# -------------------- CORS Configuration --------------------
allowed_origins = ["*"] if environment == "development" else [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------------- Rate Limiting --------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# -------------------- Repository Singletons --------------------
KernelRepository()
KnowledgeBaseRepository()

# -------------------- Middleware --------------------
@app.middleware("http")
async def log_request(request: Request, call_next):
    """
    Middleware to log each HTTP request with client IP and processing time.
    """
    start_time = time.time()
    client_ip = get_client_ip(request)
    logger.info(f"Request from {client_ip} to {request.url}")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error processing request from {client_ip}: {e}")
        response = JSONResponse(content={"message": "Internal Server Error"}, status_code=500)

    process_time = time.time() - start_time
    logger.info(f"Request from {client_ip} processed in {process_time:.4f} seconds")
    return response

@app.middleware("http")
async def check_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin and origin not in allowed_origins:
        return JSONResponse(status_code=403, content={"detail": "Invalid origin"})
    
    return await call_next(request)
   

# -------------------- Global Exception Handler --------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch unhandled exceptions and return a 500 response.
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal Server Error: {exc}"},
    )

# -------------------- Routers --------------------
app.include_router(george_router)
app.include_router(ingest_router)
