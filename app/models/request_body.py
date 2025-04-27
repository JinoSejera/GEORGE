from pydantic import BaseModel

class RequestBody(BaseModel):
    query: str
    chat_history:str