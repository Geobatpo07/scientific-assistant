"""Simple test to verify backward compatibility after langchain-chroma integration."""

from app.vectorstore.chroma import ChromaVectorStore


def test_basic_operations():
    """Test basic vector store operations."""
    print("Test 1: Creating vector store...")
    store = ChromaVectorStore(collection_name="test_compatibility")
    print("✅ Vector store created")
    
    print("\nTest 2: Adding texts...")
    texts = ["Machine learning is important", "Python is a programming language"]
    ids = store.add_texts(texts)
    assert len(ids) == 2
    print(f"✅ Added {len(ids)} texts")
    
    print("\nTest 3: Checking count...")
    count = store.count()
    assert count >= 2
    print(f"✅ Collection has {count} documents")
    
    print("\nTest 4: Searching...")
    results = store.search("machine learning", k=1)
    assert len(results) > 0
    assert "learning" in results[0]["content"].lower()
    print(f"✅ Found {len(results)} results")
    print(f"   Top result: {results[0]['content'][:50]}...")
    
    print("\nTest 5: Using as_retriever...")
    retriever = store.as_retriever(search_kwargs={"k": 2})
    docs = retriever.invoke("programming")
    assert len(docs) > 0
    print(f"✅ Retriever returned {len(docs)} documents")
    
    print("\nTest 6: Cleaning up...")
    store.delete_collection()
    print("✅ Collection deleted")
    
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("Testing backward compatibility after langchain-chroma integration")
    print("=" * 70)
    
    try:
        test_basic_operations()
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - Backward compatibility maintained!")
        print("=" * 70)
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 70)
        raise
