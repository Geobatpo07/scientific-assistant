"""Document chunking for RAG."""

from typing import List

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentChunker:
    """Split documents into chunks for RAG."""
    
    @staticmethod
    def chunk_by_size(
        text: str,
        chunk_size: int = settings.CHUNK_SIZE,
        overlap: int = settings.CHUNK_OVERLAP,
    ) -> List[str]:
        """Split text into overlapping chunks by character count."""
        chunks = []
        
        if len(text) <= chunk_size:
            return [text]
        
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    @staticmethod
    def chunk_by_paragraph(
        text: str,
        chunk_size: int = settings.CHUNK_SIZE,
        overlap: int = 0,
    ) -> List[str]:
        """Split text into chunks by paragraphs."""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Created {len(chunks)} chunks by paragraph")
        return chunks
    
    @staticmethod
    def chunk_by_section(text: str) -> List[str]:
        """Split text by markdown sections."""
        chunks = []
        current_section = ""
        
        lines = text.split('\n')
        
        for line in lines:
            # Check if line is a section header
            if line.startswith('#'):
                if current_section:
                    chunks.append(current_section.strip())
                current_section = line
            else:
                current_section += '\n' + line
        
        if current_section:
            chunks.append(current_section.strip())
        
        logger.info(f"Created {len(chunks)} chunks by section")
        return chunks
    
    @staticmethod
    def chunk_document(
        text: str,
        method: str = "size",
        **kwargs
    ) -> List[str]:
        """Chunk document using specified method."""
        if method == "size":
            return DocumentChunker.chunk_by_size(text, **kwargs)
        elif method == "paragraph":
            return DocumentChunker.chunk_by_paragraph(text, **kwargs)
        elif method == "section":
            return DocumentChunker.chunk_by_section(text)
        else:
            raise ValueError(f"Unknown chunking method: {method}")
