from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse, Document
from app.vector_store import VectorStore
import google.generativeai as genai
from app.config import GOOGLE_API_KEY, LLM_MODEL
from app.logger import logger

router = APIRouter()
vector_store = VectorStore()

# Configure the model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(LLM_MODEL)

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        # Retrieve relevant documents
        relevant_docs = vector_store.search(request.query, request.top_k)
        
        if not relevant_docs:
            raise HTTPException(status_code=404, detail="No relevant documents found")

        # Prepare context for the LLM
        context = "\n\n".join([f"Title: {doc['title']}\nContent: {doc['content']}" for doc in relevant_docs])
        
        # Create prompt with zero-shot instruction
        prompt = f"""Based on the following context, answer the question. Include DOI links as a list after your answer.

Context:
{context}

Question: {request.query}

Please provide a comprehensive answer and list any relevant DOI links."""

        # Generate response
        response = model.generate_content(prompt)
        
        return QueryResponse(
            answer=response.text,
            documents=[],
            doi_links=[]
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
