import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Model Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(BASE_DIR, "data", "pdfs")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "vector_db")
LOG_DIR = os.path.join(BASE_DIR, "data", "logs")

# Create necessary directories
for directory in [PDF_DIR, VECTOR_DB_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)
