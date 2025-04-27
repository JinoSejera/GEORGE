import logging
import asyncio
import json

from fastapi import APIRouter, Query, HTTPException, Request, Depends
from semantic_kernel.contents import ChatHistory, ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole


from ...models.request_body import RequestBody
from ...models.response_body import ResponseBody
from ...services.george_qa_service import GeorgeQAService
from ...services.knowledge_base_service import KnowledgeBaseService
from ...services.chat_history_service import ChatHistoryService
from ...dependencies import get_george_ask_service, get_chat_history, get_knowledge_base_service
from ...utils.limiter import limiter


api = "George API Q&A"
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/askgeorge")

@router.post('/ask',tags=[api], response_model=ResponseBody)
@limiter.limit("5/hour")
async def ask(
    request:Request,
    request_body:RequestBody,
    george_service: GeorgeQAService = Depends(get_george_ask_service),
    history: ChatHistoryService = Depends(get_chat_history),
    kb: KnowledgeBaseService = Depends(get_knowledge_base_service)
):
    try:
        chat_history:ChatHistory = history.load_chat_history(request_body.chat_history) if request_body.chat_history else ChatHistory()
        
        response, kb_results, web_search_results = await george_service.ask_async(request_body.query, chat_history)
        
        chat_history.add_user_message(request_body.query)
        chat_history.add_assistant_message(response)
        
        return ResponseBody(name="George",
                            message=response, 
                            chat_history=history.get_chat_history(chat_history), 
                            kb_results=kb_results, 
                            web_search_results=web_search_results)

    except Exception as e:
        logger.error(f"Failed to process query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {e}")

