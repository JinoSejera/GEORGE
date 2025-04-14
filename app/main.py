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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True
    )

logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="GEORGE API", version="0.1.0")

#rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize Singleton 
KernelRepository()
KnowledgeBaseRepository()

@app.middleware("http")
async def log_request(request: Request, call_next):
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
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal Server Error: {exc}"},
    )
    
app.include_router(george_router)
app.include_router(ingest_router)
