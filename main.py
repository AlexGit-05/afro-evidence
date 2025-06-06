from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_HOST, APP_PORT, APP_DEBUG
from app.logger import logger
from app.middleware import add_security_middleware
import uvicorn

app = FastAPI(
    title="RAG API",
    description="Retrieval Augmented Generation API for medical research",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
add_security_middleware(app)

# Include routers
from app.routes import router as api_router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    logger.info(f"Starting server on {APP_HOST}:{APP_PORT}")
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=APP_DEBUG
    )