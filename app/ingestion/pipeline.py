"""Document ingestion pipeline."""

from pathlib import Path
from typing import List, Optional

from app.ingestion.chunker import DocumentChunker
from app.ingestion.cleaner import DocumentCleaner
from app.ingestion.loader import DocumentLoader
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IngestionPipeline:
    """Complete pipeline for document ingestion and preparation."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        chunk_method: str = "size",
    ):
        """Initialize ingestion pipeline."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunk_method = chunk_method
    
    def ingest_document(self, file_path: Path) -> List[str]:
        """Ingest a single document through the pipeline."""
        logger.info(f"Ingesting document: {file_path}")
        
        # Load
        contents = DocumentLoader.load_document(Path(file_path))
        
        processed_chunks = []
        for content in contents:
            # Clean
            cleaned = DocumentCleaner.clean_document(content)
            
            # Chunk
            chunks = DocumentChunker.chunk_document(
                cleaned,
                method=self.chunk_method,
                chunk_size=self.chunk_size,
                overlap=self.chunk_overlap,
            )
            
            processed_chunks.extend(chunks)
        
        logger.info(f"Processed {len(processed_chunks)} chunks from {file_path}")
        return processed_chunks
    
    def ingest_directory(self, dir_path: Path) -> dict:
        """Ingest all documents in a directory."""
        logger.info(f"Ingesting directory: {dir_path}")
        
        all_chunks = {}
        documents = DocumentLoader.load_directory(Path(dir_path))
        
        for file_path, contents in documents.items():
            chunks = []
            for content in contents:
                cleaned = DocumentCleaner.clean_document(content)
                file_chunks = DocumentChunker.chunk_document(
                    cleaned,
                    method=self.chunk_method,
                    chunk_size=self.chunk_size,
                    overlap=self.chunk_overlap,
                )
                chunks.extend(file_chunks)
            
            all_chunks[file_path] = chunks
        
        total_chunks = sum(len(chunks) for chunks in all_chunks.values())
        logger.info(f"Ingested {len(all_chunks)} documents with {total_chunks} total chunks")
        
        return all_chunks
