"""
Advanced DuckDuckGo-based scientific search engine for Teslas.ai.

This module is designed for academic-level research:
- Strong domain filtering
- Scientific query expansion
- Result scoring and classification
- Ready for RAG + reranking pipelines
"""

from __future__ import annotations

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import re

from ddgs import DDGS

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


# =========================
# Scientific configuration
# =========================

ACADEMIC_DOMAINS = [
    "arxiv.org",
    "hal.science",
    "math.stackexchange.com",
    "mathoverflow.net",
    "springer.com",
    "sciencedirect.com",
    "ieee.org",
    "acm.org",
    "wikipedia.org",
    "ncatlab.org",
    "encyclopediaofmath.org",
    "ams.org",  # American Mathematical Society
    "siam.org",  # Society for Industrial and Applied Mathematics
    "jstor.org",
    "projecteuclid.org",
    "numdam.org",  # Numérisation de documents anciens mathématiques
    "mathscinet.ams.org",
    "zbmath.org",  # Zentralblatt MATH
    "scipost.org",
    "mdpi.com",
    "nature.com",
    "pnas.org",
]

DATA_SCIENCE_DOMAINS = [
    "kaggle.com",
    "towardsdatascience.com",
    "machinelearningmastery.com",
    "distill.pub",
    "jmlr.org",  # Journal of Machine Learning Research
    "neurips.cc",
    "icml.cc",
    "openreview.net",
    "paperswithcode.com",
    "stats.stackexchange.com",
]

MATH_SPECIALIZED_DOMAINS = [
    "mathworld.wolfram.com",
    "planetmath.org",
    "numericalmethods.eng.usf.edu",
    "scholarpedia.org",
]

CODE_DOMAINS = [
    "github.com",
    "gitlab.com",
    "bitbucket.org",
]

SCIENTIFIC_KEYWORDS = [
    "numerical analysis",
    "stability",
    "convergence",
    "error analysis",
    "ODE",
    "PDE",
    "finite difference",
    "finite element",
    "theorem",
    "proof",
    "algorithm",
]

APPLIED_MATH_KEYWORDS = [
    "optimization",
    "variational calculus",
    "functional analysis",
    "spectral methods",
    "monte carlo",
    "stochastic",
    "computational",
    "approximation theory",
    "numerical linear algebra",
    "iterative methods",
    "eigenvalue",
    "boundary value problem",
    "inverse problem",
    "well-posedness",
    "regularization",
]

FUNDAMENTAL_MATH_KEYWORDS = [
    "topology",
    "algebra",
    "analysis",
    "differential geometry",
    "lie group",
    "representation theory",
    "number theory",
    "combinatorics",
    "category theory",
    "measure theory",
    "operator theory",
    "harmonic analysis",
]

DATA_SCIENCE_KEYWORDS = [
    "machine learning",
    "deep learning",
    "neural network",
    "statistical inference",
    "regression",
    "classification",
    "clustering",
    "dimensionality reduction",
    "cross-validation",
    "feature engineering",
    "model selection",
    "ensemble methods",
    "gradient descent",
    "backpropagation",
    "overfitting",
    "bias-variance tradeoff",
]


class SourceType(str, Enum):
    PREPRINT = "preprint"
    JOURNAL = "journal"
    EDUCATIONAL = "educational"
    CODE = "code"
    GENERAL = "general"


@dataclass
class ScientificSearchResult:
    title: str
    url: str
    summary: str
    source_type: SourceType
    domain: str
    score: float


# =========================
# Core scientific searcher
# =========================

