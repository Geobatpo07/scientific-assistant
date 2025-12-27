"""Citation and reference management."""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Citation:
    """Structured citation information."""
    
    authors: List[str]
    title: str
    year: int
    source: str
    url: Optional[str] = None
    doi: Optional[str] = None
    
    def to_apa(self) -> str:
        """Format as APA citation."""
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += ", et al."
        
        citation = f"{authors_str} ({self.year}). {self.title}. {self.source}."
        
        if self.doi:
            citation += f" https://doi.org/{self.doi}"
        elif self.url:
            citation += f" Retrieved from {self.url}"
        
        return citation
    
    def to_bibtex(self) -> str:
        """Format as BibTeX citation."""
        authors_str = " and ".join(self.authors)
        
        bibtex = f"""@article{{{self.title.lower().replace(" ", "_")},
    author={{{authors_str}}},
    title={{{self.title}}},
    year={{{self.year}}},
    journal={{{self.source}}}"""
        
        if self.doi:
            bibtex += f",\n    doi={{{self.doi}}}"
        if self.url:
            bibtex += f",\n    url={{{self.url}}}"
        
        bibtex += "\n}"
        return bibtex


class CitationManager:
    """Manage citations and references."""
    
    def __init__(self):
        """Initialize citation manager."""
        self.citations: List[Citation] = []
    
    def add_citation(self, citation: Citation) -> None:
        """Add citation."""
        if citation not in self.citations:
            self.citations.append(citation)
    
    def generate_bibliography(self, format: str = "apa") -> str:
        """Generate bibliography in specified format."""
        if format == "apa":
            return self._generate_apa_bibliography()
        elif format == "bibtex":
            return self._generate_bibtex_bibliography()
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _generate_apa_bibliography(self) -> str:
        """Generate APA formatted bibliography."""
        sorted_citations = sorted(
            self.citations,
            key=lambda c: (c.authors[0] if c.authors else "", c.year)
        )
        
        bibliography = "Bibliography\n" + "=" * 50 + "\n\n"
        for citation in sorted_citations:
            bibliography += citation.to_apa() + "\n\n"
        
        return bibliography
    
    def _generate_bibtex_bibliography(self) -> str:
        """Generate BibTeX formatted bibliography."""
        bibtex = "@comment{Generated bibliography}\n\n"
        for citation in self.citations:
            bibtex += citation.to_bibtex() + "\n\n"
        return bibtex
    
    def extract_citations_from_text(self, text: str) -> List[str]:
        """Extract citation markers from text."""
        import re
        
        # Look for [Author Year] or similar patterns
        pattern = r'\[([\w\s]+,?\s\d{4})\]'
        citations = re.findall(pattern, text)
        
        return citations
