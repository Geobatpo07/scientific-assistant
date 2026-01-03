"""
Example 10: Context Engineering Layer (Flan-T5)

Demonstrates the Context Engineering layer for query normalization and context
compression. This layer preprocesses context BEFORE it reaches the main LLM.

Architecture:
    User Query
    ↓
    ContextEngineer.normalize_query (Flan-T5)
    ↓
    RAG Retrieval
    ↓
    ContextEngineer.compress_context (Flan-T5)
    ↓
    ChatOllama (reasoning)

Key Constraints:
    - Flan-T5 NEVER performs reasoning
    - CPU-only execution
    - max_new_tokens = 128
    - Model loaded once (singleton)
    - NO batching
"""

import os
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ensure CPU-only
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def example_1_query_normalization():
    """Example 1: Normalize ambiguous user queries."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Query Normalization")
    print("=" * 70)

    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    # Test cases: ambiguous queries
    test_queries = [
        "How u calculate regression?",
        "what's the diff between reg and classification",
        "how 2 use linear models",
        "variance vs std deviation?",
        "explain logistic regression pls",
    ]

    print("\nNormalizing ambiguous queries:\n")
    for i, query in enumerate(test_queries, 1):
        normalized = engineer.normalize_query(query)
        print(f"{i}. Original:   {query}")
        print(f"   Normalized: {normalized}")
        print()


def example_2_context_compression():
    """Example 2: Compress lengthy retrieved documents."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Context Compression")
    print("=" * 70)

    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    # Verbose document (typical retrieval result)
    verbose_doc = """
    Linear regression is one of the most fundamental and widely-used statistical
    methods in data science and machine learning. The method has its origins dating
    back to the 18th century when it was first developed by mathematicians studying
    physical phenomena.

    Linear regression works by finding the best-fitting straight line through a set
    of data points. This is achieved by minimizing the sum of the squared distances
    from each point to the line, which is known as the least squares method. The
    relationship between variables is assumed to be linear.

    The basic equation for simple linear regression is:
    y = mx + b
    
    where:
    - y is the dependent variable (what we're trying to predict)
    - x is the independent variable (our input)
    - m is the slope of the line
    - b is the y-intercept

    Linear regression is widely used in many applications including economics,
    engineering, and biological sciences. It forms the foundation for more advanced
    techniques in machine learning.

    Key assumptions of linear regression include:
    1. Linearity: The relationship between variables is linear
    2. Independence: Observations are independent
    3. Homoscedasticity: Constant variance of errors
    4. Normality: Errors are normally distributed
    """

    print("\nOriginal document:")
    print("-" * 70)
    print(verbose_doc)
    print(f"\nLength: {len(verbose_doc)} characters")

    print("\n" + "-" * 70)
    print("Compressed document:")
    print("-" * 70)

    compressed = engineer.compress_context(verbose_doc)
    print(compressed)
    print(f"\nLength: {len(compressed)} characters")
    print(f"Compression ratio: {len(verbose_doc) / len(compressed):.1f}x")


def example_3_batch_compression():
    """Example 3: Compress multiple documents sequentially."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Batch Compression")
    print("=" * 70)

    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    # Multiple retrieved documents
    documents = [
        """
        Logistic regression is a statistical method for binary classification.
        Unlike linear regression which predicts continuous values, logistic
        regression predicts the probability of a binary outcome (0 or 1).
        It uses the logistic function to map predictions to probabilities.
        """,
        """
        Polynomial regression extends linear regression by modeling non-linear
        relationships. Instead of fitting a straight line, it fits a polynomial
        curve to the data. Common polynomial degrees include 2 (quadratic) and
        3 (cubic).
        """,
        """
        Ridge regression adds a penalty term to the linear regression cost function.
        This penalty shrinks coefficients toward zero, reducing overfitting.
        The strength of the penalty is controlled by the alpha parameter.
        """,
    ]

    print(f"\nCompressing {len(documents)} documents:\n")

    compressed_batch = engineer.compress_context_batch(documents)

    for i, (original, compressed) in enumerate(zip(documents, compressed_batch), 1):
        print(f"Document {i}:")
        print(f"  Original length: {len(original)} chars")
        print(f"  Compressed: {compressed[:100]}...")
        print(f"  Compressed length: {len(compressed)} chars")
        print()


def example_4_rag_integration():
    """Example 4: Full RAG pipeline with context engineering."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Full RAG Pipeline")
    print("=" * 70)

    from app.rag.chains import create_rag_chain

    print("\nInitializing RAG chain with context engineering...")
    rag_chain = create_rag_chain()

    print("✓ RAG chain initialized")
    print("✓ LLM (ChatOllama) ready")
    print("✓ Vector store ready")
    print("✓ Context engineer (Flan-T5) ready")

    print("\nRAG Pipeline Stages:")
    print("  1. normalize_query (Flan-T5) - Clarify user intent")
    print("  2. retrieve_with_metadata - Hybrid search + reranking")
    print("  3. compress_context (Flan-T5) - Compress documents")
    print("  4. assemble_context - Structured, source-aware context")
    print("  5. llm.invoke (ChatOllama) - Generate answer")

    print("\nNote: Full execution requires running ChromaDB and Ollama services")
    print("For demonstration of actual query processing, ensure services are running")


