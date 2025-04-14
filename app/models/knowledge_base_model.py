from typing import Annotated, Any

from pydantic import BaseModel

from semantic_kernel.connectors.ai.open_ai import OpenAIEmbeddingPromptExecutionSettings
from semantic_kernel.data import (
    VectorStoreRecordDataField,
    VectorStoreRecordKeyField,
    VectorStoreRecordVectorField,
    vectorstoremodel,
)

# @vectorstoremodel
# class PodCastKnowledgeBaseModel(BaseModel):
#     podcast_id: Annotated[str, VectorStoreRecordKeyField]
#     podcast_title: Annotated[str | None, VectorStoreRecordDataField()] = None
#     content: Annotated[
#         str,
#         VectorStoreRecordDataField(
#             has_embedding=True, embedding_property_name="content_vector", is_full_text_searchable=True
#         ),
#     ]
#     content_vector: Annotated[
#         list[float] | None,
#         VectorStoreRecordVectorField(
#             dimensions=1536,
#             local_embedding=True,
#             embedding_settings={"embedding": OpenAIEmbeddingPromptExecutionSettings(dimensions=1536)},
#         ),
#     ] = None
#     content_reserve: Annotated[str, VectorStoreRecordDataField()]
#     time_stamp: Annotated[str, VectorStoreRecordDataField()]
    
class PodCastKnowledgeBaseModel(BaseModel):
    id:str
    podcast_title: str
    content: str
    time_stamp: str