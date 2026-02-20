"""Example: Using langchain-chroma in a RAG chain for scientific queries.

This example demonstrates how to use the enhanced ChromaVectorStore
with LangChain chains for scientific question answering.
"""

from app.vectorstore.chroma import ChromaVectorStore
from app.llm.embeddings import get_embeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def create_scientific_rag():
    """Create a RAG chain for scientific queries using langchain-chroma."""
    
    print("=" * 80)
    print("Scientific RAG Chain with LangChain-Chroma")
    print("=" * 80)
    
    # Initialize vector store
    store = ChromaVectorStore(collection_name="scientific_knowledge")
    
    # Add scientific documents
    scientific_docs = [
        Document(
            page_content="The Pythagorean theorem states that in a right triangle, "
                       "the square of the hypotenuse equals the sum of squares of the other two sides: a² + b² = c²",
            metadata={"subject": "mathematics", "topic": "geometry", "difficulty": "basic"}
        ),
        Document(
            page_content="Linear regression is a statistical method that models the relationship between "
                       "a dependent variable and one or more independent variables using a linear equation.",
            metadata={"subject": "statistics", "topic": "regression", "difficulty": "intermediate"}
        ),
        Document(
            page_content="A neural network is a computational model inspired by biological neural networks. "
                       "It consists of layers of interconnected nodes that process information through weighted connections.",
            metadata={"subject": "machine_learning", "topic": "deep_learning", "difficulty": "intermediate"}
        ),
        Document(
            page_content="Gradient descent is an optimization algorithm used to minimize a cost function. "
                       "It iteratively adjusts parameters in the direction of steepest descent of the gradient.",
            metadata={"subject": "optimization", "topic": "algorithms", "difficulty": "advanced"}
        ),
        Document(
            page_content="The Central Limit Theorem states that the distribution of sample means approaches "
                       "a normal distribution as the sample size increases, regardless of the population's distribution.",
            metadata={"subject": "statistics", "topic": "probability", "difficulty": "advanced"}
        ),
        Document(
            page_content="Principal Component Analysis (PCA) is a dimensionality reduction technique "
                       "that transforms data into a new coordinate system where the greatest variance lies on the first coordinate.",
            metadata={"subject": "data_science", "topic": "dimensionality_reduction", "difficulty": "advanced"}
        ),
    ]
    
    print(f"\n✓ Adding {len(scientific_docs)} scientific documents...")
    store.add_documents(scientific_docs)
    print(f"✓ Collection size: {store.count()}")
    
    # Get retriever
    retriever = store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    print("✓ RAG retriever created")
    
    return store, retriever


def format_docs(docs):
    """Format documents for the prompt."""
    return "\n\n".join(
        f"Document {i+1} ({doc.metadata.get('subject', 'unknown')} - {doc.metadata.get('topic', 'unknown')}):\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )


def demo_rag_queries(retriever):
    """Demonstrate RAG queries."""
    
    print("\n" + "=" * 80)
    print("Demo: Scientific Question Answering with Context")
    print("=" * 80)
    
    # Create a simple RAG prompt template
    template = """You are a scientific assistant. Answer the question based on the following context:

Context:
{context}

Question: {question}

Answer: Provide a clear, accurate answer based on the context provided. If the context doesn't contain 
enough information, say so and provide what information is available."""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Test queries
    queries = [
        "What is the Pythagorean theorem?",
        "How does gradient descent work?",
        "What is PCA used for?",
        "Explain the Central Limit Theorem",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'─' * 80}")
        print(f"Query {i}: {query}")
        print('─' * 80)
        
        # Retrieve relevant documents
        docs = retriever.invoke(query)
        
        print(f"\n📚 Retrieved {len(docs)} relevant documents:")
        for j, doc in enumerate(docs, 1):
            subject = doc.metadata.get('subject', 'unknown')
            topic = doc.metadata.get('topic', 'unknown')
            difficulty = doc.metadata.get('difficulty', 'unknown')
            print(f"\n  {j}. [{subject}] {topic} ({difficulty})")
            print(f"     {doc.page_content[:100]}...")
        
        # Format context
        context = format_docs(docs)
        
        # Create the prompt (in a real scenario, you'd send this to an LLM)
        filled_prompt = prompt.invoke({"context": context, "question": query})
        
        print(f"\n💬 Prompt created (would be sent to LLM):")
        print(f"   Context length: {len(context)} characters")
        print(f"   Question: {query}")


def demo_filtered_search(store):
    """Demonstrate filtered search by metadata."""
    
    print("\n" + "=" * 80)
    print("Demo: Filtered Search by Subject")
    print("=" * 80)
    
    # Direct search with the store
    query = "optimization techniques"
    print(f"\n🔍 Searching for: '{query}'")
    
    results = store.search(query, k=5)
    
    print(f"\n📊 Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        subject = result['metadata'].get('subject', 'unknown')
        topic = result['metadata'].get('topic', 'unknown')
        score = result.get('score', 0)
        print(f"\n{i}. [{subject}] {topic} (score: {score:.4f})")
        print(f"   {result['content'][:80]}...")


def demo_direct_chroma_access(store):
    """Demonstrate direct ChromaDB access for advanced queries."""
    
    print("\n" + "=" * 80)
    print("Demo: Direct ChromaDB Access")
    print("=" * 80)
    
    # Access the underlying Chroma collection
    collection = store.collection
    
    print(f"\n📊 Collection: {collection.name}")
    print(f"   Total documents: {collection.count()}")
    
    # Get all documents with specific metadata
    print("\n🔍 Finding all 'advanced' difficulty documents:")
    all_docs = collection.get(include=["documents", "metadatas"])
    
    advanced_docs = [
        (doc, meta)
        for doc, meta in zip(all_docs["documents"], all_docs["metadatas"])
        if meta.get("difficulty") == "advanced"
    ]
    
    print(f"   Found {len(advanced_docs)} advanced documents:")
    for doc, meta in advanced_docs:
        print(f"   - [{meta.get('subject')}] {doc[:60]}...")


def cleanup(store):
    """Clean up test data."""
    print("\n" + "=" * 80)
    print("Cleanup")
    print("=" * 80)
    store.delete_collection()
    print("✓ Collection deleted")


if __name__ == "__main__":
    print("\n" + "🔬 " * 20)
    print("Scientific RAG with LangChain-Chroma Integration")
    print("🔬 " * 20 + "\n")
    
    # Create RAG system
    store, retriever = create_scientific_rag()
    
    # Run demos
    demo_rag_queries(retriever)
    demo_filtered_search(store)
    demo_direct_chroma_access(store)
    
    # Cleanup
    cleanup(store)
    
    print("\n" + "✅ " * 20)
    print("All demos completed successfully!")
    print("✅ " * 20 + "\n")
