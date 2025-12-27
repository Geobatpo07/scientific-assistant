"""Helper utilities for Teslas.ai."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session_with_retries(
    retries: int = 3, backoff_factor: float = 0.3
) -> requests.Session:
    """Create a requests session with automatic retries."""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def validate_pdf_path(path: str) -> Path:
    """Validate and return PDF path."""
    pdf_path = Path(path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")
    
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {path}")
    
    return pdf_path


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists and return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_getenv(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Safely get environment variable with optional validation."""
    value = os.getenv(key, default)
    
    if required and not value:
        raise ValueError(f"Required environment variable '{key}' not set")
    
    return value


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_sections(text: str, section_markers: Dict[str, str]) -> Dict[str, str]:
    """Extract sections from text based on markers."""
    sections = {}
    
    for section_name, marker in section_markers.items():
        if marker in text:
            start_idx = text.find(marker) + len(marker)
            # Find next section or end of text
            remaining = text[start_idx:]
            end_idx = len(remaining)
            
            for other_marker in section_markers.values():
                if other_marker != marker and other_marker in remaining:
                    idx = remaining.find(other_marker)
                    end_idx = min(end_idx, idx)
            
            sections[section_name] = remaining[:end_idx].strip()
    
    return sections


def format_references(references: List[str]) -> str:
    """Format a list of references for display."""
    if not references:
        return "No references"
    
    formatted = "References:\n"
    for i, ref in enumerate(references, 1):
        formatted += f"{i}. {ref}\n"
    
    return formatted
