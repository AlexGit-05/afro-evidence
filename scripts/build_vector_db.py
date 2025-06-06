import os
import sys
import fitz  # PyMuPDF
import json
from pathlib import Path
import re

# Add the parent directory to Python path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.vector_store import VectorStore
from app.config import PDF_DIR, VECTOR_DB_DIR
from app.logger import logger

def extract_title_footer_doi_keywords(pdf_path):
    """Extract metadata from PDF file."""
    doc = fitz.open(pdf_path)

    # -------- TITLE EXTRACTION --------
    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]

    title_candidates = []

    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                font_size = span["size"]
                # Filter for longer text, avoid headers/metadata
                if text and len(text.split()) > 3 and not re.search(r'(journal|doi|volume|issue|page \d+)', text, re.IGNORECASE):
                    title_candidates.append((text, font_size, span["bbox"][1]))

    # Sort by font size descending, then y-position (top of page)
    title_candidates.sort(key=lambda x: (-x[1], x[2]))
    title = title_candidates[0][0] if title_candidates else "Unknown Title"

    # -------- CITATION INFO (Footer) EXTRACTION --------
    footer_blocks = first_page.get_text("blocks")
    footer_blocks.sort(key=lambda b: b[1], reverse=True)

    # Look for citation-style text among bottom blocks
    citation_candidates = [
        block[4].strip() for block in footer_blocks
        if re.search(r'(journal|volume|issue|vol\.|no\.|doi|issn)', block[4], re.IGNORECASE)
    ]

    citation_info = citation_candidates[0] if citation_candidates else (
        footer_blocks[0][4].strip() if footer_blocks else "Unknown Citation Info"
    )

    # -------- DOI + KEYWORDS --------
    text_to_search = ""
    for i in range(min(2, len(doc))):  # First 2 pages
        text_to_search += doc[i].get_text()

    # Extract DOI
    doi_match = re.search(r'\b(10\.\d{4,9}/[^\s"\'<>]*)', text_to_search)
    doi = f"http://dx.doi.org/{doi_match.group(1).rstrip('.,;')}" if doi_match else "DOI not found"

    # Extract keywords (supporting Keywords, Key words, Index Terms)
    keywords_match = re.search(r'(Keywords|Key words|Index Terms)\s[:\-–]?\s(.+)', text_to_search, re.IGNORECASE)
    if keywords_match:
        raw_keywords = keywords_match.group(2).split('\n')[0]  # Take only the first line in case of line breaks
        keywords = [kw.strip().strip('.') for kw in re.split(r',|;', raw_keywords) if kw.strip()]
    else:
        keywords = []

    return title, citation_info, doi, keywords

def process_pdf(pdf_path):
    """Process a single PDF file and return its content and metadata."""
    try:
        doc = fitz.open(pdf_path)
        content = ""
        for page in doc:
            content += page.get_text()

        # Clean the text: remove multiple newlines and replace them with a single space
        cleaned_content = re.sub(r'\s*\n\s*', ' ', content)
        cleaned_content = re.sub(r'\s{2,}', ' ', cleaned_content).strip()
        
        title, citation_info, doi, keywords = extract_title_footer_doi_keywords(pdf_path)
        
        return {
            "title": title,
            "content": cleaned_content,
            "doi": doi,
            "keywords": keywords,
            "metadata": {
                "citation_info": citation_info,
                "source_file": os.path.basename(pdf_path)
            }
        }
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {str(e)}")
        return None

def build_vector_db():
    """Build the vector database from PDF files."""
    # Create necessary directories
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

    # Initialize vector store
    vector_store = VectorStore()

    # Process all PDFs in the directory
    pdf_files = list(Path(PDF_DIR).glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {PDF_DIR}")
        return

    documents = []
    for pdf_path in pdf_files:
        logger.info(f"Processing {pdf_path}")
        doc = process_pdf(str(pdf_path))
        if doc:
            documents.append(doc)

    if documents:
        # Add documents to vector store
        vector_store.add_documents(documents)
          # Save document metadata
        metadata_path = os.path.join(VECTOR_DB_DIR, "documents.json")
        with open(metadata_path, "w") as f:
            json.dump(documents, f, indent=2)
        
        logger.info(f"Successfully processed {len(documents)} documents")
    else:
        logger.error("No documents were successfully processed")

if __name__ == "__main__":
    build_vector_db()