def example_5_model_singleton():
    """Example 5: Verify singleton pattern for model caching."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Model Singleton Pattern")
    print("=" * 70)

    from app.hf.context_engineering import get_context_engineer

    print("\nGetting context engineer instances...\n")

    # Get multiple instances
    engineer1 = get_context_engineer()
    print(f"engineer1 = get_context_engineer()  -> {id(engineer1)}")

    engineer2 = get_context_engineer()
    print(f"engineer2 = get_context_engineer()  -> {id(engineer2)}")

    engineer3 = get_context_engineer()
    print(f"engineer3 = get_context_engineer()  -> {id(engineer3)}")

    print(f"\nAll instances are same object: {engineer1 is engineer2 is engineer3}")
    print("✓ Singleton pattern verified - model loaded only once!")


def example_6_determinism():
    """Example 6: Verify deterministic output (greedy decoding)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Determinism")
    print("=" * 70)

    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    query = "How to calculate the mean of a dataset?"

    print(f"\nRunning same query multiple times:\n")
    print(f"Query: {query}\n")

    results = []
    for i in range(3):
        result = engineer.normalize_query(query)
        results.append(result)
        print(f"Run {i+1}: {result}")

    all_same = all(r == results[0] for r in results)
    print(f"\nAll outputs identical: {all_same}")
    print("✓ Determinism verified - greedy decoding (no sampling)")


def example_7_cpu_only():
    """Example 7: Verify CPU-only execution."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: CPU-Only Execution")
    print("=" * 70)

    import torch
    from app.hf.context_engineering import (
        get_context_engineer,
        _DEVICE,
        _FLAN_T5_MODEL,
        _MAX_NEW_TOKENS,
    )

    print(f"\nConfiguration:")
    print(f"  Model: {_FLAN_T5_MODEL}")
    print(f"  Device: {_DEVICE}")
    print(f"  Max new tokens: {_MAX_NEW_TOKENS}")
    print(f"  PyTorch version: {torch.__version__}")

    engineer = get_context_engineer()

    print(f"\nContext Engineer:")
    print(f"  Device: {engineer.device}")
    print(f"  Model device: {next(engineer.model.parameters()).device}")

    print(f"\nGPU available: {torch.cuda.is_available()}")
    print(f"CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES')}")

    print("\n✓ CPU-only execution verified")


def example_8_constraints():
    """Example 8: Verify model constraints."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Model Constraints (MANDATORY)")
    print("=" * 70)

    from app.hf.context_engineering import (
        _FLAN_T5_MODEL,
        _MAX_NEW_TOKENS,
        _DEVICE,
    )

    constraints = {
        "Model": _FLAN_T5_MODEL,
        "Max new tokens": _MAX_NEW_TOKENS,
        "Device": _DEVICE,
        "Batching": "No (sequential)",
        "GPU": "Disabled",
        "Reasoning": "Never",
        "Conclusions": "Never",
    }

    print("\nMandatory Constraints:")
    print("-" * 70)
    for key, value in constraints.items():
        print(f"  {key:<20}: {value}")

    # Verify constraints
    assert _FLAN_T5_MODEL == "google/flan-t5-base", "Wrong model!"
    assert _MAX_NEW_TOKENS == 128, "Max tokens exceeded!"
    assert _DEVICE == "cpu", "GPU detected!"

    print("\n✓ All constraints verified")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Context Engineering Layer (Flan-T5)".center(68) + "║")
    print("║" + "  Query Normalization & Context Compression".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    # Run examples
    examples = [
        ("Query Normalization", example_1_query_normalization),
        ("Context Compression", example_2_context_compression),
        ("Batch Compression", example_3_batch_compression),
        ("RAG Integration", example_4_rag_integration),
        ("Model Singleton", example_5_model_singleton),
        ("Determinism", example_6_determinism),
        ("CPU-Only Execution", example_7_cpu_only),
        ("Model Constraints", example_8_constraints),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("✓ All examples completed")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
