"""Document cleaning and preprocessing."""

import re
from typing import List

from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentCleaner:
    """Clean and preprocess documents."""
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove extra whitespace."""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\n+', '\n\n', text)
        return text.strip()
    
    @staticmethod
    def remove_special_characters(text: str, preserve_math: bool = True) -> str:
        """Remove special characters while preserving structure."""
        if preserve_math:
            # Preserve LaTeX and mathematical notation
            return text
        else:
            # Remove non-alphanumeric except common symbols
            text = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]\{\}]', '', text)
            return text
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text encoding and structure."""
        # Remove null characters
        text = text.replace('\x00', '')
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Remove page breaks and form feeds
        text = text.replace('\f', '\n')
        return text
    
    @staticmethod
    def extract_metadata(text: str) -> dict:
        """Extract potential metadata from text."""
        metadata = {}
        
        # Try to extract title (first non-empty line)
        lines = [l for l in text.split('\n') if l.strip()]
        if lines:
            metadata['title'] = lines[0][:100]
        
        # Count sections
        metadata['sections'] = len(re.findall(r'^#+\s', text, re.MULTILINE))
        
        # Count equations
        metadata['equations'] = len(re.findall(r'\$\$.*?\$\$', text, re.DOTALL))
        metadata['inline_math'] = len(re.findall(r'\$.*?\$', text))
        
        # Word count
        metadata['word_count'] = len(text.split())
        
        return metadata
    
    @staticmethod
    def clean_document(text: str) -> str:
        """Apply full cleaning pipeline."""
        text = DocumentCleaner.normalize_text(text)
        text = DocumentCleaner.remove_extra_whitespace(text)
        text = DocumentCleaner.remove_special_characters(text, preserve_math=True)
        return text
