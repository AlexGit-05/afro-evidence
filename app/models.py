from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="The question to ask about the documents")
    top_k: int = Field(default=3, description="Number of most relevant documents to retrieve")

class Document(BaseModel):
    title: str
    content: str
    doi: Optional[str] = None
    keywords: List[str] = []
    metadata: dict = Field(default_factory=dict)

class QueryResponse(BaseModel):
    answer: str
    documents: List[Document]
    doi_links: List[str] = Field(default_factory=list)
