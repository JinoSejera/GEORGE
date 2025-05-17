import logging

from fastapi import APIRouter,HTTPException, Request, Depends

from ...services.knowledge_base_service import KnowledgeBaseService
from ...dependencies import get_knowledge_base_service
from ...utils.security import get_api_key


api = "George API Q&A"
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ingest")

@router.post('/transcripts',tags=[api])
async def ingest(
    request:Request,
    kb_service: KnowledgeBaseService = Depends(get_knowledge_base_service),
    api_key: str = Depends(get_api_key)
):
    """
    Endpoint to ingest transcripts into the knowledge base.

    Args:
        request (Request): The incoming HTTP request.
        kb_service (KnowledgeBaseService): Service for ingesting transcripts.

    Returns:
        dict: Success message and status code.
    """
    try:
        await kb_service.ingest_transcripts_async()
        return {
            "message": "Success",
            "status_code": 200
        }
    except Exception as e:
        logger.error(f"Failed to process: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {e}")