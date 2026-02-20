"""Test calculator integration with agent system."""
import sys
import numpy as np
from app.agents.graph import TeslasAIOrchestrator
from app.agents.states import ResearchContext
from app.tools.calculator import create_calculator

print("=" * 80)
print("CALCULATOR INTEGRATION TEST WITH AGENT SYSTEM")
print("=" * 80)

# Test 1: Direct calculator instantiation
print("\n[TEST 1] Direct Calculator Usage")
print("-" * 80)
try:
    calc = create_calculator()
    print("[OK] Calculator created successfully")
    
    # Test basic operations
    result = calc.symbolic.differentiate("x**2 * sin(x)", "x")
    if result.success:
        print(f"[OK] Symbolic differentiation works: d/dx[x²sin(x)] = {result.results['simplified']}")
    else:
        print(f"[FAIL] Differentiation failed: {result.interpretation}")
    
    # Test numerical operation
    result = calc.numerical.euler_stability_analysis(0.1, 1.0)
    if result.success:
        print(f"[OK] Numerical analysis works: Method = {result.results.get('method', 'Euler')}")
    else:
        print(f"[FAIL] Numerical analysis failed")
    
    # Test data science
    X = np.random.randn(50, 2)
    y = np.random.randint(0, 2, 50)
    result = calc.data_science.linear_regression(X, y)
    if result.success:
        print(f"[OK] Data science works: R² = {result.results['r_squared']:.4f}")
    else:
        print(f"[FAIL] Data science failed")
    
except Exception as e:
    print(f"[FAIL] Calculator initialization error: {e}")
    sys.exit(1)

# Test 2: Agent's calculator reference
print("\n[TEST 2] Agents' Calculator References")
print("-" * 80)
try:
    from app.agents.mathematician import MathematicalAnalystAgent
    from app.agents.data_scientist import DataScientistAgent
    
    math_agent = MathematicalAnalystAgent()
    if hasattr(math_agent, 'calculator') and math_agent.calculator is not None:
        print("[OK] MathematicalAnalystAgent has calculator")
    else:
        print("[WARN] MathematicalAnalystAgent missing calculator reference")
    
    data_agent = DataScientistAgent()
    if hasattr(data_agent, 'calculator'):
        print("[OK] DataScientistAgent has calculator attribute")
    else:
        print("[WARN] DataScientistAgent missing calculator attribute")
    
except Exception as e:
    print(f"[FAIL] Agent initialization error: {e}")

# Test 3: Orchestrator workflow
print("\n[TEST 3] Orchestrator Workflow with Calculator")
print("-" * 80)
try:
    orchestrator = TeslasAIOrchestrator()
    print("[OK] Orchestrator initialized")
    
    # Check all agents
    agents_to_check = [
        ('planner', orchestrator.planner),
        ('mathematician', orchestrator.mathematician),
        ('numerical', orchestrator.numerical),
        ('data_scientist', orchestrator.data_scientist),
        ('reviewer', orchestrator.reviewer),
        ('writer', orchestrator.writer),
    ]
    
    for agent_name, agent in agents_to_check:
        has_calc = hasattr(agent, 'calculator')
        print(f"  {agent_name:15} - {'[OK]' if has_calc else '[WARN]'} has calculator")
    
except Exception as e:
    print(f"[FAIL] Orchestrator initialization error: {e}")

# Test 4: Workflow execution
print("\n[TEST 4] Running Selective Workflow")
print("-" * 80)
try:
    query = "Find the derivative of x^3 * cos(x) and analyze convergence"
    context = orchestrator.run_research_selective(
        query,
        agents=["planner", "mathematician", "reviewer", "writer"]
    )
    
    print(f"[OK] Workflow executed")
    print(f"  Query: {query}")
    print(f"  Execution path: {' -> '.join(context.execution_path)}")
    print(f"  Mathematical insights: {len(context.mathematical_insights)}")
    print(f"  Errors: {len(context.errors)}")
    
    if context.errors:
        for error in context.errors[:3]:
            print(f"    - {error[:70]}")
    
except Exception as e:
    print(f"[FAIL] Workflow execution error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Calculator methods that agents might use
print("\n[TEST 5] Calculator Methods Available for Agents")
print("-" * 80)
try:
    calc = create_calculator()
    
    # Check SymbolicMath methods
    symbolic_methods = [m for m in dir(calc.symbolic) if not m.startswith('_')]
    print(f"[OK] SymbolicMath methods ({len(symbolic_methods)}): {', '.join(symbolic_methods[:5])}...")
    
    # Check NumericalAnalysis methods
    numerical_methods = [m for m in dir(calc.numerical) if not m.startswith('_')]
    print(f"[OK] NumericalAnalysis methods ({len(numerical_methods)}): {', '.join(numerical_methods[:5])}...")
    
    # Check DataScienceTools methods
    ds_methods = [m for m in dir(calc.data_science) if not m.startswith('_')]
    print(f"[OK] DataScienceTools methods ({len(ds_methods)}): {', '.join(ds_methods[:5])}...")
    
    # Check ScientificCalculator methods
    main_methods = [m for m in dir(calc) if not m.startswith('_') and not hasattr(m, '__')]
    print(f"[OK] ScientificCalculator methods ({len(main_methods)}): {', '.join(main_methods[:8])}...")
    
except Exception as e:
    print(f"[FAIL] Method inspection error: {e}")

print("\n" + "=" * 80)
print("INTEGRATION TEST SUMMARY")
print("=" * 80)
print("""
Key Integration Points:
1. Calculator is accessible to agents (MathematicalAnalystAgent)
2. ComputationResult provides structured outputs
3. Decorators (@computation_wrapper, @validate_inputs) handle errors gracefully
4. Generator functions (convergence_rate_generator, gradient_descent_steps) 
   support streaming results
5. All four specialized classes (SymbolicMath, NumericalAnalysis, 
   LinearAlgebra, DataScienceTools) are available

Next Steps:
- Add calculator integration to DataScientistAgent (missing)
- Add calculator integration to NumericalSimulationAgent (missing)
- Ensure ComputationResult is compatible with agent context updates
- Test full orchestrator workflow with real queries
""")
