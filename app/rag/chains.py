"""RAG chains for question answering."""

from typing import Optional

from app.llm.ollama import get_llm
from app.vectorstore.chroma import get_vector_store
from app.vectorstore.retriever import Retriever
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGChain:
    """Retrieval-Augmented Generation chain."""
    
    def __init__(self):
        """Initialize RAG chain."""
        self.llm = get_llm()
        self.vector_store = get_vector_store()
        self.retriever = Retriever(self.vector_store)
    
    def retrieve_and_generate(
        self,
        query: str,
        k: int = 5,
        system_prompt: Optional[str] = None,
    ) -> dict:
        """Retrieve documents and generate response."""
        logger.info(f"RAG query: {query[:100]}...")
        
        # Retrieve
        retrieved_docs = self.retriever.retrieve_with_metadata(query, k=k)
        context = self.retriever.format_context(
            [doc["content"] for doc in retrieved_docs]
        )
        
        # Generate prompt
        if system_prompt is None:
            system_prompt = "You are a scientific assistant. Use the provided context to answer questions accurately and rigorously."
        
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
            "response": response,
            "context": context,
            "sources": retrieved_docs,
        }


def create_rag_chain() -> RAGChain:
    """Create RAG chain instance."""
    return RAGChain()
