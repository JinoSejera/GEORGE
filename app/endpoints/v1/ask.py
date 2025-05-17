import logging
import asyncio
import json

from fastapi import APIRouter, Query, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from semantic_kernel.contents import ChatHistory

from ...models.request_body import RequestBody
from ...models.response_body import ResponseBody
from ...services.george_qa_service import GeorgeQAService
from ...services.chat_history_service import ChatHistoryService
from ...dependencies import get_george_ask_service, get_chat_history
from ...utils.limiter import limiter


api = "George API Q&A"
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/askgeorge")

@router.post('/ask/stream',tags=[api])
@limiter.limit("5/hour")
async def ask_streaming(
    request:Request,
    request_body:RequestBody,
    george_service: GeorgeQAService = Depends(get_george_ask_service),
    history: ChatHistoryService = Depends(get_chat_history)
):
    """
    Handles a streaming Q&A request to George. Streams the response as server-sent events.

    Args:
        request (Request): The incoming HTTP request.
        request_body (RequestBody): The request payload containing the query and chat history.
        george_service (GeorgeQAService): Service for handling Q&A logic.
        history (ChatHistoryService): Service for managing chat history.

    Returns:
        StreamingResponse: The streaming response with the answer.
    """
    try:
        # Load or initialize chat history
        chat_history:ChatHistory = history.load_chat_history(request_body.chat_history) if request_body.chat_history else ChatHistory()
        
        return StreamingResponse(
            content=george_service.ask_streaming_async(request_body.query, chat_history),
            media_type="text/event-stream"
        )

    except Exception as e:
        logger.error(f"Failed to process query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {e}")