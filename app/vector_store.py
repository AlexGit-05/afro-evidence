import os
import json
import numpy as np
import faiss
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import GOOGLE_API_KEY, EMBEDDING_MODEL, VECTOR_DB_DIR
from app.logger import logger

# Configure Google API
genai.configure(api_key=GOOGLE_API_KEY)

class VectorStore:
    def __init__(self):
        self.index = None
        self.documents = []
        # Initialize the embedding model
        self.embedding_model = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        self._load_or_create_index()
        self._load_documents()

    def _load_or_create_index(self):
        index_path = os.path.join(VECTOR_DB_DIR, "faiss_index.bin")
        if os.path.exists(index_path):
            logger.info("Loading existing FAISS index")
            self.index = faiss.read_index(index_path)
        else:
            logger.info("Creating new FAISS index")
            self.index = faiss.IndexFlatL2(768)  # Gemini embeddings are 768-dimensional

    def _load_documents(self):
        """Load documents from JSON file if it exists"""
        docs_path = os.path.join(VECTOR_DB_DIR, "documents.json")
        if os.path.exists(docs_path):
            logger.info("Loading existing documents")
            with open(docs_path, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)

    def _save_documents(self):
        """Save documents to JSON file"""
        docs_path = os.path.join(VECTOR_DB_DIR, "documents.json")
        with open(docs_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

    def _get_embedding(self, text: str) -> np.ndarray:
        try:
            # Use the embed_query method which handles both queries and documents
            embedding = self.embedding_model.embed_query(text)
            return np.array(embedding).astype('float32').reshape(1, -1)
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            raise

    def add_documents(self, documents: list):
        if not documents:
            return

        embeddings = []
        for doc in documents:
            embedding = self._get_embedding(doc["content"])
            embeddings.append(embedding)
            self.documents.append(doc)

        embeddings = np.vstack(embeddings)
        self.index.add(embeddings)
        
        # Save both the index and documents
        faiss.write_index(self.index, os.path.join(VECTOR_DB_DIR, "faiss_index.bin"))
        self._save_documents()
        logger.info(f"Added {len(documents)} documents to the index")

    def search(self, query: str, top_k: int = 3) -> list:
        if not self.documents:
            logger.warning("No documents in the vector store")
            return []
            
        query_embedding = self._get_embedding(query)
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])
        
        return results
