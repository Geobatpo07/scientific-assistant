"""Example: Using langchain-chroma integration with ChromaDB.

This example demonstrates how to use the enhanced ChromaVectorStore
with langchain-chroma for better integration with LangChain ecosystem.
"""

from app.vectorstore.chroma import ChromaVectorStore
from app.llm.embeddings import get_embeddings
from langchain_core.documents import Document


def example_basic_usage():
    """Basic usage of ChromaVectorStore with langchain-chroma."""
    print("=" * 80)
    print("Example 1: Basic Text Storage and Retrieval")
    print("=" * 80)
    
    # Initialize vector store
    store = ChromaVectorStore(collection_name="test_langchain_chroma")
    
    # Add some texts
    texts = [
        "The Pythagorean theorem states that a² + b² = c²",
        "Linear regression is a statistical method for modeling relationships",
        "Neural networks are composed of layers of interconnected nodes",
        "The gradient descent algorithm minimizes a cost function",
    ]
    
    metadatas = [
        {"source": "geometry", "topic": "theorem"},
        {"source": "statistics", "topic": "regression"},
        {"source": "deep_learning", "topic": "architecture"},
        {"source": "optimization", "topic": "algorithm"},
    ]
    
    ids = store.add_texts(texts=texts, metadatas=metadatas)
    print(f"\n✓ Added {len(ids)} texts to vector store")
    print(f"✓ Collection size: {store.count()}")
    
    # Search for similar documents
    query = "What is a mathematical theorem?"
    results = store.search(query, k=2)
    
    print(f"\n🔍 Query: '{query}'")
    print(f"📊 Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Content: {result['content']}")
        print(f"  Metadata: {result['metadata']}")
        print(f"  Score: {result['score']:.4f}")
        print()
    
    # Clean up
    store.delete_collection()
    print("✓ Collection deleted")


def example_langchain_documents():
    """Using LangChain Document objects."""
    print("\n" + "=" * 80)
    print("Example 2: Using LangChain Documents")
    print("=" * 80)
    
    # Initialize vector store
    store = ChromaVectorStore(collection_name="test_documents")
    
    # Create LangChain documents
    documents = [
        Document(
            page_content="The derivative of x² is 2x",
            metadata={"subject": "calculus", "difficulty": "basic"}
        ),
        Document(
            page_content="Integration is the inverse operation of differentiation",
            metadata={"subject": "calculus", "difficulty": "intermediate"}
        ),
        Document(
            page_content="The fundamental theorem of calculus connects derivatives and integrals",
            metadata={"subject": "calculus", "difficulty": "advanced"}
        ),
    ]
    
    ids = store.add_documents(documents)
    print(f"\n✓ Added {len(ids)} documents to vector store")
    
    # Search
    query = "How are derivatives and integrals related?"
    results = store.search(query, k=2)
    
    print(f"\n🔍 Query: '{query}'")
    print(f"📊 Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Content: {result['content']}")
        print(f"  Subject: {result['metadata'].get('subject')}")
        print(f"  Difficulty: {result['metadata'].get('difficulty')}")
        print()
    
    # Clean up
    store.delete_collection()
    print("✓ Collection deleted")


def example_retriever_interface():
    """Using the LangChain retriever interface."""
    print("\n" + "=" * 80)
    print("Example 3: Using LangChain Retriever Interface")
    print("=" * 80)
    
    # Initialize vector store
    store = ChromaVectorStore(collection_name="test_retriever")
    
    # Add scientific texts
    texts = [
        "Machine learning models learn patterns from data",
        "Supervised learning uses labeled training data",
        "Unsupervised learning finds patterns without labels",
        "Reinforcement learning learns through trial and error",
        "Deep learning uses neural networks with multiple layers",
    ]
    
    store.add_texts(texts)
    print(f"✓ Added {len(texts)} texts")
    
    # Get a LangChain retriever
    retriever = store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    print("✓ Created LangChain retriever")
    
    # Use the retriever
    query = "How does machine learning work?"
    docs = retriever.invoke(query)
    
    print(f"\n🔍 Query: '{query}'")
    print(f"📊 Retrieved {len(docs)} documents:\n")
    
    for i, doc in enumerate(docs, 1):
        print(f"Document {i}: {doc.page_content}")
    
    # Clean up
    store.delete_collection()
    print("\n✓ Collection deleted")


def example_embeddings_interface():
    """Demonstrating the LangChain-compatible embeddings interface."""
    print("\n" + "=" * 80)
    print("Example 4: LangChain-Compatible Embeddings")
    print("=" * 80)
    
    embeddings = get_embeddings()
    
    # Test embed_query (for single queries)
    query = "What is machine learning?"
    query_embedding = embeddings.embed_query(query)
    print(f"✓ Query embedding dimension: {len(query_embedding)}")
    
    # Test embed_documents (for multiple documents)
    docs = [
        "Machine learning is a subset of AI",
        "Deep learning uses neural networks",
        "Natural language processing understands text",
    ]
    doc_embeddings = embeddings.embed_documents(docs)
    print(f"✓ Document embeddings: {len(doc_embeddings)} vectors of dimension {len(doc_embeddings[0])}")
    
    # Backward compatibility check
    old_style_embedding = embeddings.embed_text(query)
    print(f"✓ Backward compatibility: embed_text() works (dimension: {len(old_style_embedding)})")
    
    old_style_embeddings = embeddings.embed_texts(docs)
    print(f"✓ Backward compatibility: embed_texts() works ({len(old_style_embeddings)} vectors)")


if __name__ == "__main__":
    print("\n" + "🚀 " * 20)
    print("LangChain-Chroma Integration Examples")
    print("🚀 " * 20 + "\n")
    
    example_basic_usage()
    example_langchain_documents()
    example_retriever_interface()
    example_embeddings_interface()
    
    print("\n" + "✅ " * 20)
    print("All examples completed successfully!")
    print("✅ " * 20 + "\n")
