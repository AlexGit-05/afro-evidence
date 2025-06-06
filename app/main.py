from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.config import APP_HOST, APP_PORT, APP_DEBUG
from app.logger import logger
import uvicorn

app = FastAPI(
    title="Afro Evidence",
    description="RAG system using Gemini and FAISS",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG API"}

if __name__ == "__main__":
    logger.info(f"Starting server on {APP_HOST}:{APP_PORT}")
    uvicorn.run(
        "app.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=APP_DEBUG
    )

