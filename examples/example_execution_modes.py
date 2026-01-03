"""Example demonstrating FAST and FULL execution modes in Teslas.ai.

This script shows how to use both execution modes and when to choose each one.

Usage:
    python examples/example_execution_modes.py
"""

from app.assistant import Assistant
from app.config import ExecutionMode
from app.utils.logger import get_logger
import time

logger = get_logger(__name__)


def example_fast_mode():
    """Demonstrate FAST mode for quick exploratory queries."""
    print("\n" + "="*80)
    print("🚀 FAST MODE EXAMPLE")
    print("="*80)
    print("\nUse Case: Quick calculation and exploration")
    print("Expected Runtime: 1-2 minutes\n")
    
    assistant = Assistant()
    
    # Simple queries perfect for FAST mode
    queries = [
        "What is the derivative of sin(x^2)?",
        "Explain the central limit theorem in one paragraph",
        "Calculate the first 3 terms of Taylor series for ln(1+x)",
    ]
    
    for query in queries:
        print(f"\n📝 Query: {query}")
        print("-" * 80)
        
        start_time = time.time()
        
        # Run in FAST mode
        result = assistant.research(query, mode=ExecutionMode.FAST)
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ Result:")
        print(f"   Summary: {result.final_summary[:200]}...")
        print(f"   Agents Used: {', '.join(result.execution_path)}")
        print(f"   Execution Mode: {result.metadata.get('execution_mode', 'unknown')}")
        print(f"   Agent Calls: {result.metadata.get('agent_calls', 0)}")
        print(f"   Time: {elapsed:.2f}s")
        
        if result.errors:
            print(f"   ⚠️  Errors: {result.errors}")


def example_full_mode():
    """Demonstrate FULL mode for deep research and rigorous analysis."""
    print("\n" + "="*80)
    print("🔬 FULL MODE EXAMPLE")
    print("="*80)
    print("\nUse Case: Deep research with maximum rigor")
    print("Expected Runtime: 5-15 minutes\n")
    
    assistant = Assistant()
    
    # Complex queries requiring deep analysis
    queries = [
        "Compare gradient descent and Adam optimizer for training neural networks",
        "Analyze the stability of the Runge-Kutta method for stiff ODEs",
    ]
    
    for query in queries:
        print(f"\n📝 Query: {query}")
        print("-" * 80)
        
        start_time = time.time()
        
        # Run in FULL mode
        result = assistant.research(query, mode=ExecutionMode.FULL)
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ Result:")
        print(f"   Summary: {result.final_summary[:300]}...")
        print(f"   Agents Used: {', '.join(result.execution_path)}")
        print(f"   Execution Mode: {result.metadata.get('execution_mode', 'unknown')}")
        print(f"   Agent Calls: {result.metadata.get('agent_calls', 0)}")
        print(f"\n   Mathematical Insights: {len(result.mathematical_insights)}")
        print(f"   Numerical Results: {len(result.numerical_results)}")
        print(f"   Literature Sources: {len(result.literature_sources)}")
        print(f"   Criticisms: {len(result.criticisms)}")
        print(f"   Improvements: {len(result.improvements)}")
        print(f"   Time: {elapsed:.2f}s ({elapsed/60:.1f}m)")
        
        if result.errors:
            print(f"   ⚠️  Errors: {result.errors}")


def example_mode_comparison():
    """Compare FAST and FULL modes on the same query."""
    print("\n" + "="*80)
    print("⚖️  MODE COMPARISON")
    print("="*80)
    print("\nComparing FAST vs FULL on the same query\n")
    
    assistant = Assistant()
    
    query = "Derive the Euler-Lagrange equations for classical mechanics"
    
    print(f"📝 Query: {query}")
    print("-" * 80)
    
    # Run in FAST mode
    print("\n🚀 Running in FAST mode...")
    start_fast = time.time()
    result_fast = assistant.research(query, mode=ExecutionMode.FAST)
    time_fast = time.time() - start_fast
    
    # Run in FULL mode
    print("\n🔬 Running in FULL mode...")
    start_full = time.time()
    result_full = assistant.research(query, mode=ExecutionMode.FULL)
    time_full = time.time() - start_full
    
    # Comparison table
    print("\n" + "="*80)
    print("COMPARISON RESULTS")
    print("="*80)
    
    print(f"\n{'Metric':<30} {'FAST':<20} {'FULL':<20}")
    print("-" * 70)
    print(f"{'Execution Time':<30} {f'{time_fast:.1f}s':<20} {f'{time_full:.1f}s':<20}")
    print(f"{'Agent Calls':<30} {result_fast.metadata.get('agent_calls', 0):<20} {result_full.metadata.get('agent_calls', 0):<20}")
    print(f"{'Agents Used':<30} {len(result_fast.execution_path):<20} {len(result_full.execution_path):<20}")
    print(f"{'Math Insights':<30} {len(result_fast.mathematical_insights):<20} {len(result_full.mathematical_insights):<20}")
    print(f"{'Numerical Results':<30} {len(result_fast.numerical_results):<20} {len(result_full.numerical_results):<20}")
    print(f"{'Literature Sources':<30} {len(result_fast.literature_sources):<20} {len(result_full.literature_sources):<20}")
    print(f"{'Criticisms':<30} {len(result_fast.criticisms):<20} {len(result_full.criticisms):<20}")
    print(f"{'Summary Length':<30} {len(result_fast.final_summary):<20} {len(result_full.final_summary):<20}")
    
    print(f"\n{'Speedup (FULL/FAST)':<30} {time_full/time_fast:.2f}x slower")
    print(f"{'Depth Increase':<30} {len(result_full.execution_path)/max(len(result_fast.execution_path), 1):.2f}x more agents")


