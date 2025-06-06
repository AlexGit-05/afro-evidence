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
        
        # Create one-shot prompt with example
        prompt = f"""You are a medical research assistant. Answer questions based on the provided context in markdown format. Include a list of DOI references at the end.

Example:
Context:
Title: Example Research
Content: This is an example research paper about diabetes treatment.

Question: What is the main finding about diabetes treatment?

Answer:
The main finding is that regular exercise combined with medication shows significant improvement in diabetes management.

References:
- [Example Research](https://doi.org/10.1234/example.2023)

Now, based on the following context, answer the question:

Context:
{context}

Question: {request.query}

Please provide a comprehensive answer in markdown format and list all relevant DOI references with full URLs."""

        # Generate response
        response = model.generate_content(prompt)
        
        # Extract DOI links from relevant documents
        doi_links = [doc.get('doi') for doc in relevant_docs if doc.get('doi')]
        
        return QueryResponse(
            answer=response.text,
            documents=[Document(**doc) for doc in relevant_docs],
            doi_links=doi_links
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
