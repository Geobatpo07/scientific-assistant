"""Document loader for various file formats."""

import os
from pathlib import Path
from typing import List, Optional

from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentLoader:
    """Load documents from various formats."""
    
    SUPPORTED_FORMATS = {".pdf", ".txt", ".md", ".docx", ".doc"}
    
    @staticmethod
    def load_pdf(file_path: Path, chunk_size: int = 1000) -> List[str]:
        """Load and extract text from PDF."""
        logger.info(f"Loading PDF: {file_path}")
        
        try:
            elements = partition_pdf(
                str(file_path),
                infer_table_structure=True,
            )
            
            # Convert elements to text
            text_content = "\n".join([str(el) for el in elements])
            logger.info(f"Extracted {len(elements)} elements from PDF")
            
            return [text_content]
            
        except Exception as e:
            logger.error(f"Error loading PDF: {file_path}", error=str(e))
            raise
    
    @staticmethod
    def load_text_file(file_path: Path) -> List[str]:
        """Load text from plain text or markdown file."""
        logger.info(f"Loading text file: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            return [content]
            
        except Exception as e:
            logger.error(f"Error loading text file: {file_path}", error=str(e))
            raise
    
    @staticmethod
    def load_document(file_path: Path) -> List[str]:
        """Load document with automatic format detection."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() == ".pdf":
            return DocumentLoader.load_pdf(file_path)
        elif file_path.suffix.lower() in {".txt", ".md"}:
            return DocumentLoader.load_text_file(file_path)
        else:
            # Try unstructured's auto-partition
            try:
                elements = partition(str(file_path))
                text_content = "\n".join([str(el) for el in elements])
                return [text_content]
            except Exception as e:
                logger.error(f"Unsupported file format: {file_path.suffix}", error=str(e))
                raise
    
    @staticmethod
    def load_directory(dir_path: Path) -> dict:
        """Load all supported documents from a directory."""
        logger.info(f"Loading documents from directory: {dir_path}")
        
        documents = {}
        dir_path = Path(dir_path)
        
        for file_path in dir_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in DocumentLoader.SUPPORTED_FORMATS:
                try:
                    content = DocumentLoader.load_document(file_path)
                    documents[str(file_path)] = content
                    logger.info(f"Loaded: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Skipped file: {file_path.name}, error: {str(e)}")
        
        logger.info(f"Loaded {len(documents)} documents from directory")
        return documents