class DuckDuckGoScientificSearcher:
    """
    High-quality scientific search engine built on DuckDuckGo.
    """

    def __init__(
        self,
        max_results: int = settings.DUCKDUCKGO_MAX_RESULTS,
        year_filter: Optional[str] = "y",
    ):
        self.max_results = max_results
        self.year_filter = year_filter
        self.ddgs = DDGS()

    # ---------
    # Utilities
    # ---------

    def _extract_domain(self, url: str) -> str:
        match = re.search(r"https?://([^/]+)/", url)
        return match.group(1) if match else ""

    def _classify_source(self, domain: str) -> SourceType:
        if "arxiv" in domain or "hal" in domain:
            return SourceType.PREPRINT
        if domain in CODE_DOMAINS:
            return SourceType.CODE
        if domain in ACADEMIC_DOMAINS:
            return SourceType.JOURNAL
        if "wikipedia" in domain or "encyclopedia" in domain:
            return SourceType.EDUCATIONAL
        return SourceType.GENERAL

    def _scientific_score(self, domain: str, text: str, query: str = "") -> float:
        """
        Heuristic scientific relevance score with math and data science awareness.
        """
        score = 0.0
        text_lower = text.lower()
        query_lower = query.lower()

        # Domain-based scoring
        if domain in ACADEMIC_DOMAINS:
            score += 3.0
        if domain in DATA_SCIENCE_DOMAINS:
            score += 2.5
        if domain in MATH_SPECIALIZED_DOMAINS:
            score += 2.0
        if domain in CODE_DOMAINS:
            score += 1.5

        # General scientific keywords
        for kw in SCIENTIFIC_KEYWORDS:
            if kw.lower() in text_lower:
                score += 0.4

        # Applied mathematics keywords
        for kw in APPLIED_MATH_KEYWORDS:
            if kw.lower() in text_lower:
                score += 0.5

        # Fundamental mathematics keywords
        for kw in FUNDAMENTAL_MATH_KEYWORDS:
            if kw.lower() in text_lower:
                score += 0.5

        # Data science keywords
        for kw in DATA_SCIENCE_KEYWORDS:
            if kw.lower() in text_lower:
                score += 0.5

        # Boost if query terms appear in title/text
        if query:
            query_terms = query_lower.split()
            for term in query_terms:
                if len(term) > 3 and term in text_lower:
                    score += 0.3

        # Penalties for low-quality indicators
        if "advertisement" in text_lower or "sponsored" in text_lower:
            score -= 2.0
        if "buy now" in text_lower or "download free" in text_lower:
            score -= 1.5

        # Bonus for mathematical notation indicators
        math_indicators = ["equation", "formula", "\\frac", "\\sum", "proof of", "lemma", "corollary"]
        for indicator in math_indicators:
            if indicator in text_lower:
                score += 0.3

        return round(score, 2)

    def _expand_query(self, query: str, mode: str = "auto") -> str:
        """
        Intelligently expand query based on detected domain.
        """
        query_lower = query.lower()
        
        # Detect query type
        is_data_science = any(
            kw in query_lower for kw in ["machine learning", "neural network", "data", "model", "prediction"]
        )
        is_fundamental_math = any(
            kw in query_lower for kw in ["topology", "algebra", "group", "ring", "field", "manifold"]
        )
        is_applied_math = any(
            kw in query_lower for kw in ["numerical", "pde", "ode", "optimization", "simulation"]
        )
        
        # Select appropriate domains
        if mode == "data_science" or (mode == "auto" and is_data_science):
            domains = ACADEMIC_DOMAINS + DATA_SCIENCE_DOMAINS
            keywords = DATA_SCIENCE_KEYWORDS[:5]
        elif mode == "fundamental" or (mode == "auto" and is_fundamental_math):
            domains = ACADEMIC_DOMAINS + MATH_SPECIALIZED_DOMAINS
            keywords = FUNDAMENTAL_MATH_KEYWORDS[:5]
        elif mode == "applied" or (mode == "auto" and is_applied_math):
            domains = ACADEMIC_DOMAINS + MATH_SPECIALIZED_DOMAINS
            keywords = APPLIED_MATH_KEYWORDS[:5]
        else:
            # Default: broad scientific search
            domains = ACADEMIC_DOMAINS
            keywords = SCIENTIFIC_KEYWORDS[:4]
        
        # Build domain filter (limit to avoid too long queries)
        top_domains = domains[:10]
        domain_filter = " OR ".join(f"site:{d}" for d in top_domains)
        keyword_str = " OR ".join(keywords)
        
        # Don't over-complicate short queries
        if len(query.split()) <= 2:
            return f"{query} ({keyword_str})"
        
        return f"{query} ({keyword_str})"

    # -----------------
    # Public API
    # -----------------

    def search(self, query: str) -> List[ScientificSearchResult]:
        """
        Perform a high-quality scientific search.
        """
        logger.info(f"[Teslas.ai] Scientific search: {query}")

        enriched_query = self._expand_query(query)
        logger.debug(f"Expanded query: {enriched_query}")

        try:
            raw_results = self.ddgs.text(
                keywords=enriched_query,
                max_results=self.max_results * 2,
                safesearch="Off",
                timelimit=self.year_filter,
            )

            results: List[ScientificSearchResult] = []

            for r in raw_results:
                url = r.get("href", "")
                domain = self._extract_domain(url)
                text_blob = f"{r.get('title', '')} {r.get('body', '')}"

                score = self._scientific_score(domain, text_blob, query)

                # Reject low-quality noise early
                if score < 1.5:
                    continue

                result = ScientificSearchResult(
                    title=r.get("title", ""),
                    url=url,
                    summary=r.get("body", ""),
                    domain=domain,
                    source_type=self._classify_source(domain),
                    score=score,
                )
                results.append(result)

            # Sort by scientific relevance
            results.sort(key=lambda x: x.score, reverse=True)

            logger.info(
                f"[Teslas.ai] {len(results)} scientific results retained "
                f"(out of {len(list(raw_results))})"
            )

            return results[: self.max_results]

        except Exception as e:
            logger.error(f"[Teslas.ai] Scientific search error: {e}")
            return []

    # -----------------
    # Specialized modes
    # -----------------

    def search_arxiv(self, query: str, category: str = "math") -> List[ScientificSearchResult]:
        """Search arXiv with optional category filter (math, cs, stat, etc.)"""
        return self.search(f"site:arxiv.org {query} {category}")

    def search_applied_mathematics(self, query: str) -> List[ScientificSearchResult]:
        """Specialized search for applied mathematics (numerical methods, PDEs, optimization)."""
        expanded = f"{query} numerical analysis computational OR finite element OR optimization"
        return self.search(expanded)
    
    def search_fundamental_mathematics(self, query: str) -> List[ScientificSearchResult]:
        """Specialized search for fundamental mathematics (algebra, topology, analysis)."""
        expanded = f"{query} theorem proof lemma OR topology OR algebra"
        return self.search(expanded)
    
    def search_data_science(self, query: str) -> List[ScientificSearchResult]:
        """Specialized search for data science and machine learning."""
        expanded = f"{query} machine learning statistical OR neural network OR regression"
        results = self.search(expanded)
        
        # Re-rank with data science bias
        for result in results:
            if any(domain in result.domain for domain in DATA_SCIENCE_DOMAINS):
                result.score += 1.0
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def search_numerical_methods(self, query: str) -> List[ScientificSearchResult]:
        """Search for numerical methods implementations and theory."""
        expanded = f"{query} numerical methods algorithm implementation convergence stability"
        return self.search(expanded)
    
    def search_statistics(self, query: str) -> List[ScientificSearchResult]:
        """Search for statistical methods and theory."""
        expanded = f"{query} statistical inference hypothesis test OR distribution OR bayesian"
        return self.search(expanded)

    def search_code(self, query: str, language: Optional[str] = None) -> List[ScientificSearchResult]:
        """Search for code implementations with optional language filter."""
        lang_filter = f"{language}" if language else ""
        return self.search(f"{query} {lang_filter} site:github.com OR site:gitlab.com")


# =========================
# Factory
# =========================

def create_searcher() -> DuckDuckGoScientificSearcher:
    """
    Factory for Teslas.ai scientific searcher.
    """
    return DuckDuckGoScientificSearcher()
