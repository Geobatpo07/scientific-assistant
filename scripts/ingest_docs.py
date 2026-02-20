"""Script to ingest documents into the knowledge base."""

import sys
from pathlib import Path
import argparse

from app.ingestion.pipeline import IngestionPipeline
from app.vectorstore.chroma import get_vector_store
from app.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Main ingestion script."""
    parser = argparse.ArgumentParser(description="Ingest documents into Teslas.ai knowledge base")
    parser.add_argument("path", help="Path to document or directory")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="Chunk overlap")
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        logger.error(f"Path not found: {path}")
        sys.exit(1)
    
    # Initialize pipeline and vector store
    pipeline = IngestionPipeline(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    vector_store = get_vector_store()
    
    try:
        if path.is_file():
            logger.info(f"Ingesting file: {path}")
            chunks = pipeline.ingest_document(path)
            vector_store.add_texts(chunks)
            logger.info(f"Ingested {len(chunks)} chunks")
            
        else:
            logger.info(f"Ingesting directory: {path}")
            documents = pipeline.ingest_directory(path)
            
            total_chunks = 0
            for file_path, chunks in documents.items():
                vector_store.add_texts(chunks)
                total_chunks += len(chunks)
                logger.info(f"Ingested {file_path}: {len(chunks)} chunks")
            
            logger.info(f"Total chunks ingested: {total_chunks}")
        
        logger.info("✅ Ingestion completed successfully")
        
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
