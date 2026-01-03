"""RAG chains for question answering using hybrid vector store.

Pipeline:
    User Query
    ↓
    ContextEngineer.normalize_query (query clarification)
    ↓
    RAG (HF embedding → FAISS → ChromaDB → HF reranker)
    ↓
    ContextEngineer.compress_context (context compression)
    ↓
    Context Assembly (structured, source-aware)
    ↓
    ChatOllama (reasoning & synthesis)
"""

from typing import Optional

from app.llm.ollama import get_llm
from app.vectorstore.store import get_vector_store
from app.vectorstore.retriever import Retriever
from app.hf.context_engineering import get_context_engineer
from app.config import ExecutionMode, ModeConfig
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGChain:
    """Retrieval-Augmented Generation chain with context engineering.

    This chain implements a two-stage context processing pipeline:
    1. Query normalization (Flan-T5): Clarify user intent
    2. Context compression (Flan-T5): Compress retrieved documents
    3. Reasoning (ChatOllama): Generate scientific response

    The context engineer is lightweight and deterministic, operating only
    to preprocess context before it reaches the main LLM.
    """
    
    def __init__(self):
        """Initialize RAG chain with context engineering.

        Components:
        - LLM: ChatOllama (reasoning and synthesis)
        - Vector Store: Hybrid (FAISS + ChromaDB + HF reranker)
        - Retriever: Metadata-aware retrieval
        - ContextEngineer: Flan-T5 preprocessing
        """
        self.llm = get_llm()
        self.vector_store = get_vector_store()
        self.retriever = Retriever(self.vector_store)
        self.context_engineer = get_context_engineer()
    
    def retrieve_and_generate(
        self,
        query: str,
        k: int = 5,
        system_prompt: Optional[str] = None,
        mode: ExecutionMode = ExecutionMode.FAST,
    ) -> dict:
        """Retrieve documents and generate response with context engineering.

        This method implements the full RAG pipeline with mode-aware parameters:
        1. Normalize query using Flan-T5
        2. Retrieve documents using hybrid search + reranking
        3. Compress retrieved context using Flan-T5
        4. Assemble context with source metadata
        5. Generate response using ChatOllama

        Parameters
        ----------
        query : str
            User query (may be ambiguous or noisy)
        k : int, optional
            Number of top documents to retrieve (default: 5)
            Overridden by mode configuration if mode is specified
        system_prompt : str, optional
            Custom system prompt for the LLM
        mode : ExecutionMode, optional
            Execution mode (FAST or FULL), defaults to FAST
            Controls retrieval depth and context size:
            - FAST: faiss_top_k=15, final_chunks=3
            - FULL: faiss_top_k=30, final_chunks=5

        Returns
        -------
        dict
            Response dictionary with keys:
            - query: original user query
            - normalized_query: clarified query (for debugging)
            - response: LLM-generated answer
            - context: assembled context (compressed)
            - sources: retrieved documents with metadata
            - mode: execution mode used
        """
        logger.info(f"RAG query: {query[:100]}... [Mode: {mode.value.upper()}]")
        
        # Get mode-specific RAG configuration
        rag_config = ModeConfig.get_rag_config(mode)
        
        # Override k with mode configuration
        faiss_top_k = rag_config["faiss_top_k"]
        final_chunks = rag_config["final_chunks"]
        logger.debug(f"RAG config: faiss_top_k={faiss_top_k}, final_chunks={final_chunks}")

        logger.debug(f"RAG config: faiss_top_k={faiss_top_k}, final_chunks={final_chunks}")

        # Stage 1: Query normalization (Flan-T5)
        # Purpose: Clarify user intent for better retrieval
        normalized_query = self.context_engineer.normalize_query(query)
        logger.debug(f"Normalized query: {normalized_query}")

        # Stage 2: Retrieve documents
        # Use hybrid search (FAISS + ChromaDB) with reranking
        # Mode controls initial retrieval breadth (faiss_top_k)
        retrieved_docs = self.retriever.retrieve_with_metadata(
            normalized_query, k=faiss_top_k
        )
        logger.debug(f"Retrieved {len(retrieved_docs)} documents (top-k={faiss_top_k})")
        
        # Limit to final_chunks based on mode
        if len(retrieved_docs) > final_chunks:
            retrieved_docs = retrieved_docs[:final_chunks]
            logger.debug(f"Limited to {final_chunks} chunks for {mode.value.upper()} mode")

        # Stage 3: Compress context (Flan-T5)
        # Purpose: Reduce noise while preserving essential information
        original_contents = [doc["content"] for doc in retrieved_docs]
        compressed_contents = self.context_engineer.compress_context_batch(
            original_contents
        )

        # Stage 4: Assemble structured context
        # Include source metadata and compressed content
        context_parts = []
        for i, (doc, compressed) in enumerate(zip(retrieved_docs, compressed_contents)):
            source = doc.get("source", "Unknown")
            context_parts.append(f"[Source {i+1}: {source}]\n{compressed}")

        context = "\n\n---\n\n".join(context_parts)

        # Stage 5: Generate response using ChatOllama
        # Only the LLM performs reasoning and synthesis
        if system_prompt is None:
            system_prompt = (
                "You are Teslas.ai, a scientific assistant. "
                "Use the provided context to answer questions accurately and rigorously. "
                "State assumptions clearly. Cite sources when relevant."
            )

        prompt = f"""{system_prompt}

Context:
{context}

Question: {query}

Answer:"""

        # Generate response
        try:
            ai = self.llm.invoke(prompt)
            response = getattr(ai, "content", str(ai))
        except Exception as e:
            logger.warning(f"LLM RAG chain invocation failed: {e}")
            response = "RAG response unavailable from LLM; return top-ranked context snippets."

        return {
            "query": query,
            "normalized_query": normalized_query,
            "response": response,
            "context": context,
            "sources": retrieved_docs,
            "mode": mode.value,
        }


def create_rag_chain() -> RAGChain:
    """Create RAG chain instance."""
    return RAGChain()