def example_selective_agents_with_mode():
    """Demonstrate combining selective agents with execution modes."""
    print("\n" + "="*80)
    print("🎯 SELECTIVE AGENTS + MODE EXAMPLE")
    print("="*80)
    print("\nUse Case: Custom agent selection with mode parameters\n")
    
    assistant = Assistant()
    
    query = "Solve the quadratic equation x^2 - 5x + 6 = 0"
    
    # Use only specific agents but with FULL mode RAG parameters
    print(f"📝 Query: {query}")
    print("   Agents: ['mathematician', 'writer']")
    print("   Mode: FULL (for better RAG depth)")
    print("-" * 80)
    
    start_time = time.time()
    
    result = assistant.research(
        query,
        agents=["mathematician", "writer"],
        mode=ExecutionMode.FULL  # Use FULL mode RAG/LLM config
    )
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Result:")
    print(f"   Summary: {result.final_summary[:200]}...")
    print(f"   Agents: {', '.join(result.execution_path)}")
    print(f"   Mode: {result.metadata.get('execution_mode', 'unknown')}")
    print(f"   Time: {elapsed:.2f}s")


def example_decision_guide():
    """Print a decision guide for choosing execution modes."""
    print("\n" + "="*80)
    print("📋 EXECUTION MODE DECISION GUIDE")
    print("="*80)
    
    print("\n🚀 Choose FAST Mode When:")
    print("   ✓ You need a quick answer (< 5 minutes)")
    print("   ✓ Exploring new topics or concepts")
    print("   ✓ Question is straightforward")
    print("   ✓ Interactive development/prototyping")
    print("   ✓ Time is more critical than depth")
    
    print("\n🔬 Choose FULL Mode When:")
    print("   ✓ Research for publication or production")
    print("   ✓ High-stakes decisions requiring rigor")
    print("   ✓ Need comprehensive review and citations")
    print("   ✓ Complex multi-disciplinary queries")
    print("   ✓ Want memory persistence and traceability")
    print("   ✓ Maximum correctness is essential")
    
    print("\n⚙️  Mode Configurations:")
    print(f"\n   {'Parameter':<25} {'FAST':<20} {'FULL':<20}")
    print("   " + "-" * 65)
    print(f"   {'FAISS top-k':<25} {'15':<20} {'30':<20}")
    print(f"   {'Final chunks':<25} {'3':<20} {'5':<20}")
    print(f"   {'Temperature':<25} {'0.1':<20} {'0.3':<20}")
    print(f"   {'Max tokens':<25} {'2000':<20} {'4000':<20}")
    print(f"   {'Max iterations':<25} {'3':<20} {'10':<20}")
    print(f"   {'Max agent calls':<25} {'5':<20} {'20':<20}")
    print(f"   {'Reviewer agent':<25} {'Disabled':<20} {'Enabled':<20}")
    print(f"   {'Memory agent':<25} {'Disabled':<20} {'Enabled':<20}")
    print(f"   {'Web search':<25} {'Disabled':<20} {'Enabled':<20}")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("TESLAS.AI EXECUTION MODES - COMPREHENSIVE EXAMPLES")
    print("="*80)
    print("\nThis script demonstrates:")
    print("  1. FAST mode for quick queries")
    print("  2. FULL mode for deep research")
    print("  3. Side-by-side mode comparison")
    print("  4. Selective agents with modes")
    print("  5. Decision guide")
    
    # Show decision guide first
    example_decision_guide()
    
    # Run examples
    try:
        # Quick FAST mode example
        example_fast_mode()
        
        # Selective agents (faster than full FULL mode)
        example_selective_agents_with_mode()
        
        # Uncomment for full comparison (takes longer)
        # example_full_mode()
        # example_mode_comparison()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"Example failed: {e}")
        print(f"\n❌ Error: {e}")
    
    print("\n" + "="*80)
    print("✅ Examples completed!")
    print("="*80)
    print("\nFor more information, see: docs/EXECUTION_MODES.md\n")


if __name__ == "__main__":
    main()
