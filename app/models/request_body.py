from pydantic import BaseModel


class RequestBody(BaseModel):
    query: str
    chat_history:str
    
class ResponseBody(BaseModel):
    name:str
    message:str
    kb_result:dict
    chat_history:str